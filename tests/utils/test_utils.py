import os

from airtools.utils.operations import parse_data, SensorType


def test_parse_data_sds011(test_files_path):

    with open(
        os.path.join(
            test_files_path, "csv", "2025-02-07_sds011_sensor_88358.csv"
        ),
        encoding="utf-8",
    ) as datacsv:
        result = parse_data(datacsv, SensorType.SDS011)

        # I except one line with an average of the day data
        assert "sensor_type" in result
        assert "P1" in result
        assert "P2" in result


def test_parse_data_dht22(test_files_path):

    with open(
        os.path.join(
            test_files_path, "csv", "2025-02-07_dht22_sensor_88359.csv"
        ),
        encoding="utf-8",
    ) as datacsv:
        result = parse_data(datacsv, SensorType.DHT22)

        # I except one line with an average of the day data
        assert "sensor_type" in result
        assert "temperature" in result
        assert "humidity" in result
