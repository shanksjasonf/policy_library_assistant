def search_policies(policy_records, search_term: str):
    """Return policies matching title or content; blank searches return an empty list."""

    normalized_search_term = search_term.strip().lower()

    if not normalized_search_term:
        return []
    
    matches = []

    for policy_record in policy_records:
        title_matches = normalized_search_term in policy_record["title"].lower()
        content_matches = normalized_search_term in policy_record["content"].lower()

        if title_matches or content_matches:
            matches.append(policy_record)

    return matches