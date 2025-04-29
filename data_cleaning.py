import logging
import pandas as pd
from src.utils.paths import Config
from src.transforms.reusable_mapping import standardize_column_values
from src.utils.saved_files import saved_files
import os
import sys
import json
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

config = Config()
file_path = config.raw_file_path


def read(file_path: str) -> pd.DataFrame:

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.lower().endswith((".csv")):
            raise ValueError("File must be CSV format (.csv )")

        df = pd.read_csv(file_path, engine="python", encoding="unicode_escape")

        logging.info(f"Successfully loaded data from {file_path}")
        return df

    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        raise


def fetch_data(file_path: str) -> pd.DataFrame:

    df = read(file_path)

    # Basic data validation
    if df.empty:
        logging.warning("Loaded DataFrame is empty")
    else:
        logging.info(f"Loaded DataFrame shape: {df.shape}")

    return df


# Task 01 [Fetch data]
df = fetch_data(file_path)
print("shape", df.shape)

# Task 02 [Change Col_case]


def col_mutation(col_name: str) -> str:

    try:
        # Convert to string and strip whitespace
        col = str(col_name).strip()

        # Replace spaces and special characters
        col = col.lower()
        col = col.replace(" ", "_")
        col = "".join(c if c.isalnum() or c == "_" else "_" for c in col)

        # Remove consecutive underscores
        col = "_".join(filter(None, col.split("_")))

        # Ensure valid Python identifier
        if not col.isidentifier():
            col = "col_" + col

        logging.debug(f"Standardized column name: {col_name} -> {col}")
        return col

    except Exception as e:
        logging.error(f"Error standardizing column name '{col_name}': {str(e)}")
        return str(col_name)  # Return original if error occurs


df = df.rename(col_mutation, axis=1)

#  Task 03 [remove_unwanted_col or select only desired col's]
columns_to_keep = [
    "hotel",
    "is_canceled",
    "arrival_date_year",
    "arrival_date_month",
    "adults",
    "children",
    "babies",
    "country",
    "reserved_room_type",
    "assigned_room_type",
    "reservation_status",
    "reservation_status_date",
]
df = df[columns_to_keep]
# Task 03-01 [Find actual duplicate rows]
# complete_duplicates = df[df.duplicated(keep=False)]
# print(complete_duplicates.shape, complete_duplicates.head(10))


# task 04 [attributes]
def get_isNull_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    total_rows = len(df)

    report = []

    for col in df.columns:
        null_count = df[col].isnull().sum()

        report.append(
            {
                "Column": col,
                "Nulls": null_count,
                "Nulls %": round((null_count / total_rows) * 100, 2),
            }
        )

    quality_df = pd.DataFrame(report)

    # quality_df = quality_df[(quality_df["Nulls"] > 0)]

    # quality_df = quality_df.sort_values(by="Nulls", ascending=False)

    return quality_df


null_report = get_isNull_quality_report(df)

# now replace null  with business logic

df.fillna({"country": "Unknown", "children": 0}, inplace=True)

# Task 05 :
# standardize_column_values

# hey = df["country"].unique()
with open("src/utils/country_codes.json", "r") as file:
    country_code_map = json.load(file)


df = standardize_column_values(
    df,
    column_name="country",
    value_map=country_code_map,
    label="Country",
    clean_encoding=True,
    clean_whitespace=True,
    convert_dtype=None,
)
df["children"] = df["children"].astype(int)

df = standardize_column_values(
    df,
    column_name="is_canceled",
    value_map={"0": "no", "1": "yes"},
    label="is_canceled",
    clean_encoding=True,
    clean_whitespace=True,
    convert_dtype=None,
)


def add_room_status_col(
    df: pd.DataFrame, reserved_col: str, assigned_col: str
) -> pd.DataFrame:
    try:
        if reserved_col not in df.columns or assigned_col not in df.columns:
            raise ValueError("One or both columns not found in DataFrame")

        # Define a custom rank where A is highest, Z is lowest
        def room_rank(room_type):
            return 90 - ord(room_type.upper())  # A=25, B=24, ..., Z=1

        reserved_rank = df[reserved_col].apply(room_rank)
        assigned_rank = df[assigned_col].apply(room_rank)

        df["room_status"] = np.where(
            reserved_rank == assigned_rank,
            "Same",
            np.where(reserved_rank > assigned_rank, "Desired", "Un-Desired"),
        )

        return df

    except Exception as e:
        logging.error(f"Error creating room_status: {str(e)}")
        return df


df = add_room_status_col(
    df, reserved_col="reserved_room_type", assigned_col="assigned_room_type"
)


def add_guest_type(df: pd.DataFrame) -> pd.DataFrame:
    try:
        # Define guest_type using np.select
        conditions = [
            # Couples: Strictly 2 adults, zero children/babies
            (df["adults"] == 2) & (df["children"] + df["babies"] == 0),
            # Single: 1 adult, zero children/babies
            (df["adults"] == 1) & (df["children"] == 0) & (df["babies"] == 0),
            # Family: Any adults with kids, EXCLUDING 2 adults + 0 kids (couples)
            ((df["children"] > 0) | (df["babies"] > 0)) & ~(df["adults"] == 2),
            # Group: 3+ adults without children (optional)
            (df["adults"] >= 3) & (df["children"] + df["babies"] == 0),
        ]

        choices = ["Couple", "Single", "Family", "Group"]

        df["guest_type"] = np.select(conditions, choices, default="Others")
        return df

    except KeyError as e:
        print(f"Missing required column: {e}")
        return df
    except Exception as e:
        print(f"Unexpected error: {e}")
        return df


df = add_guest_type(df)


dupes = df[df.duplicated(keep="first")]
saved_files(dupes, folder="data/outputs", file_name="Duplicate_Data.csv")


# Gold Mine Dupes Proof
# dupe_groups = df[df.duplicated(keep=False)].groupby(list(df.columns))
# for _, group in list(dupe_groups)[:3]:  # Inspect first 3 duplicate groups
#     print(group.head(2), "\n---")

# # drop those extra dupes
cleaned = df[~df.duplicated(keep="first")]

saved_files(cleaned, folder="data/processed", file_name="Cleaned_Data.csv")


print(len(df), "original")
print(len(dupes), "extra dupes,excluding 1st occurence")
print(len(cleaned), "cleaned", f"{len(df)} - {len(dupes)}")
