import pytest
import pandas as pd

def pytest_addoption(parser):
    parser.addoption(
        '--path-to-file',
        action='store',
        default='player_data.csv',
        help="Path to CSV file"
    )

# Fixture to read the CSV file
@pytest.fixture(scope="session")
def data(request):
    path = request.config.getoption("--path-to-file")
    try:
        df = pd.read_csv(path)
    except Exception as e:
        pytest.skip(f"Skipping tests because CSV file {path} cannot be read: {e}")
    return df

# Fixture to validate the schema of the file
@pytest.fixture(scope='session')
def validate_schema():
    def validate(actual_schema, expected_schema):
        errors = []
        # Missing columns
        missing = [col for col in expected_schema if col not in actual_schema]
        if missing:
            errors.append(f"Missing columns: {missing}")
        # Extra columns
        extra = [col for col in actual_schema if col not in expected_schema]
        if extra:
            errors.append(f"Extra columns: {extra}")
        # Column order
        for i, col in enumerate(expected_schema):
            if i < len(actual_schema) and actual_schema[i] != col:
                errors.append(f"Column order mismatch at position {i}: expected {col}, got {actual_schema[i]}")
        assert not errors, "\n".join(errors)
    return validate



# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(items, config):
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker("unmarked")
