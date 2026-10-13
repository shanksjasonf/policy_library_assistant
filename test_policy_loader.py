from pathlib import Path
from tempfile import TemporaryDirectory

from policy_loader import load_policies

def test_load_policies_reads_json():
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text(
            '[{"policy_id": "TEST-001", "title": "Example", "content": "Synthetic content"}]',
            encoding="utf-8",
        )

        result = load_policies(data_path)

        assert len(result) == 1, "Exactly one loaded policy."
        assert result[0]["policy_id"] == "TEST-001", "Expected the test policy."

if __name__ == "__main__":
    test_load_policies_reads_json()
    print("Policy loader test passed.")