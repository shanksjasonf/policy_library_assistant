from pathlib import Path
from policy_loader import load_policies

data_path = Path(__file__).parent / "data" / "policies.json"

policies = load_policies(data_path)

print(f"Loaded {len(policies)} policies.")