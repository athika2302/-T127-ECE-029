
from pathlib import Path

from src.command_parser import parse_commands
from src.data_loader import (
    load_sites,
    load_runs,
    load_refills,
    load_services,
)
from src.engine import FuelEngine
from src.report_generator import (
    save_outputs,
    generate_monthly_report,
    write_csv,
    REPORT_FIELDS,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


def print_monthly_report(report_rows):
    """Display monthly site reports in the terminal."""

    print("\n" + "=" * 90)
    print("                 MONTHLY SITE REPORT")
    print("=" * 90)

    for row in report_rows:
        print(f"\nMonth             : {row['month']}")
        print(f"Site ID           : {row['site_id']}")
        print(f"Run Hours         : {row['run_hours']}")
        print(f"Fuel Consumed     : {row['litres']} litres")
        print(f"Fuel Cost         : Rs. {row['fuel_cost']}")
        print(f"Service Cost      : Rs. {row['service_cost']}")
        print(f"Energy Generated  : {row['kwh']} kWh")
        print(f"Cost per kWh      : Rs. {row['cost_per_kwh']}")
        print(f"Overload Alerts   : {row['overload_alerts']}")
        print(f"Low Load Alerts   : {row['low_load_alerts']}")
        print(f"Refill Due Alerts : {row['refill_due_alerts']}")
        print(f"Service Due Alerts: {row['service_due_alerts']}")
        print("-" * 90)


def main():
    print("\n" + "=" * 55)
    print("       DIESEL GENERATOR MANAGEMENT ENGINE")
    print("=" * 55)

    sites = []
    runs = []
    refills = []
    services = []

    engine = None
    all_report_rows = []

    print("\nReading command file...")

    commands = parse_commands(DATA_DIR / "commands.txt")

    print("Command file loaded successfully.")

    for command, args in commands:

        if command == "LOAD_SITES":
            sites = load_sites(DATA_DIR / args[0])
            print(f"\nSites loaded       : {len(sites)}")

        elif command == "LOAD_RUNS":
            runs = load_runs(DATA_DIR / args[0])
            print(f"Run logs loaded    : {len(runs)}")

        elif command == "LOAD_REFILLS":
            refills = load_refills(DATA_DIR / args[0])
            print(f"Refills loaded     : {len(refills)}")

        elif command == "LOAD_SERVICES":
            services = load_services(DATA_DIR / args[0])
            print(f"Services loaded    : {len(services)}")

        elif command == "PROCESS":

            if not sites or not runs:
                raise ValueError(
                    "Load sites and runs before PROCESS."
                )

            print("\n" + "-" * 55)
            print("PROCESSING GENERATOR EVENTS")
            print("-" * 55)

            engine = FuelEngine(
                sites,
                runs,
                refills,
                services
            )

            run_costs, alerts = engine.process()

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            save_outputs(
                OUTPUT_DIR,
                run_costs,
                alerts
            )

            rejected_runs = len(runs) - len(run_costs)

            print("\nProcessing completed successfully!")
            print(f"Total input runs    : {len(runs)}")
            print(f"Accepted runs       : {len(run_costs)}")
            print(f"Rejected runs       : {rejected_runs}")
            print(f"Generated alerts    : {len(alerts)}")

            print("\nDetailed output files saved:")
            print("  output/run_costs.csv")
            print("  output/alerts.csv")

        elif command == "REPORT":

            if engine is None:
                raise ValueError(
                    "Execute PROCESS before generating REPORT."
                )

            month = args[0]

            report = generate_monthly_report(
                month,
                engine.sites,
                engine.run_costs,
                engine.alerts,
                engine.service_records
            )

            all_report_rows.extend(report)

            print(f"\nMonthly report generated for {month}.")

            # Display the actual report in the terminal.
            print_monthly_report(report)

    if all_report_rows:

        write_csv(
            OUTPUT_DIR / "site_report.csv",
            REPORT_FIELDS,
            all_report_rows
        )

        print("\nMonthly report saved:")
        print("  output/site_report.csv")

    print("\n" + "=" * 55)
    print("          PROJECT EXECUTION COMPLETED")
    print("=" * 55)


if __name__ == "__main__":
    main()
