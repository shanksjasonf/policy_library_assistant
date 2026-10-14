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

def test_load_policies_rejects_non_array():
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text("{}", encoding="utf-8")

        try:
            load_policies(data_path)
        except ValueError as error:
            assert str(error) == "Policy data must be a JSON array.", f"Unexpected error: {error}"
        else:
            raise AssertionError("Expected ValueError for a JSON object.")

def test_load_policies_rejects_non_object_record():
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text("[42]", encoding="utf-8")

        try:
            load_policies(data_path)
        except ValueError as error:
            assert str(error) == "Each policy must be a JSON object.", f"Unexpected error: {error}"
        else:
            raise AssertionError("Expected ValueError for a non-object policy record.")

def test_load_policies_rejects_missing_title():
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text('[{"policy_id": "TEST-004", "content": "Synthetic content."}]', encoding="utf-8")

        try:
            load_policies(data_path)
        except ValueError as error:
            assert str(error) == "Each policy must include a title.", f"Unexpected error: {error}"
        else:
            raise AssertionError("Expected ValueError for non-title policy record.")

def test_load_policies_rejects_numeric_title():
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text('[{"policy_id": "TEST-005", "title": 42, "content": "Synthetic content."}]', encoding="utf-8")

        try:
            load_policies(data_path)
        except ValueError as error:
            assert str(error) == "Policy title must be a string.", f"Unexpected error: {error}"
        else:
            raise AssertionError("Expected ValueError for policy title datatype mismatch.")

def test_load_policies_rejects_missing_content():
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text('[{"policy_id": "TEST-006", "title": "Example policy"}]', encoding="utf-8")

        try:
            load_policies(data_path)
        except ValueError as error:
            assert str(error) == "Each policy must include content.", f"Unexpected error: {error}"
        else:
            raise AssertionError("Expected ValueError for missing content.")

def test_load_policies_rejects_non_string_content():
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text('[{"policy_id": "TEST-007", "title": "Example policy", "content": 42}]', encoding="utf-8")

        try:
            load_policies(data_path)
        except ValueError as error:
            assert str(error) == "Policy content must be a string.", f"Unexpected error: {error}"
        else:
            raise AssertionError("Expected ValueError for non-string content.")

def test_load_policies_rejects_missing_policy_id():
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text('[{"title": "Example policy", "content": "Synthetic content."}]', encoding='utf-8')

        try:
            load_policies(data_path)
        except ValueError as error:
            assert str(error) == "Each policy must include a policy_id.", f"Unexpected error: {error}"
        else:
            raise AssertionError("Expected ValueError for missing policy_id.")

def test_load_policies_rejects_non_string_policy_id():
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text('[{"policy_id": 42, "title": "Example policy", "content": "Synthetic content."}]', encoding="utf-8")

        try:
            load_policies(data_path)
        except ValueError as error:
            assert str(error) == "Policy ID must be a string.", f"Unexpected error: {error}"
        else:
            raise AssertionError("Expected ValueError for non-string policy_id.")


if __name__ == "__main__":
    test_load_policies_reads_json()
    test_load_policies_rejects_non_array()
    test_load_policies_rejects_non_object_record()
    test_load_policies_rejects_missing_title()
    test_load_policies_rejects_numeric_title()
    test_load_policies_rejects_missing_content()
    test_load_policies_rejects_non_string_content()
    test_load_policies_rejects_missing_policy_id()
    test_load_policies_rejects_non_string_policy_id()
    print("All policy loader tests passed.")
    