"""
Description: DQ tests for test_facility_type_avg_time_spent_per_visit_date Parquet dataset
Requirement(s): TICKET-1234
Author(s): Bohdan
"""

import pytest

@pytest.fixture(scope='module')
def source_data(db_connection):
    source_query = """
    SELECT
        f.facility_type,
        v.visit_timestamp::date AS visit_date,
        ROUND(AVG(v.duration_minutes), 2) AS avg_time_spent
    FROM visits v
    JOIN facilities f
        ON f.id = v.facility_id
    GROUP BY f.facility_type, visit_date
    """
    data = db_connection.get_data_sql(source_query)
    df = data.sort_values(["facility_type", "visit_date"]).reset_index(drop=True)
    return df



@pytest.fixture(scope='module')
def target_data(parquet_reader):
    target_path = "/var/jenkins_home/workspace/parquet_data/facility_type_avg_time_spent_per_visit_date"
    data = parquet_reader.process(target_path, include_subfolders=True)
    df = data.sort_values(["facility_type", "visit_date"]).reset_index(drop=True)    
    return df


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)

@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)

@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_data_full_data_set(source_data, target_data, data_quality_library):
    data_quality_library.check_data_full_data_set(source_data, target_data)

@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_duplicates(target_data, data_quality_library):
    data_quality_library.check_duplicates(target_data)

@pytest.mark.parquet_data
@pytest.mark.facility_type_avg_time_spent_per_visit_date
def test_check_not_null_values(target_data, data_quality_library):
    data_quality_library.check_not_null_values(target_data, ['facility_type', 'visit_date', 'avg_time_spent'])
