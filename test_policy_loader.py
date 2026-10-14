from pathlib import Path
from tempfile import TemporaryDirectory

from policy_loader import load_policies


def assert_invalid_policy_data(json_text: str, expected_message: str):
    with TemporaryDirectory() as temporary_folder:
        data_path = Path(temporary_folder) / "policies.json"
        data_path.write_text(json_text, encoding="utf-8")

        try:
            load_policies(data_path)
        except ValueError as error:
            assert str(error) == expected_message, f"Unexpected error: {error}"
        else:
            raise AssertionError("Expected ValueError, but loading succeeded.")


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
    assert_invalid_policy_data(
        "{}",
        "Policy data must be a JSON array.",
    )


def test_load_policies_rejects_non_object_record():
    assert_invalid_policy_data(
        "[42]",
        "Each policy must be a JSON object.",
    )


def test_load_policies_rejects_missing_title():
    assert_invalid_policy_data(
        '[{"policy_id": "TEST-004", "content": "Synthetic content."}]',
        "Each policy must include a title.",
    )


def test_load_policies_rejects_numeric_title():
    assert_invalid_policy_data(
        '[{"policy_id": "TEST-005", "title": 42, "content": "Synthetic content."}]',
        "Policy title must be a string.",
    )


def test_load_policies_rejects_missing_content():
    assert_invalid_policy_data(
        '[{"policy_id": "TEST-006", "title": "Example policy"}]',
        "Each policy must include content.",
    )


def test_load_policies_rejects_non_string_content():
    assert_invalid_policy_data(
        '[{"policy_id": "TEST-007", "title": "Example policy", "content": 42}]',
        "Policy content must be a string.",
    )


def test_load_policies_rejects_missing_policy_id():
    assert_invalid_policy_data(
        '[{"title": "Example policy", "content": "Synthetic content."}]',
        "Each policy must include a policy_id.",
    )


def test_load_policies_rejects_non_string_policy_id():
    assert_invalid_policy_data(
        '[{"policy_id": 42, "title": "Example policy", "content": "Synthetic content."}]',
        "Policy ID must be a string.",
    )


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
    