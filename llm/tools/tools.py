

def search_tool():
    return {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Fuzzy keyword search over warehouse inventory items (matches against item name, measurements, and type). Good for 'find items like X' questions. For counts, totals, distinct categories, or ranking (most expensive, etc.), use query_data instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    }


def query_data_tool():
    return {
        "type": "function",
        "function": {
            "name": "query_data",
            "description": (
                "Query the full warehouse inventory dataset. Use this for questions that plain "
                "search can't answer: exact counts/totals ('how many X'), listing distinct "
                "categories ('what types exist'), ranking ('most expensive', 'highest quantity'), or "
                "numeric ranges ('between 20 and 500', 'over 100 units'). Combine text_query and/or "
                "filter_field+filter_value for exact-match narrowing, range_field+min_value/max_value "
                "for numeric ranges, then use sort_by/descending for ranking, distinct_field to list "
                "unique values, or count_only for an exact total instead of a capped list of rows."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text_query": {
                        "type": "string",
                        "description": "Free-text keyword to fuzzy-match against item name, type, and measurements (case-insensitive substring match)."
                    },
                    "filter_field": {
                        "type": "string",
                        "enum": ["type", "location", "unit_of_measure"],
                        "description": "Field to filter on with an exact match (case-insensitive)."
                    },
                    "filter_value": {
                        "type": "string",
                        "description": "Value to match filter_field against, e.g. 'Vamzdis' for filter_field='type'."
                    },
                    "range_field": {
                        "type": "string",
                        "enum": ["price", "quantity", "weight_kg", "critical_quantity"],
                        "description": "Numeric field to apply min_value/max_value range filtering to, e.g. 'price' for a price range question."
                    },
                    "min_value": {
                        "type": "number",
                        "description": "Minimum value (inclusive) for range_field. Use for 'over X' or 'between X and Y' questions."
                    },
                    "max_value": {
                        "type": "number",
                        "description": "Maximum value (inclusive) for range_field. Use for 'under X' or 'between X and Y' questions."
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["price", "quantity", "weight_kg", "critical_quantity"],
                        "description": "Numeric field to sort results by."
                    },
                    "descending": {
                        "type": "boolean",
                        "description": "Sort highest-to-lowest if true (e.g. 'most expensive'), lowest-to-highest if false."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max number of rows to return. Leave unset to return ALL matching rows, unbounded. Only set this when the user explicitly asks for a specific number, e.g. 'top 5' or 'least 10' (pair with sort_by/descending). Ignored if distinct_field or count_only is set."
                    },
                    "distinct_field": {
                        "type": "string",
                        "enum": ["type", "location", "unit_of_measure", "material"],
                        "description": "If set, return the distinct/unique values of this field (after filtering) instead of individual item rows."
                    },
                    "count_only": {
                        "type": "boolean",
                        "description": "If true, return the total count of matching items instead of the item rows themselves."
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        }
    }
