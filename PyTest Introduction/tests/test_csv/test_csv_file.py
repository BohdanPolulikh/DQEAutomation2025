import pytest

def test_file_not_empty(data):
    assert not data.empty, "File is empty!"

@pytest.mark.validate_csv
def test_schema(data, validate_schema):
    expected_columns = ['id', 'name', 'age', 'email', 'is_active']
    validate_schema(list(data.columns), expected_columns)

@pytest.mark.validate_csv
@pytest.mark.skip
def test_age_range(data):
    df_exceeds_age = data[(data['age'] <= 0) | (data['age'] > 100)]
    errors = [f"Player with id = {row.id} has invalid age {row.age}" 
              for row in df_exceeds_age.itertuples(index=False)]
    assert not errors, "\n".join(errors)

@pytest.mark.validate_csv
def test_email_format(data):
    df_incorrect_email = data[~data['email'].str.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}')]
    errors = [f'Player with id = {row.id} has invalid email "{row.email}"' 
              for row in df_incorrect_email.itertuples(index=False)]
    assert not errors, "\n".join(errors)

@pytest.mark.validate_csv
@pytest.mark.xfail
def test_full_duplicate(data):
    df_duplicate = data[data.duplicated()]
    error_id = df_duplicate['id'].to_list()
    assert not error_id, f"Full duplicate records with IDs = {error_id}"

@pytest.mark.parametrize("id, expected_status", [
    (1, False),
    (2, True)
])
def test_record_values(data, id, expected_status):
    real_status = data[data['id'] == id]['is_active'].iloc[0]
    assert real_status == expected_status, f"Player with id = {id} has is_active status = {real_status}, expected = {expected_status}"

def test_two_records(data):
    assert data[data['id'] == 1]['is_active'].iloc[0] == False, "Player with id = 1 is active"
    assert data[data['id'] == 2]['is_active'].iloc[0] == True, "Player with id = 2 has retired"
