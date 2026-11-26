
from src.calculations import (
    calculate_minutes,
    calculate_load_percentage,
    get_fuel_band,
    calculate_fuel_consumed,
    calculate_kwh,
    calculate_fuel_cost
)


# Test 1: Runtime
minutes = calculate_minutes(
    "2026-09-01 10:00:00",
    "2026-09-01 12:00:00"
)
assert minutes == 120


# Test 2: Load percentage
load = calculate_load_percentage(20.2, 25)
assert load == 101


# Test 3: Fuel bands
assert get_fuel_band(25) == 0.08
assert get_fuel_band(50) == 0.12
assert get_fuel_band(75) == 0.17
assert get_fuel_band(100) == 0.22


# Test 4: Fuel consumed
litres = calculate_fuel_consumed(0.17, 100, 120)
assert litres == 34.0


# Test 5: Energy generated
kwh = calculate_kwh(20, 120)
assert kwh == 40.0


# Test 6: Fuel cost
cost = calculate_fuel_cost(34, 90)
assert cost == 3060.0


print("All calculation tests passed!")
