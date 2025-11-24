import pandas as pd

class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is intended to be used in a PyTest-based testing framework to validate
    the quality of data in DataFrames. Each method performs a specific data quality
    check and uses assertions to ensure that the data meets the expected conditions.
    """
    @staticmethod
    def check_duplicates(df, column_names=None):
        if column_names:
            duplicates = df[df.duplicated(column_names)]
        else:
            duplicates = df[df.duplicated()]
        assert duplicates.shape[0] == 0, f"DataFrame contains {duplicates.shape[0]} duplicates!"

    @staticmethod
    def check_count(df1, df2):
        """Checking that the number of lines matches"""        
        assert df1.shape[0] == df2.shape[0], f"Row count mismatch: source={df1.shape[0]}, target={df2.shape[0]}"

    @staticmethod
    def check_data_full_data_set(df1, df2):
        assert df1.equals(df2), "Source and target DataFrames do not match."

    @staticmethod
    def check_dataset_is_not_empty(df):
        """Checking that the DataFrame is not empty"""
        assert not df.empty, f"DataFrame is empty."

    @staticmethod
    def check_not_null_values(df, column_names=None):
        """Checking for null values in columns (or in the entire DataFrame)"""
        if column_names:
            null_cols = df[column_names].isnull().any()
            assert not null_cols.any(), f"Null values found in columns: {list(null_cols[null_cols].index)}"
        else:
            assert not df.isnull().any().any(), "Null values found in DataFrame."
