import pandas as pd
import unicodedata
import logging
from typing import Dict, Optional


def standardize_column_values(
    df: pd.DataFrame,
    column_name: str,
    value_map: Optional[Dict[str, str]] = None,
    label: str = "Column",
    clean_encoding: bool = True,
    clean_whitespace: bool = True,
    convert_dtype: Optional[str] = None,
    missing_values: Optional[set] = None,
) -> pd.DataFrame:
    """
    Standardize column values with comprehensive cleaning and mapping.

    Args:
        df: Input DataFrame
        column_name: Column to standardize
        value_map: Dictionary mapping original values to standardized values
        label: Label for logging
        clean_encoding: Whether to normalize Unicode characters
        clean_whitespace: Whether to clean whitespace
        convert_dtype: Target data type for conversion
        missing_values: Set of values to treat as missing

    Returns:
        DataFrame with standardized column

    Raises:
        ValueError: If column not found or invalid parameters
        TypeError: If invalid data types provided
    """
    try:
        # Validate input
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        if not isinstance(column_name, str):
            raise TypeError("Column name must be a string")

        # Default missing value patterns
        if missing_values is None:
            missing_values = {"", "nan", "none", "null", "na", "unknown", "-", "."}

        # Match column name ignoring case
        match_col = next(
            (
                col
                for col in df.columns
                if col.lower().strip() == column_name.lower().strip()
            ),
            None,
        )

        if not match_col:
            logging.error(f"Column '{column_name}' not found in DataFrame")
            return df

        # Step 1: Normalize + Clean Data
        # [for strings]
        # col_series = df[match_col].astype(str)
        # [for numericals and strings]
        col_series = df[match_col].apply(lambda x: str(x) if pd.notna(x) else pd.NA)

        if clean_encoding:
            col_series = col_series.apply(
                lambda x: unicodedata.normalize("NFKD", x) if isinstance(x, str) else x
            )

        if clean_whitespace:
            col_series = col_series.str.strip().str.replace(r"\s+", " ", regex=True)

        col_series = col_series.apply(
            lambda x: (
                x.lower()
                if isinstance(x, str) and not x.replace(".", "", 1).isdigit()
                else x
            )
        )

        # Step 2: Handle Missing-like values
        col_series = col_series.replace(missing_values, pd.NA)

        # Step 3: Optional Data Type Conversion
        if convert_dtype:
            try:
                col_series = col_series.astype(convert_dtype)
                logging.info(f"Converted column '{match_col}' to {convert_dtype}")
            except Exception as e:
                logging.warning(
                    f"Could not convert column '{match_col}' to {convert_dtype}: {e}"
                )

        # Step 4: Map Values if Mapping Provided
        if value_map:
            value_map = {k.lower(): v for k, v in value_map.items()}
            unique_vals = set(col_series.dropna().unique())
            if not unique_vals.isdisjoint(set(value_map.keys())):
                col_series = col_series.map(value_map).fillna(df[match_col])
                logging.info(f"{label} column '{match_col}' transformed successfully")
            else:
                logging.info(
                    f"{label} column '{match_col}' already looks transformed. Skipping"
                )
        else:
            logging.info(f"{label} column '{match_col}' cleaned without mapping")

        # Final Assignment
        df[match_col] = col_series
        return df

    except Exception as e:
        logging.error(f"Error standardizing column '{column_name}': {str(e)}")
        raise
