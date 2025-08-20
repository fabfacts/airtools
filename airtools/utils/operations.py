import logging
from io import TextIOBase
from typing import Dict, List, Any
from enum import Enum

import pandas as pd
import requests

from airtools.exceptions import DownloadError
from airtools.types import Url

logger = logging.getLogger(__name__)


class SensorType(Enum):
    """
    Enumerate sensor types used by the project.
    """

    SDS011 = 0
    DHT22 = 1


def download(unitid: int, sensor_type: SensorType, date: str, url: Url) -> str:
    """
    Download one sensor file from an archive URL.

    Args:
        unitid: Sensor numeric id.
        sensor_type: SensorType enum value.
        date: Date string used in the filename (e.g. "2025-01-20").
        url: Base Url to download from.

    Returns:
        The response body as text.

    Raises:
        DownloadError: If the HTTP request failed.
    """
    abs_url: Url = Url(f"{url}/{date}_{sensor_type}_{unitid}.csv")

    res: requests.Response = requests.get(abs_url, timeout=60)

    if res.status_code != 200:
        logger.error(
            "Download failed for %s (status %s)", abs_url, res.status_code
        )
        raise DownloadError(f"Failed to download {abs_url}: {res.status_code}")

    return res.text


def parse_data(data: TextIOBase, sensor_type: SensorType) -> Dict[str, Any]:
    """
    Parse a CSV file-like object and compute summary statistics.

    The function extracts common fields and sensor-specific fields, then computes
    average, min and max for sensor measurement fields.

    Args:
        data: A text file-like object (opened CSV).
        sensor_type: Type of sensor (controls which sensor columns are expected).

    Returns:
        A dictionary containing default fields plus computed statistics.
    """
    # default columns present in every sensor CSV
    default_fields: List[str] = [
        "sensor_id",
        "sensor_type",
        "location",
        "lat",
        "lon",
        "timestamp",
    ]

    field_names: List[str] = default_fields.copy()
    sensor_field_names: List[str] = []

    # result dictionary (mutable)
    average_out: Dict[str, Any] = {k: None for k in default_fields}
    csv_separator: str = ","

    logger.info("Parsing sensor data for type %s", sensor_type)
    if sensor_type == SensorType.DHT22:
        sensor_field_names = ["temperature", "humidity"]
        field_names += sensor_field_names
        csv_separator = ";"
    elif sensor_type == SensorType.SDS011:
        sensor_field_names = ["P1", "P2"]
        field_names += sensor_field_names

    # read csv into a DataFrame
    reader: pd.DataFrame = pd.read_csv(
        data, usecols=field_names, sep=csv_separator
    )
    logger.debug("Imported csv, columns %s", list(reader.columns))

    # get default values from first row (if present)
    default_row: List[Dict[str, Any]] = (
        reader.head(1)[default_fields].to_dict(orient="records")
        if not reader.empty
        else []
    )

    # calculate average, max, min per sensor field
    for field in sensor_field_names:
        # ensure we reset per-field accumulators
        sensor_field_avg: float = 0.0
        sensor_field_count: int = 0
        sensor_field_max: float | None = None
        sensor_field_min: float | None = None

        for _, row in reader.iterrows():
            # row is a pandas Series
            value = row[field]
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                # skip non-numeric entries
                continue

            sensor_field_avg += numeric
            sensor_field_count += 1

            if sensor_field_max is None or numeric > sensor_field_max:
                sensor_field_max = numeric
            if sensor_field_min is None or numeric < sensor_field_min:
                sensor_field_min = numeric

        if sensor_field_count > 0:
            average_out[field] = round(
                sensor_field_avg / sensor_field_count, 1
            )
            average_out[f"{field}_max"] = sensor_field_max
            average_out[f"{field}_min"] = sensor_field_min
        else:
            average_out[field] = None
            average_out[f"{field}_max"] = None
            average_out[f"{field}_min"] = None

    # merge default row values (if available)
    if default_row:
        average_out.update(default_row[0])

    return average_out
