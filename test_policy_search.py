from policy_search import search_policies, get_policy_by_id

def test_blank_search_returns_no_matches():
    sample_policies = [
        {
            "policy_id": "TEST-001",
            "title": "Example Policy",
            "content": "Synthetic example content.",
        }
    ]

    result = search_policies(sample_policies, "  ")

    assert result == [], "Blank searches should return an empty list."

def test_search_matches_content():
    sample_policies = [
        {
            "policy_id": "TEST-002",
            "title": "Remote Work Policy",
            "content": "Remote access requires multifactor authentication.",
        }
    ]

    result = search_policies(sample_policies, "authentication")

    assert len(result) == 1, "Expected one matching policy"
    assert result[0]["policy_id"] == "TEST-002", "Expected the remote work policy."

def test_search_normalizes_input():
    sample_policies = [
        {
            "policy_id": "TEST-003",
            "title": "Data Retention Policy",
            "content": "Keep training records for two years.",
        }
    ]

    result = search_policies(sample_policies, " RETENTION ")

    assert len(result) == 1, "Expected one matching policy"
    assert result[0]["policy_id"] == "TEST-003", "Expected data retention policy."


def test_get_policy_by_id_finds_second_record():
    sample_policies = [
        {"policy_id": "TEST-001", "title": "First", "content": "First policy."},
        {"policy_id": "TEST-002", "title": "Second", "content": "Second policy."},
    ]

    result = get_policy_by_id(sample_policies, "TEST-002")

    assert result == sample_policies[1]

def test_get_policy_by_id_returns_none_when_absent():
    sample_policies = [
        {"policy_id": "TEST-001", "title": "Example", "content": "Synthetic policy."},
    ]

    result = get_policy_by_id(sample_policies, "TEST-999")

    assert result is None