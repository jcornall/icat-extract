from icat import Client
from icat.config import Config
import pandas as pd
import os
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


def get_icat_client() -> Client:
    cfg = Config()
    client = Client(cfg.url)
    client.login(cfg.auth, cfg.credentials)
    return client


def query_icat(query: str) -> pd.DataFrame:
    """
    Queries the ICAT server and returns results as a pandas DataFrame.

    Parameters:
    query (str): The ICAT query to execute.

    Returns:
    pd.DataFrame: A DataFrame containing the query results.
    """
    try:
        client = get_icat_client()
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
