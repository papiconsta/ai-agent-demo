import json
import time
from dataclasses import dataclass, field
from datetime import datetime

import psycopg2

from llm.tools.tools import query_data_tool, search_tool
from pages.db import DB_CONFIG


# TODO: these are placeholder rates -- replace with the real current
# per-token pricing for each model from OpenAI's pricing page before
# trusting any cost numbers this produces.
MODEL_PRICING = {
    "gpt-5.6-sol": {"input": 0.0, "output": 0.0},
    "gpt-5.6-terra": {"input": 0.0, "output": 0.0},
    "gpt-5.6-luna": {"input": 0.0, "output": 0.0},
}


def calculate_cost(model, usage):
    rates = MODEL_PRICING.get(model)
    if rates is None:
        return 0.0
    return (usage.prompt_tokens * rates["input"] + usage.completion_tokens * rates["output"]) / 1_000_000

@dataclass
class LLMCallRecord:
    model: str
    prompt: str
    instructions: str
    answer: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time: float
    cost: float
    timestamp: datetime = field(default_factory=datetime.now)





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
        self.call_log = []

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

    def llm(self, prompt, conversation_id=None):
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": prompt},
        ]

        # Aegentic loop !
        while True:
            start_time = time.time()
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=[search_tool(), query_data_tool()],
                reasoning_effort="none",
            )
            response_time = time.time() - start_time
            message = response.choices[0].message

            self._log_response(prompt, response, response_time, conversation_id=conversation_id)
            if not message.tool_calls:
                return message.content

            messages.append(message)

            for tool_call in message.tool_calls:
                tool_start_time = time.time()
                arguments = json.loads(tool_call.function.arguments)
                print("TOOL CALLED:", tool_call.function.name, arguments)

                if tool_call.function.name == "search":
                    results = self.search(arguments["query"])
                elif tool_call.function.name == "query_data":
                    results = self.query_data(**arguments)
                else:
                    results = {"error": f"Unknown tool: {tool_call.function.name}"}
                tool_end_time = time.time()

                print("RESULTS:", results if isinstance(results, dict) else f"{len(results)} rows")
                print(f"TOOL EXECUTION TIME: {tool_end_time - tool_start_time:.2f} seconds")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(results),
                })

    def insertStatisticsToDBforAnalysis(self, record, conversation_id):
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO llm_call_records (
                        conversation_id, model, prompt, instructions, answer,
                        prompt_tokens, completion_tokens, total_tokens,
                        response_time, cost, timestamp_created
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        conversation_id,
                        record.model,
                        record.prompt,
                        record.instructions,
                        record.answer,
                        record.prompt_tokens,
                        record.completion_tokens,
                        record.total_tokens,
                        record.response_time,
                        record.cost,
                        record.timestamp,
                    )
                )
            connection.commit()

    def _log_response(self, prompt, response, response_time, conversation_id=None):
        usage = response.usage
        cost = calculate_cost(self.model, usage)

        call_record = LLMCallRecord(
            model=self.model,
            prompt=prompt,
            instructions=self.instructions,
            answer=response.choices[0].message.content,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            response_time=response_time,
            cost=cost,
        )
        print(call_record)
        self.call_log.append(call_record)
        if conversation_id is not None:
            self.insertStatisticsToDBforAnalysis(call_record, conversation_id)



    def rag(self, query, history=None, conversation_id=None):
        prompt = self.build_prompt(query, [], history=history)
        start_time = time.time()
        answer = self.llm(prompt, conversation_id=conversation_id)
        end_time = time.time()

        print(f"RAG RESPONSE TIME: {end_time - start_time:.2f} seconds")
        return answer

    