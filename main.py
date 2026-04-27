# src/main.py
from icat.config import Config
from src.queries.investigations import (
    investigations_by_instrument,
    investigations_by_rb,
    investigations_by_user,
    investigations_by_start_date,
)
import pandas as pd


import logging
import json
import os
import sys
from datetime import datetime


logger = logging.getLogger(__name__)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=f"{os.getcwd()}/logs/{timestamp}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger.info("Initiating logger for data audit.")


try:
    config = Config()
    client, cfg = config.getconfig()
    client.login(cfg.auth, cfg.credentials)
    logger.info(
        f"Successfully connected to {cfg.url} - ICAT version {client.apiversion}"
    )
except Exception as e:
    logger.error(f"Failed to connect to ICAT server: {e}")
    raise


def query_icat(query: str) -> pd.DataFrame:
    """
    Queries the ICAT server and returns results as a pandas DataFrame.

    Parameters:
    query (str): The ICAT query to execute.

    Returns:
    pd.DataFrame: A DataFrame containing the query results.
    """
    try:
        results = client.search(query)
        logger.info(f"Query executed successfully: {query}")
        logger.info(f"Number of records retrieved: {len(results)}")
        return pd.DataFrame(results)
    except Exception as e:
        logger.error(f"Failed to execute query: {query} - Error: {e}")
        raise


def write_to_csv(df: pd.DataFrame, filename: str) -> None:
    """
    Writes a DataFrame to a CSV file.

    Parameters:
    df (pd.DataFrame): The DataFrame to write.
    filename (str): The name of the CSV file to create.
    """
    try:
        df.to_csv(f"{os.getcwd()}/results/{filename}", index=False)
        logger.info(f"Data successfully written to {filename}")
    except Exception as e:
        logger.error(f"Failed to write data to {filename}: {e}")
        raise


def main() -> int:
    try:
        facilities_df = query_icat("SELECT f FROM Facility f")
        write_to_csv(facilities_df, "facilities.csv")

        investigations_df = query_icat(investigations_by_instrument("HRPD"))
        write_to_csv(investigations_df, "investigations_by_instrument.csv")

        investigations_df = query_icat(investigations_by_rb("2220008"))
        write_to_csv(investigations_df, "investigations_by_rb.csv")

        investigations_df = query_icat(investigations_by_user("Dr Dominic Fortes"))
        write_to_csv(investigations_df, "investigations_by_user.csv")

        investigations_df = query_icat(
            investigations_by_start_date("2022-07-12 05:14:39+01:00")
        )
        write_to_csv(investigations_df, "investigations_by_start_date.csv")

        logger.info("All queries executed and results saved successfully.")
        return 0

    except Exception as e:
        logger.error(f"An error occurred during execution: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
