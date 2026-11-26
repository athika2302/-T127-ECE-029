
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


def round_half_up(value, decimal_places=2):
    """Round numbers using commercial half-up rounding."""
    quantum = Decimal("1").scaleb(-decimal_places)

    return float(
        Decimal(str(value)).quantize(
            quantum,
            rounding=ROUND_HALF_UP
        )
    )


def calculate_minutes(start_time, end_time):
    """Calculate generator runtime in minutes."""

    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    if end <= start:
        raise ValueError("End time must be after start time")

    return int((end - start).total_seconds() / 60)


def calculate_load_percentage(avg_load_kw, rating_kva):
    """Calculate generator load percentage."""

    if rating_kva <= 0:
        raise ValueError("DG rating must be greater than zero")

    load_percentage = (avg_load_kw / (rating_kva * 0.8)) * 100

    return int(round_half_up(load_percentage, 0))


def get_fuel_band(load_percentage):
    """Return fuel consumption rate based on load percentage."""

    if load_percentage <= 25:
        return 0.08
    elif load_percentage <= 50:
        return 0.12
    elif load_percentage <= 75:
        return 0.17
    elif load_percentage <= 100:
        return 0.22
    else:
        raise ValueError("OVERLOAD: Load exceeds 100%")


def calculate_fuel_consumed(band_rate, rating_kva, minutes):
    """Calculate litres consumed during a generator run."""

    hours = minutes / 60
    litres = band_rate * rating_kva * hours

    return round_half_up(litres, 2)


def calculate_kwh(avg_load_kw, minutes):
    """Calculate electrical energy generated in kWh."""

    hours = minutes / 60
    return round_half_up(avg_load_kw * hours, 2)


def calculate_fuel_cost(litres, diesel_rate):
    """Calculate fuel cost in rupees."""

    return round_half_up(litres * diesel_rate, 2)
