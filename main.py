from pathlib import Path

from policy_loader import load_policies
from policy_search import search_policies

def get_policy_summary(policy_record):
    return f"{policy_record['policy_id']}: {policy_record['title']}"

def main():
    data_path = Path(__file__).parent / "data" / "policies.json"

    try:
        policies = load_policies(data_path)
    except FileNotFoundError:
        print(f"Policy file not found: {data_path}")
        return
    except ValueError as error:
        print(f"Invalid policy data: {error}")
        return
    
    search_term = input("Enter a policy search term: ")
    matching_policies = search_policies(policies, search_term)

    if not matching_policies:
        print("No matching policies found.")
    else:
        for policy_record in matching_policies:
            print(get_policy_summary(policy_record))

if __name__ == "__main__":
    main()