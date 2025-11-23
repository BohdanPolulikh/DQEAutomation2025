import pandas as pd
import os

class ParquetReader:
    """
    Class for working with Parquet files.
    Implements basic file reading methods.
    """

    def read_file(self, file_path: str) -> pd.DataFrame:
        """
        Reads a single Parquet file and returns a pandas DataFrame
        """
        return pd.read_parquet(file_path)
    
    def process(self, root_path: str, include_subfolders: bool = True) -> pd.DataFrame:
        """
        Reads all parquet files in the specified folder (recursively, if include_subfolders=True)
        and returns a merged DataFrame.
        Args:
            root_path (str): Path to the folder containing parquet files.
            include_subfolders (bool): If True, recursively traverses all subfolders.
        Returns:
            pd.DataFrame: A combined data frame from all parquet files.
        """
        all_dfs = []

        if include_subfolders:
            for dirpath, _, filenames in os.walk(root_path):
                for file in filenames:
                    if file.endswith(".parquet"):
                        file_path = os.path.join(dirpath, file)
                        df = pd.read_parquet(file_path)
                        all_dfs.append(df)
        else:
            for file in os.listdir(root_path):
                if file.endswith(".parquet"):
                    file_path = os.path.join(root_path, file)
                    df = pd.read_parquet(file_path)
                    all_dfs.append(df)

        if not all_dfs:
            raise ValueError(f"No parquet files found in {root_path}")

        # Combine all dataframes into one
        combined_df = pd.concat(all_dfs, ignore_index=True)
        return combined_df
