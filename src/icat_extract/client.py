from icat_extract.config import resolve_secrets

from pathlib import Path

from icat import Client
import pandas as pd
import logging


logger = logging.getLogger(__name__)


def get_icat_client(icat_config: dict) -> Client:
    """
    Establishes a connection to the ICAT server using the provided configuration.
    Parameters:
    - icat_config: A dictionary containing the ICAT server configuration, including:
        - url: The URL of the ICAT server
        - auth: The authentication method (e.g., "basic" or "oauth")
        - credentials: A dictionary containing the necessary credentials for authentication
    Returns:
    - An authenticated Client instance connected to the ICAT server
    """

    try:
        client = Client(icat_config["url"])
        auth = icat_config.get("auth")
        client.login(auth, icat_config["credentials"])
        logger.info(
            f"Successfully connected to {icat_config['url']} - ICAT version {client.apiversion}"
        )
        return client
    except Exception as e:
        logger.error(f"Failed to connect to ICAT server: {e}")
        raise


def query_icat(query: str, icat_config: dict) -> pd.DataFrame:
    """
    Executes a query against the ICAT server and returns the results as a DataFrame.

    Parameters:
    - query: The ICAT query string to execute
    - icat_config: A dictionary containing the ICAT server configuration (see get_icat_client)

    Returns:
    - A pandas DataFrame containing the query results
    """
    try:
        client = get_icat_client(icat_config)
        results = client.search(query)
        logger.info(f"Query executed successfully: {query}")
        logger.info(f"Number of records retrieved: {len(results)}")
        return pd.DataFrame(results)
    except Exception as e:
        logger.error(f"Failed to execute query: {query} - Error: {e}")
        raise


def write_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Writes a DataFrame to a CSV file at the specified output path.
    If the output directory does not exist, it will be created.

    Parameters:
    - df: The pandas DataFrame to write to CSV
    - output_path: The file path where the CSV should be saved
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info("Wrote %d rows to %s", len(df), output_path)
    except Exception as e:
        logger.error(f"Failed to write data to {output_path}: {e}")
        raise
