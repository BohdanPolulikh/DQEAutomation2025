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
            df.duplicated(column_names)
        else:
            df.duplicated(df.columns)

    @staticmethod
    def check_count(df1, df2):
        """Checking that the number of lines matches"""        
        if df1.count != df2.count:
            raise AssertionError(f"""Row count mismatch: source={len(df1)}, target={len(df2)}""")

    @staticmethod
    def check_data_full_data_set(df1, df2):
        if not df1.equals(df2):
            raise AssertionError("Source and target DataFrames do not match.")

    @staticmethod
    def check_dataset_is_not_empty(df):
        """Checking that the DataFrame is not empty"""
        if df.empty:
            raise AssertionError("DataFrame is empty.")

    @staticmethod
    def check_not_null_values(df, column_names=None):
        """Checking for null values in columns (or in the entire df)"""
        if column_names:
            null_cols = df[column_names].isnull().any()
            if null_cols.any():
                raise AssertionError(f"Null values found in columns: {list(null_cols[null_cols].index)}")
        else:
            if df.isnull().any().any():
                raise AssertionError("Null values found in DataFrame.")
