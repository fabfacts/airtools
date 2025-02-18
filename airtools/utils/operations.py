import logging
from io import TextIOBase
from typing import Tuple, Mapping, Any
from enum import Enum
import pandas as pd
import requests

from airtools.exceptions import DownloadError
from airtools.types import Url

logger = logging.getLogger(__name__)


class SensorType(Enum):
    """
    Enumerate sensors
    """

    SDS011 = (0,)
    DHT22 = 1


def download(unitid: int, sensor_type: SensorType, date: str, url: Url) -> str:
    """
    Download one sensor file from the archive located in url. File name format is

    `2025-01-20_bme280_sensor_113.csv`

    Args:
        unitid (int): _description_
        sensor_type (str): _description_

    Returns:
        bool: _description_
    """
    abs_url: Url = f"{url}/{date}_{sensor_type}_{unitid}.csv"

    res = requests.get(
        abs_url,
    )

    if res.status_code != 200:
        logger.error("Download failed for %s", abs_url)
        raise DownloadError

    return res.data


def parse_data(
    data: TextIOBase, sensor_type: SensorType
) -> Tuple[str, str, str]:
    """
    Parse a csv file, squize data and calculate the average, min and max

    Common to all sensors fields are: sensor_id,sensor_type,location,lat,lon,timestamp

    Our sensors types are `SDS011` for air particles set fields:

    P1,P2

    and `DHT22` for temp/humidity that sets fields:

    temperature,humidity

    Args:
        data (TextIOBase): Text file Object

    Returns:
        Tuple[str,str,str]: _description_
    """
    default_fields: list = [
        "sensor_id",
        "sensor_type",
        "location",
        "lat",
        "lon",
        "timestamp",
    ]
    field_names = default_fields.copy()
    sensor_field_names: list[str] = []
    average_out: Mapping[str, Any] = dict.fromkeys(default_fields)
    csv_separator: str = ","

    logger.info("Sensor %s", sensor_type)
    if sensor_type == SensorType.DHT22:
        sensor_field_names = ["temperature", "humidity"]
        field_names += sensor_field_names
        csv_separator = ";"
    elif sensor_type == SensorType.SDS011:
        sensor_field_names = ["P1", "P2"]
        field_names += sensor_field_names

    # read fieldnames
    reader = pd.read_csv(data, usecols=field_names, sep=csv_separator)
    logger.debug("imported csv, columns %s", reader.columns)

    sensor_field_avg: float = 0.0
    sensor_field_avg_count: int = 0
    sensor_field_max: float = 0.0
    sensor_field_min: float = 0.0

    # get default values from first row
    default_row = reader.head(1)[default_fields].to_dict(orient="records")

    # calculate average, max, min
    for field in sensor_field_names:
        for _, row in reader.iterrows():
            sensor_field_avg += row[field]
            sensor_field_max = (
                sensor_field_max
                if row[field] < sensor_field_max
                else row[field]
            )
            sensor_field_min = (
                sensor_field_min
                if row[field] > sensor_field_min
                else row[field]
            )
            sensor_field_avg_count += 1

        average_out[field] = round(
            sensor_field_avg / sensor_field_avg_count, 1
        )
        average_out[f"{field}_max"] = sensor_field_max
        average_out[f"{field}_min"] = sensor_field_min

    # merge into final dictionary
    average_out.update(default_row[0])

    return average_out
