"""
Generates a labeled evaluation set: for each real record in data.json, ask an
LLM to invent plausible user questions that record would answer. The result
is a list of {"id": <record id>, "question": <generated question>} pairs you
can later run through retrieval to check whether the right record comes back.
"""

GENERATE_QUESTIONS_PROMPT = '''
TODO: write a prompt that:
- shows the LLM one record's relevant fields (name, type, measurements, material, ...)
- asks it to generate N different questions a warehouse employee might ask
  that this specific record would answer
- tells it to return the questions in a format you can parse reliably
  (e.g. one per line, or ask for JSON)
'''.strip()


def generate_questions_for_record(record, llm_client, model, num_questions=3):
    """
    Ask the LLM to generate `num_questions` plausible user questions for a
    single data.json record.

    Args:
        record (dict): one item from data.json (has 'id', 'name', 'type', ...).
        llm_client: an OpenAI client instance.
        model (str): model name to use for generation.
        num_questions (int): how many questions to generate per record.

    Returns:
        list[str]: the generated questions.

    TODO:
    - format GENERATE_QUESTIONS_PROMPT with this record's fields
    - call llm_client.chat.completions.create(...) with that prompt
    - parse the response into a list of separate question strings
    """
    raise NotImplementedError


def build_ground_truth(documents, llm_client, model, num_questions=3, sample_size=None):
    """
    Build the full evaluation set by generating questions for many records.

    Args:
        documents (list[dict]): the full data.json records (from load_data()).
        llm_client: an OpenAI client instance.
        model (str): model name to use for generation.
        num_questions (int): questions to generate per record.
        sample_size (int | None): if set, only generate for this many random
            records instead of all 357 — worth using while developing, since
            357 records x N questions is a lot of LLM calls (time + cost).

    Returns:
        list[dict]: [{"id": record_id, "question": "..."}, ...]

    TODO:
    - optionally subsample `documents` down to `sample_size`
    - loop over documents, call generate_questions_for_record() for each
    - flatten into one list of {"id": ..., "question": ...} dicts
    - consider saving the result to a JSON file (e.g. data/ground_truth.json)
      so you don't have to regenerate it (and burn LLM calls) every run
    """
    raise NotImplementedError
