from policy_search import search_policies

policies = [
    {
        "policy_id": "POL-001",
        "title": "Data Retention Policy",
        "content": "Retain training records for two years.",
    },
    {
        "policy_id": "POL-002",
        "title": "Remote Work Policy",
        "content": "Remote access requires multifactor authentication.",
    }
]

def get_policy_summary(policy_record):
    return f"{policy_record['policy_id']}: {policy_record['title']}"

def main():
    matching_policies = search_policies(policies, ' RETENTION ')

    if not matching_policies:
        print("No matching policies found.")
    else:
        for policy_record in matching_policies:
            print(get_policy_summary(policy_record))

if __name__ == "__main__":
    main()