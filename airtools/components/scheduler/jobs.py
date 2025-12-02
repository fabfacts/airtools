"""
Background job implementations for data collection.
"""

import logging
from datetime import datetime
from io import StringIO
from typing import Optional
import csv

from sqlmodel import Session, create_engine, select
from sqlalchemy.exc import IntegrityError

from airtools.utils.operations import download, SensorType
from airtools.models.core import Sensor, SensorData
from airtools.exceptions import DownloadError
from airtools.types import Url

logger = logging.getLogger(__name__)

# Database configuration - should match main.py
SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"


class FetchData:
    """Collection of background jobs for fetching sensor data."""

    @classmethod
    def collect_sensor_data(
        cls,
        sensor_uid: str,
        sensor_type: str,
        date: Optional[str] = None,
        base_url: str = "https://archive.sensor.community",
    ) -> None:
        """
        Download and store sensor data from sensor.community archive.

        This method runs as a scheduled background job. Downloads CSV data,
        parses individual records, and stores them in the database.
        Idempotent: duplicate records are skipped.

        Args:
            sensor_uid: Unique sensor identifier (e.g., "88359")
            sensor_type: Type of sensor ("dht22" or "sds011")
            date: Date string in YYYY-MM-DD format (defaults to today)
            base_url: Base URL for sensor.community archive
        """
        logger.info(
            "Starting data collection for sensor %s (type: %s, date: %s)",
            sensor_uid,
            sensor_type,
            date or "today",
        )

        # Default to today if not provided
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Map string sensor type to enum
        sensor_type_map = {
            "dht22": SensorType.DHT22,
            "sds011": SensorType.SDS011,
        }

        if sensor_type.lower() not in sensor_type_map:
            logger.error("Invalid sensor type: %s", sensor_type)
            return

        sensor_type_enum = sensor_type_map[sensor_type.lower()]

        try:
            # Download CSV data
            csv_text = download(
                unitid=int(sensor_uid),
                sensor_type=sensor_type_enum,
                date=date,
                url=Url(base_url),
            )
            logger.debug("Downloaded %d bytes of CSV data", len(csv_text))

            # Parse CSV into individual records
            csv_file = StringIO(csv_text)
            records = cls._parse_csv_to_records(csv_file, sensor_type_enum)
            logger.info("Parsed %d records from CSV", len(records))

            # Store records in database
            stored_count = cls._store_sensor_records(sensor_uid, records)
            logger.info(
                "Successfully stored %d new records for sensor %s",
                stored_count,
                sensor_uid,
            )

        except DownloadError as e:
            logger.error("Failed to download data: %s", str(e))
        except Exception as e:
            logger.error(
                "Unexpected error collecting data for sensor %s: %s",
                sensor_uid,
                str(e),
                exc_info=True,
            )

    @classmethod
    def _parse_csv_to_records(
        cls, csv_file: StringIO, sensor_type: SensorType
    ) -> list[dict]:
        """
        Parse CSV file into list of record dictionaries.

        Args:
            csv_file: StringIO object containing CSV data
            sensor_type: Type of sensor (determines separator and fields)

        Returns:
            List of dictionaries, one per CSV row
        """
        # Determine separator based on sensor type
        separator = ";" if sensor_type == SensorType.DHT22 else ","

        # Read CSV into list of dicts
        csv_file.seek(0)
        reader = csv.DictReader(csv_file, delimiter=separator)
        records = list(reader)

        return records

    @classmethod
    def _store_sensor_records(
        cls, sensor_uid: str, records: list[dict]
    ) -> int:
        """
        Store sensor data records in the database.

        Args:
            sensor_uid: Sensor unique identifier
            records: List of record dictionaries from CSV

        Returns:
            Number of records successfully stored

        Note:
            Skips records that already exist (composite unique constraint
            on sensor_id + timestamp). This makes the job idempotent.
        """
        # Create database session
        engine = create_engine(
            SQLITE_URL, connect_args={"check_same_thread": False}
        )

        stored_count = 0
        skipped_count = 0

        with Session(engine) as session:
            # Look up sensor by UID
            sensor = session.exec(
                select(Sensor).where(Sensor.uid == sensor_uid)
            ).first()

            if not sensor:
                logger.error(
                    "Sensor with uid '%s' not found in database", sensor_uid
                )
                return 0

            # Process each record
            for record in records:
                try:
                    # Parse timestamp
                    timestamp = datetime.strptime(
                        record["timestamp"], "%Y-%m-%dT%H:%M:%S"
                    )

                    # Create SensorData object
                    sensor_data = SensorData(
                        timestamp=timestamp,
                        temperature=float(record.get("temperature", 0.0)),
                        humidity=float(record.get("humidity", 0.0)),
                        sensor_id=sensor.id,
                    )

                    session.add(sensor_data)
                    session.commit()
                    stored_count += 1

                except IntegrityError:
                    # Record already exists (duplicate timestamp for this sensor)
                    session.rollback()
                    skipped_count += 1
                    logger.debug(
                        "Skipped duplicate record for timestamp %s",
                        record.get("timestamp"),
                    )

                except (ValueError, KeyError) as e:
                    # Invalid data in record
                    logger.warning(
                        "Skipped invalid record: %s (error: %s)",
                        record,
                        str(e),
                    )
                    session.rollback()

        logger.info(
            "Stored %d new records, skipped %d duplicates",
            stored_count,
            skipped_count,
        )
        return stored_count
