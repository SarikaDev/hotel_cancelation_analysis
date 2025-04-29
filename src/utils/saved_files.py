import os
from pathlib import Path
import pandas as pd
import logging
from typing import Optional, Any


def saved_files(
    df: pd.DataFrame,
    folder: str = "data",
    file_name: str = "Transformed_Data.xlsx",
    **save_kwargs: Any,
) -> Optional[str]:
    """
    Save DataFrame to either Excel (.xlsx) or CSV (.csv) format with validation and error handling.

    Args:
        df: DataFrame to save
        folder: Output directory (default: 'outputs')
        file_name: Output filename with extension (.xlsx or .csv)
        **save_kwargs: Additional arguments passed to to_excel() or to_csv()

    Returns:
        str: Full path to saved file if successful, None otherwise

    Raises:
        ValueError: If invalid file format or empty DataFrame
        TypeError: If invalid input types
        PermissionError: If file is locked
        FileNotFoundError: If path is invalid

    Examples:
        >>> saved_files(df, "results", "data.xlsx")
        >>> saved_files(df, "results", "data.csv", index=True)
    """
    try:
        # Validate input
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        if df.empty:
            raise ValueError("Cannot save empty DataFrame")

        if not isinstance(folder, str):
            raise TypeError("Folder path must be a string")

        if not isinstance(file_name, str):
            raise TypeError("File name must be a string")

        # Step 1: Ensure folder exists
        os.makedirs(folder, exist_ok=True)
        logging.info(f"Created/verified output directory: {folder}")

        # Step 2: Build full file path
        output_path = os.path.join(folder, file_name)
        file_ext = Path(file_name).suffix.lower()

        # Validate file extension
        if file_ext not in [".xlsx", ".csv"]:
            raise ValueError(f"Unsupported file format: {file_ext}. Use .xlsx or .csv")

        # Step 3: Save based on file extension
        if file_ext == ".xlsx":
            df.to_excel(
                output_path,
                index=False,
                engine="openpyxl",
                **{
                    k: v for k, v in save_kwargs.items() if k not in ["sep", "encoding"]
                },
            )
        else:  # .csv
            df.to_csv(
                output_path,
                index=False,
                **{k: v for k, v in save_kwargs.items() if k not in ["engine"]},
            )

        logging.info(f"Successfully saved {len(df)} rows to {output_path}")
        return output_path

    except PermissionError:
        logging.error(
            f"Permission denied! Please close the file if it's open: {output_path}"
        )
    except FileNotFoundError:
        logging.error(f"Invalid path: {output_path}")
    except ValueError as ve:
        logging.error(f"Value error: {ve}")
    except Exception as e:
        logging.error(f"Unexpected error while saving {file_name}: {str(e)}")

    return None
