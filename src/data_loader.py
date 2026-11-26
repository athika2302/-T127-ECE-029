
import csv
from pathlib import Path
from datetime import datetime


def load_csv(file_path, required_columns):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"CSV is empty: {path}")

        missing = [
            col for col in required_columns
            if col not in reader.fieldnames
        ]

        if missing:
            raise ValueError(
                f"{path.name} is missing columns: {missing}"
            )

        rows = []

        for line_number, row in enumerate(reader, start=2):
            cleaned = {
                key: (value.strip() if value else "")
                for key, value in row.items()
            }

            for column in required_columns:
                if not cleaned.get(column):
                    raise ValueError(
                        f"{path.name}, row {line_number}: "
                        f"{column} cannot be empty"
                    )

            rows.append(cleaned)

        return rows


def validate_unique(rows, key, file_name):
    seen = set()

    for row in rows:
        value = row[key]

        if value in seen:
            raise ValueError(
                f"Duplicate {key} '{value}' in {file_name}"
            )

        seen.add(value)


def validate_positive(rows, columns, file_name, allow_zero=False):
    for index, row in enumerate(rows, start=2):
        for column in columns:
            try:
                value = float(row[column])
            except ValueError:
                raise ValueError(
                    f"{file_name}, row {index}: "
                    f"{column} must be numeric"
                )

            if value < 0 or (value == 0 and not allow_zero):
                raise ValueError(
                    f"{file_name}, row {index}: "
                    f"{column} has an invalid value"
                )


def validate_date(value, fmt, field):
    try:
        return datetime.strptime(value, fmt)
    except ValueError:
        raise ValueError(f"Invalid date in {field}: {value}")


def load_sites(file_path):
    columns = [
        "site_id", "site_name", "city",
        "dg_rating_kva", "tank_capacity_l",
        "diesel_rate_rs_per_l", "opening_fuel_l",
        "hour_meter_reading", "last_service_hour_meter",
        "last_service_date"
    ]

    rows = load_csv(file_path, columns)

    validate_unique(rows, "site_id", "sites.csv")
    validate_positive(
        rows,
        [
            "dg_rating_kva", "tank_capacity_l",
            "diesel_rate_rs_per_l", "hour_meter_reading",
            "last_service_hour_meter"
        ],
        "sites.csv"
    )
    validate_positive(
        rows, ["opening_fuel_l"], "sites.csv", allow_zero=True
    )

    for row in rows:
        if float(row["opening_fuel_l"]) > float(row["tank_capacity_l"]):
            raise ValueError(
                f"Opening fuel exceeds tank capacity: {row['site_id']}"
            )

        if float(row["last_service_hour_meter"]) > float(row["hour_meter_reading"]):
            raise ValueError(
                f"Service meter exceeds current meter: {row['site_id']}"
            )

        validate_date(
            row["last_service_date"], "%Y-%m-%d",
            "last_service_date"
        )

    return rows


def load_runs(file_path):
    columns = [
        "run_id", "site_id", "start_time",
        "end_time", "avg_load_kw"
    ]

    rows = load_csv(file_path, columns)
    validate_unique(rows, "run_id", "run_logs.csv")
    validate_positive(rows, ["avg_load_kw"], "run_logs.csv")

    for row in rows:
        start = validate_date(
            row["start_time"], "%Y-%m-%d %H:%M:%S", "start_time"
        )
        end = validate_date(
            row["end_time"], "%Y-%m-%d %H:%M:%S", "end_time"
        )

        if end <= start:
            raise ValueError(
                f"Run end must be after start: {row['run_id']}"
            )

    return rows


def load_refills(file_path):
    columns = ["refill_id", "site_id", "refill_time", "litres"]
    rows = load_csv(file_path, columns)

    validate_unique(rows, "refill_id", "refills.csv")
    validate_positive(rows, ["litres"], "refills.csv")

    for row in rows:
        validate_date(
            row["refill_time"], "%Y-%m-%d %H:%M:%S",
            "refill_time"
        )

    return rows


def load_services(file_path):
    columns = ["service_id", "site_id", "service_time"]
    rows = load_csv(file_path, columns)

    validate_unique(rows, "service_id", "services.csv")

    for row in rows:
        validate_date(
            row["service_time"], "%Y-%m-%d %H:%M:%S",
            "service_time"
        )

    return rows
