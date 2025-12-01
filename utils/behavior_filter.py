def filter_behaviors(behaviors, allowed_categories=None):
    """
    behaviors: list of dicts like:
      {
         "category": "medical_harm",
         "behavior": "...text..."
      }

    allowed_categories: list[str]
    """

    # If categories not provided – return all behaviors
    if not allowed_categories:
        return behaviors

    allowed = set(allowed_categories)

    filtered = [
        b for b in behaviors
        if b.get("category") in allowed
    ]
    return filtered
