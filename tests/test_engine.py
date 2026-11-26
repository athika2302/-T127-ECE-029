
import unittest
from src.engine import FuelEngine


def make_site():
    return {
        "site_id": "SITE-001",
        "site_name": "Test Site",
        "city": "Bangalore",
        "dg_rating_kva": "100",
        "tank_capacity_l": "500",
        "diesel_rate_rs_per_l": "90",
        "opening_fuel_l": "300",
        "hour_meter_reading": "100",
        "last_service_hour_meter": "0",
        "last_service_date": "2026-08-01",
    }


def make_run(run_id, start, end, load_kw):
    return {
        "run_id": run_id,
        "site_id": "SITE-001",
        "start_time": start,
        "end_time": end,
        "avg_load_kw": str(load_kw),
    }


class TestFuelEngine(unittest.TestCase):

    def process_data(self, runs=None, refills=None, services=None, site=None):
        engine = FuelEngine(
            sites=[site or make_site()],
            runs=runs or [],
            refills=refills or [],
            services=services or [],
        )
        engine.process()
        return engine

    def test_normal_run(self):
        engine = self.process_data([
            make_run("R1", "2026-09-01 10:00:00",
                     "2026-09-01 12:00:00", 40)
        ])
        self.assertEqual(len(engine.run_costs), 1)
        self.assertEqual(engine.run_costs[0]["load_pct"], 50)
        self.assertEqual(engine.run_costs[0]["litres"], 24.0)

    def test_overload_rejected(self):
        engine = self.process_data([
            make_run("R2", "2026-09-01 10:00:00",
                     "2026-09-01 11:00:00", 81)
        ])
        self.assertEqual(len(engine.run_costs), 0)
        self.assertIn("OVERLOAD", [a["type"] for a in engine.alerts])

    def test_95_percent_exactly_60_minutes(self):
        engine = self.process_data([
            make_run("R3", "2026-09-01 10:00:00",
                     "2026-09-01 11:00:00", 76)
        ])
        self.assertNotIn(
            "OVERLOAD_WARNING", [a["type"] for a in engine.alerts]
        )

    def test_95_percent_more_than_60_minutes(self):
        engine = self.process_data([
            make_run("R4", "2026-09-01 10:00:00",
                     "2026-09-01 11:01:00", 76)
        ])
        self.assertIn(
            "OVERLOAD_WARNING", [a["type"] for a in engine.alerts]
        )

    def test_low_load_over_four_hours(self):
        engine = self.process_data([
            make_run("R5", "2026-09-01 10:00:00",
                     "2026-09-01 14:30:00", 16)
        ])
        self.assertIn("LOW_LOAD", [a["type"] for a in engine.alerts])

    def test_exactly_four_hours_no_low_load(self):
        engine = self.process_data([
            make_run("R6", "2026-09-01 10:00:00",
                     "2026-09-01 14:00:00", 16)
        ])
        self.assertNotIn("LOW_LOAD", [a["type"] for a in engine.alerts])

    def test_overlap_rejected(self):
        engine = self.process_data([
            make_run("R7", "2026-09-01 10:00:00",
                     "2026-09-01 12:00:00", 40),
            make_run("R8", "2026-09-01 11:00:00",
                     "2026-09-01 13:00:00", 40),
        ])
        self.assertEqual(len(engine.run_costs), 1)
        self.assertIn("OVERLAP_ERROR", [a["type"] for a in engine.alerts])

    def test_adjacent_runs_accepted(self):
        engine = self.process_data([
            make_run("R9", "2026-09-01 10:00:00",
                     "2026-09-01 11:00:00", 40),
            make_run("R10", "2026-09-01 11:00:00",
                     "2026-09-01 12:00:00", 40),
        ])
        self.assertEqual(len(engine.run_costs), 2)

    def test_exact_tank_fill_no_spill(self):
        site = make_site()
        site["opening_fuel_l"] = "400"

        refill = {
            "refill_id": "RF1",
            "site_id": "SITE-001",
            "refill_time": "2026-09-01 09:00:00",
            "litres": "100",
        }

        engine = self.process_data(refills=[refill], site=site)

        self.assertEqual(engine.sites["SITE-001"]["fuel"], 500)
        self.assertNotIn("SPILL_ERROR", [a["type"] for a in engine.alerts])

    def test_refill_spill(self):
        refill = {
            "refill_id": "RF2",
            "site_id": "SITE-001",
            "refill_time": "2026-09-01 09:00:00",
            "litres": "250",
        }

        engine = self.process_data(refills=[refill])
        self.assertEqual(engine.sites["SITE-001"]["fuel"], 500)
        self.assertIn("SPILL_ERROR", [a["type"] for a in engine.alerts])

    def test_service_due_at_250_hours(self):
        site = make_site()
        site["hour_meter_reading"] = "249"
        site["last_service_hour_meter"] = "0"

        engine = self.process_data([
            make_run("R11", "2026-09-01 10:00:00",
                     "2026-09-01 11:00:00", 40)
        ], site=site)

        self.assertIn("SERVICE_DUE", [a["type"] for a in engine.alerts])

    def test_service_due_at_180_days(self):
        site = make_site()
        site["last_service_date"] = "2026-03-01"
        site["hour_meter_reading"] = "120"
        site["last_service_hour_meter"] = "0"

        engine = self.process_data([
            make_run("R12", "2026-09-01 10:00:00",
                     "2026-09-01 11:00:00", 40)
        ], site=site)

        self.assertIn("SERVICE_DUE", [a["type"] for a in engine.alerts])

    def test_service_resets_counters(self):
        service = {
            "service_id": "SV1",
            "site_id": "SITE-001",
            "service_time": "2026-09-01 09:00:00",
        }

        engine = self.process_data(services=[service])
        self.assertEqual(
            engine.sites["SITE-001"]["hours_since_service"], 0
        )
        self.assertEqual(len(engine.service_records), 1)


if __name__ == "__main__":
    unittest.main()
