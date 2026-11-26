
from pathlib import Path

from src.data_loader import (
    load_sites,
    load_runs,
    load_refills,
    load_services,
)
from src.engine import FuelEngine
from src.report_generator import generate_monthly_report


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def main():
    print("\n========== SAMPLE DATA VERIFICATION ==========\n")

    sites = load_sites(DATA_DIR / "sites.csv")
    runs = load_runs(DATA_DIR / "run_logs.csv")
    refills = load_refills(DATA_DIR / "refills.csv")
    services = load_services(DATA_DIR / "services.csv")

    print("INPUT COUNTS")
    print("Sites:", len(sites))
    print("Runs:", len(runs))
    print("Refills:", len(refills))
    print("Services:", len(services))

    engine = FuelEngine(sites, runs, refills, services)
    engine.process()

    print("\nPROCESSING COUNTS")
    print("Accepted runs:", len(engine.run_costs))
    print("Alerts:", len(engine.alerts))

    run_ids = [
        "RUN-0137", "RUN-0147", "RUN-0152", "RUN-0153",
        "RUN-0157", "RUN-0165", "RUN-0169", "RUN-0174",
        "RUN-0184", "RUN-0187", "RUN-0254", "RUN-0061",
        "RUN-0653", "RUN-0654", "RUN-0659", "RUN-0661"
    ]

    print("\nIMPORTANT RUN RECORDS")

    for run_id in run_ids:
        record = next(
            (r for r in engine.run_costs if r["run_id"] == run_id),
            None
        )

        if record:
            print(run_id, "ACCEPTED", record)
        else:
            print(run_id, "NOT IN ACCEPTED RUNS")

    print("\nIMPORTANT ALERTS")

    reference_ids = [
        "RUN-0157", "RUN-0165", "RUN-0169",
        "RUN-0174", "RUN-0184", "RUN-0254",
        "RUN-0061", "RUN-0654", "RF-025", "RF-043"
    ]

    for ref_id in reference_ids:
        matching = [
            a for a in engine.alerts
            if a["ref_id"] == ref_id
        ]

        print(ref_id, matching if matching else "NO ALERT")

    print("\nMONTHLY REPORT CHECK")

    october_report = generate_monthly_report(
        "2026-10",
        engine.sites,
        engine.run_costs,
        engine.alerts,
        engine.service_records,
    )

    site_009 = next(
        (r for r in october_report if r["site_id"] == "SITE-009"),
        None
    )

    print("SITE-009 October report:", site_009)

    print("\n========== VERIFICATION FINISHED ==========")


if __name__ == "__main__":
    main()
