def search(query, index, num_results=5, filter_dict=None):
    """
    Search for documents in the index.

    Args:
        query (str): The search query.
        index: The minsearch Index to search against.
        num_results (int): The number of results to return.
        filter_dict (dict, optional): A dictionary of filters to apply.

    Returns:
        list: A list of search results.
    """
    boost_dict = {'name': 3.0}

    return index.search(
        query,
        num_results=num_results,
        boost_dict=boost_dict,
        filter_dict=filter_dict or {},
    )