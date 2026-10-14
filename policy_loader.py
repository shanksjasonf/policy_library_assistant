import json
from pathlib import Path

def load_policies(data_path: Path) -> list:
    """Load policy records from a UTF-8 JSON file."""
    with data_path.open("r", encoding="utf-8") as policy_file:
        policies = json.load(policy_file)

    if not isinstance(policies, list):
        raise ValueError("Policy data must be a JSON array.")

    for policy_record in policies:
        if not isinstance(policy_record, dict):
            raise ValueError("Each policy must be a JSON object.")

        if "title" not in policy_record:
            raise ValueError("Each policy must include a title.")

        if not isinstance(policy_record["title"], str):
            raise ValueError("Policy title must be a string.")

        if "content" not in policy_record:
            raise ValueError("Each policy must include content.")

        if not isinstance(policy_record["content"], str):
            raise ValueError("Policy content must be a string.")

        if "policy_id" not in policy_record:
            raise ValueError("Each policy must include a policy_id.")

        if not isinstance(policy_record["policy_id"], str):
            raise ValueError("Policy ID must be a string.")

    return policies