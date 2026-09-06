import json
from llm.tools.tools import query_data_tool, search_tool

SYSTEM_PROMPT = '''
You are a helpful assistant that answers questions about warehouse inventory
using only the information provided in the CONTEXT section below.

Use the CONTEXT to find relevant items and give an accurate answer. If the
answer is not found in the CONTEXT, respond with "I don't know."
'''

PROMPT_TEMPLATE = '''
QUESTION: {question}

CONTEXT:
{context}

PREVIOUS ANSWERS:
{previous_answers}

'''.strip()


class RAGClient:

    def __init__(self, index, llm_client, model, instructions=SYSTEM_PROMPT, prompt_template=PROMPT_TEMPLATE):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model

    def search(self, query, num_results=5, filter_dict=None):
        """
        Search for documents in the index.

        Args:
            query (str): The search query.
            num_results (int): The number of results to return.
            filter_dict (dict, optional): A dictionary of filters to apply.

        Returns:
            list: A list of search results.
        """
        boost_dict = {'name': 3.0}

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict,
            filter_dict=filter_dict or {},
        )

    def query_data(self, text_query=None, filter_field=None, filter_value=None,
                    range_field=None, min_value=None, max_value=None,
                    sort_by=None, descending=False, limit=None,
                    distinct_field=None, count_only=False):
        """
        Query the full dataset with filtering, sorting, distinct-values, and counting.
        Unlike search(), this looks at ALL documents, not just the top-N text matches.
        """
        documents = self.index.docs

        results = documents
        if text_query:
            q = text_query.lower()
            results = [
                doc for doc in results
                if q in f"{doc.get('name') or ''} {doc.get('type') or ''} {doc.get('measurements') or ''}".lower()
            ]

        if filter_field and filter_value:
            fv = str(filter_value).lower()
            results = [doc for doc in results if str(doc.get(filter_field) or '').lower() == fv]

        if range_field and (min_value is not None or max_value is not None):
            results = [
                doc for doc in results
                if doc.get(range_field) is not None
                and (min_value is None or doc[range_field] >= min_value)
                and (max_value is None or doc[range_field] <= max_value)
            ]

        if distinct_field:
            values = sorted({
                doc.get(distinct_field) for doc in results
                if doc.get(distinct_field) is not None
            })
            return {"distinct_values": values}

        if count_only:
            return {"count": len(results)}

        if sort_by:
            results = [doc for doc in results if doc.get(sort_by) is not None]
            results = sorted(results, key=lambda doc: doc[sort_by], reverse=descending)

        return results if limit is None else results[:limit]

    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append(f"Name: {doc.get('name')}")
            lines.append(f"Type: {doc.get('type')}")
            lines.append(f"Material: {doc.get('material')}")
            lines.append(f"Location: {doc.get('location')}")
            lines.append(f"Quantity: {doc.get('quantity')} {doc.get('unit_of_measure')}")
            lines.append(f"Price: {doc.get('price')}")
            lines.append('')

        return '\n'.join(lines).strip()

    def build_prompt(self, query, search_results, history=None):
        context = self.build_context(search_results)
        if history is None:
            history = []
        conversation_history = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in history
        )
        return self.prompt_template.format(question=query, context=context, previous_answers=conversation_history)

    def llm(self, prompt):
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": prompt},
        ]

        # Aegentic loop !
        while True:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=[search_tool(), query_data_tool()],
                reasoning_effort="none",
            )
            message = response.choices[0].message

            if not message.tool_calls:
                return message.content

            messages.append(message)

            for tool_call in message.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                print("TOOL CALLED:", tool_call.function.name, arguments)

                if tool_call.function.name == "search":
                    results = self.search(arguments["query"])
                elif tool_call.function.name == "query_data":
                    results = self.query_data(**arguments)
                else:
                    results = {"error": f"Unknown tool: {tool_call.function.name}"}

                print("RESULTS:", results if isinstance(results, dict) else f"{len(results)} rows")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(results),
                })

    def rag(self, query, history=None):
        prompt = self.build_prompt(query, [], history=history)
        answer = self.llm(prompt)
        return answer
