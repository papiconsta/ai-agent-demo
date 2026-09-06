"""
Answer evaluation via LLM-as-a-judge: score the RAG system's final generated
answer, since there's no simple exact-match metric for free-text answers.
This is independent of retrieval evaluation (metrics.py) — an answer can be
wrong even with perfect retrieval (the model ignores good context), or right
despite bad retrieval (rare, but possible with tool-calling).
"""

JUDGE_PROMPT = '''
TODO: write a prompt that gives the judge LLM:
- the original question
- the answer the RAG system produced
- (optionally) the retrieved context/records it was based on
and asks it to score the answer, e.g. on relevance/faithfulness/correctness,
in a format you can parse reliably (e.g. a JSON object with a score + reason).
'''.strip()


def judge_answer(question, answer, context, llm_client, model):
    """
    Score one (question, answer) pair using a second LLM call as judge.

    Args:
        question (str): the original user question.
        answer (str): the RAG system's final generated answer.
        context (str): the retrieved context the answer was supposed to be
            grounded in (e.g. from build_context()).
        llm_client: an OpenAI client instance.
        model (str): model to use as the judge (can be the same or different
            from the model being evaluated).

    Returns:
        dict: whatever scoring shape you decide on, e.g.
            {"relevant": bool, "faithful": bool, "reasoning": str}

    TODO:
    - format JUDGE_PROMPT with question/answer/context
    - call llm_client.chat.completions.create(...)
    - parse the response into a structured score
    """
    raise NotImplementedError
