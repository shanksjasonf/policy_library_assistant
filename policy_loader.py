import json
from pathlib import Path

def load_policies(data_path: Path) -> list:
    """Load policy records from a UTF-8 JSON file."""
    with data_path.open("r", encoding="utf-8") as policy_file:
        return json.load(policy_file)