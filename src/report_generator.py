
import csv
from pathlib import Path


RUN_FIELDS = [
    "run_id",
    "site_id",
    "start_time",
    "minutes",
    "load_pct",
    "band_rate",
    "litres",
    "kwh",
    "fuel_cost",
    "fuel_after_l",
]

ALERT_FIELDS = [
    "timestamp",
    "site_id",
    "type",
    "ref_id",
    "detail",
]

REPORT_FIELDS = [
    "month",
    "site_id",
    "run_hours",
    "litres",
    "fuel_cost",
    "service_cost",
    "kwh",
    "cost_per_kwh",
    "overload_alerts",
    "low_load_alerts",
    "refill_due_alerts",
    "service_due_alerts",
]


def write_csv(file_path, fieldnames, rows):
    """Write records to a CSV file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_monthly_report(month, sites, run_costs, alerts, services):
    """Generate a monthly report for every registered site."""

    report_rows = []

    for site_id in sorted(sites):

        # Select runs belonging to this month and site.
        site_runs = [
            run for run in run_costs
            if run["site_id"] == site_id
            and run["start_time"][:7] == month
        ]

        # Select services performed in this month and site.
        site_services = [
            service for service in services
            if service["site_id"] == site_id
            and service["service_time"][:7] == month
        ]

        # Select alerts belonging to this month and site.
        site_alerts = [
            alert for alert in alerts
            if alert["site_id"] == site_id
            and alert["timestamp"][:7] == month
        ]

        # Calculate monthly totals.
        run_hours = sum(
            float(run["minutes"]) for run in site_runs
        ) / 60

        total_litres = sum(
            float(run["litres"]) for run in site_runs
        )

        total_fuel_cost = sum(
            float(run["fuel_cost"]) for run in site_runs
        )

        total_service_cost = sum(
            float(service.get("service_cost", 4500))
            for service in site_services
        )

        total_kwh = sum(
            float(run["kwh"]) for run in site_runs
        )

        # Calculate cost per kWh.
        if total_kwh == 0:
            cost_per_kwh = "NA"
        else:
            cost_per_kwh = f"{(total_fuel_cost + total_service_cost) / total_kwh:.2f}"

        # Count overload errors and warnings.
        overload_count = sum(
            alert["type"] in ("OVERLOAD", "OVERLOAD_WARNING")
            for alert in site_alerts
        )

        low_load_count = sum(
            alert["type"] == "LOW_LOAD"
            for alert in site_alerts
        )

        refill_due_count = sum(
            alert["type"] == "REFILL_DUE"
            for alert in site_alerts
        )

        service_due_count = sum(
            alert["type"] == "SERVICE_DUE"
            for alert in site_alerts
        )

        report_rows.append({
            "month": month,
            "site_id": site_id,
            "run_hours": f"{run_hours:.2f}",
            "litres": f"{total_litres:.2f}",
            "fuel_cost": f"{total_fuel_cost:.2f}",
            "service_cost": f"{total_service_cost:.2f}",
            "kwh": f"{total_kwh:.2f}",
            "cost_per_kwh": cost_per_kwh,
            "overload_alerts": overload_count,
            "low_load_alerts": low_load_count,
            "refill_due_alerts": refill_due_count,
            "service_due_alerts": service_due_count,
        })

    return report_rows


def save_outputs(output_dir, run_costs, alerts):
    """Save run costs and alerts to CSV files."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(
        output_dir / "run_costs.csv",
        RUN_FIELDS,
        run_costs,
    )

    write_csv(
        output_dir / "alerts.csv",
        ALERT_FIELDS,
        alerts,
    )
