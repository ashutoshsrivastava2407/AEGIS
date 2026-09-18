from services.data_platform.connectors.base import BaseConnector
from services.data_platform.connectors.csv_connector import csv_connector, CSVConnector
from services.data_platform.connectors.json_connector import json_connector, JSONConnector
from services.data_platform.connectors.postgres_connector import postgres_connector, PostgreSQLConnector
from services.data_platform.connectors.rest_connector import rest_connector, RESTConnector


def get_connector(source_type: str) -> BaseConnector:
    st = source_type.upper()
    if st == "CSV":
        return csv_connector
    elif st == "JSON":
        return json_connector
    elif st == "POSTGRESQL":
        return postgres_connector
    elif st == "REST_API":
        return rest_connector
    else:
        raise ValueError(f"Unsupported connector source type: '{source_type}'")


__all__ = [
    "BaseConnector",
    "CSVConnector",
    "JSONConnector",
    "PostgreSQLConnector",
    "RESTConnector",
    "csv_connector",
    "json_connector",
    "postgres_connector",
    "rest_connector",
    "get_connector",
]
