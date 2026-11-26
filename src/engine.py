
from datetime import datetime
from src.calculations import (
    calculate_minutes,
    calculate_load_percentage,
    get_fuel_band,
    calculate_fuel_consumed,
    calculate_kwh,
    calculate_fuel_cost,
)
from src.alerts import check_run_alerts


class FuelEngine:
    def __init__(self, sites, runs, refills, services):
        self.sites = {}
        for row in sites:
            site_id = row["site_id"]
            self.sites[site_id] = {
                **row,
                "fuel": float(row["opening_fuel_l"]),
                "capacity": float(row["tank_capacity_l"]),
                "rating": float(row["dg_rating_kva"]),
                "diesel_rate": float(row["diesel_rate_rs_per_l"]),
                "hours_since_service": (
                    float(row["hour_meter_reading"])
                    - float(row["last_service_hour_meter"])
                ),
                "last_service_date": datetime.strptime(
                    row["last_service_date"], "%Y-%m-%d"
                ),
                "last_run_end": None,
                "accepted_runs": [],
                "refill_alerted": False,
                "service_alerted": False,
            }

        self.runs = runs
        self.refills = refills
        self.services = services

        self.run_costs = []
        self.alerts = []
        self.service_records = []

    def add_alert(self, timestamp, site_id, alert_type, ref_id, detail):
        self.alerts.append({
            "timestamp": timestamp,
            "site_id": site_id,
            "type": alert_type,
            "ref_id": ref_id,
            "detail": detail,
        })

    def process(self):
        events = []

        for row in self.runs:
            events.append((
                datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S"),
                2, "RUN", row
            ))

        for row in self.refills:
            events.append((
                datetime.strptime(row["refill_time"], "%Y-%m-%d %H:%M:%S"),
                1, "REFILL", row
            ))

        for row in self.services:
            events.append((
                datetime.strptime(row["service_time"], "%Y-%m-%d %H:%M:%S"),
                0, "SERVICE", row
            ))

        events.sort(key=lambda event: (event[0], event[1]))

        for event_time, _, event_type, row in events:
            site_id = row["site_id"]

            if site_id not in self.sites:
                raise ValueError(f"Unknown site ID: {site_id}")

            site = self.sites[site_id]

            if event_type == "SERVICE":
                self.process_service(row, site)
            elif event_type == "REFILL":
                self.process_refill(row, site)
            else:
                self.process_run(row, site)

        return self.run_costs, self.alerts

    def process_service(self, row, site):
        site["hours_since_service"] = 0
        site["last_service_date"] = datetime.strptime(
            row["service_time"], "%Y-%m-%d %H:%M:%S"
        )
        site["service_alerted"] = False

        self.service_records.append({
            "site_id": row["site_id"],
            "service_time": row["service_time"],
            "service_cost": 4500.00,
        })

    def process_refill(self, row, site):
        litres = float(row["litres"])

        if litres <= 0:
            raise ValueError(f"Invalid refill quantity: {row['refill_id']}")

        available_space = site["capacity"] - site["fuel"]
        added = min(litres, available_space)
        excess = litres - added

        site["fuel"] += added
        site["refill_alerted"] = False

        if excess > 0:
            self.add_alert(
                row["refill_time"], row["site_id"],
                "SPILL_ERROR", row["refill_id"],
                f"Refill exceeded tank capacity by {excess:.2f} litres"
            )

    def process_run(self, row, site):
        minutes = calculate_minutes(row["start_time"], row["end_time"])
        avg_kw = float(row["avg_load_kw"])

        if avg_kw <= 0:
            raise ValueError(f"Invalid average load: {row['run_id']}")

        load_pct = calculate_load_percentage(avg_kw, site["rating"])

        # Reject overlapping runs.
        start = datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(row["end_time"], "%Y-%m-%d %H:%M:%S")

        if site["last_run_end"] is not None and start < site["last_run_end"]:
            self.add_alert(
                row["end_time"], row["site_id"],
                "OVERLAP_ERROR", row["run_id"],
                "Run overlaps a previously accepted run"
            )
            return

        # Overload: reject without fuel consumption or cost.
        if load_pct > 100:
            self.add_alert(
                row["end_time"], row["site_id"],
                "OVERLOAD", row["run_id"],
                f"Load exceeded 100%: {load_pct}%"
            )
            return

        band_rate = get_fuel_band(load_pct)
        litres = calculate_fuel_consumed(
            band_rate, site["rating"], minutes
        )
        kwh = calculate_kwh(avg_kw, minutes)
        fuel_cost = calculate_fuel_cost(
            litres, site["diesel_rate"]
        )

        site["fuel"] -= litres
        site["hours_since_service"] += minutes / 60
        site["last_run_end"] = end

        self.run_costs.append({
            "run_id": row["run_id"],
            "site_id": row["site_id"],
            "start_time": row["start_time"],
            "minutes": minutes,
            "load_pct": load_pct,
            "band_rate": band_rate,
            "litres": litres,
            "kwh": kwh,
            "fuel_cost": fuel_cost,
            "fuel_after_l": round(site["fuel"], 2),
        })

        site["accepted_runs"].append({
            "avg_kw": avg_kw,
            "rating": site["rating"],
        })

        # Run-specific alerts.
        for alert in check_run_alerts(
            load_pct, minutes, row["run_id"],
            row["site_id"], row["end_time"]
        ):
            self.alerts.append(alert)

        self.check_refill_due(row, site)
        self.check_service_due(row, site, end)


    def check_refill_due(self, row, site):
        recent = site["accepted_runs"][-5:]

        if not recent or site["refill_alerted"]:
            return

        average_kw = sum(r["avg_kw"] for r in recent) / len(recent)
        average_load = calculate_load_percentage(
            average_kw, site["rating"]
        )

        band_rate = get_fuel_band(average_load)
        litres_per_hour = band_rate * site["rating"]

        if litres_per_hour <= 0:
            return

        hours_left = site["fuel"] / litres_per_hour

        if hours_left <= 8:
            self.add_alert(
                row["end_time"], row["site_id"],
                "REFILL_DUE", row["run_id"],
                f"Estimated fuel remaining: {hours_left:.2f} hours"
            )
            site["refill_alerted"] = True

    def check_service_due(self, row, site, run_end):
        days_since_service = (
            run_end - site["last_service_date"]
        ).days

        if (
            not site["service_alerted"]
            and (
                site["hours_since_service"] >= 250
                or days_since_service >= 180
            )
        ):
            self.add_alert(
                row["end_time"], row["site_id"],
                "SERVICE_DUE", row["run_id"],
                "Service due: 250 run hours or 180 days reached"
            )
            site["service_alerted"] = True
