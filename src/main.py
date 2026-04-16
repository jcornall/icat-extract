from icat.config import Config
import logging
import json
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=f"../logs/{timestamp}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger.info("Initiating logger for data audit.")

try:
    config = Config()
    client, cfg = config.getconfig()
    client.login(cfg.auth, cfg.credentials)
    logger.info("Successfully connected to ICAT server.")
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
        return results
    except Exception as e:
        logger.error(f"Failed to execute query: {query} - Error: {e}")
        raise


if __name__ == "__main__":
    # Example query to fetch all facilities
    facilities_df = query_icat("SELECT f FROM Facility f")
    print(facilities_df)

    # # Example query to fetch investigations related to a specific RB number
    rb_number = "2220008"
    investigations_df = query_icat(f"SELECT i FROM Investigation i WHERE i.name = {rb_number} INCLUDE i.datasets.datafiles")
    print(investigations_df)