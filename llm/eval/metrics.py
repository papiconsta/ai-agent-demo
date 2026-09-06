"""
Retrieval evaluation: given the ground truth (question -> expected record id)
from ground_truth.py, check whether your actual retrieval function finds the
right record, and how highly it ranks it.
"""


def hit_rate(eval_results):
    """
    Fraction of questions where the expected record appeared ANYWHERE in the
    retrieved results (regardless of rank).

    Args:
        eval_results (list[bool]): one entry per question — True if the
            expected id was found somewhere in that question's results.

    Returns:
        float: hit rate between 0 and 1.

    TODO: sum(eval_results) / len(eval_results), handling the empty-list case.
    """
    raise NotImplementedError


def mean_reciprocal_rank(ranks):
    """
    Rewards finding the right record NEAR THE TOP, not just somewhere in the
    results. For each question, the "rank" is 1/position if found (e.g. found
    at position 1 -> 1.0, position 3 -> 0.333), or 0 if not found at all.

    Args:
        ranks (list[float]): one reciprocal-rank value per question.

    Returns:
        float: MRR, average of `ranks`.

    TODO: sum(ranks) / len(ranks), handling the empty-list case.
    """
    raise NotImplementedError


def evaluate_retrieval(ground_truth, retrieve_fn):
    """
    Run every (id, question) pair from ground_truth through retrieve_fn, and
    compute hit_rate + MRR across the whole set.

    Args:
        ground_truth (list[dict]): [{"id": ..., "question": ...}, ...] from
            build_ground_truth().
        retrieve_fn (callable): a function taking a question string and
            returning a list of result dicts (e.g. RAGClient.search, or a
            wrapper around query_data) — each result dict should have an
            'id' field to compare against ground_truth's expected id.

    Returns:
        dict: {"hit_rate": float, "mrr": float}

    TODO for each (expected_id, question) pair:
    - results = retrieve_fn(question)
    - find the position (1-indexed) of the result whose 'id' == expected_id,
      or None if it's not in results at all
    - build up the `found` (bool) list for hit_rate() and the reciprocal-rank
      list for mean_reciprocal_rank() (1/position if found, else 0)
    - return both aggregated metrics
    """
    raise NotImplementedError
