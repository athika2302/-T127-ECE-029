# Diesel Generator Fuel, Runtime and Maintenance Cost Engine

**Project Code:** T127-ECE-029  
**Developer:** Syeda Athika S A  
**Language:** Python 3.10+

A Python application for monitoring diesel generators across multiple telecom sites. It processes runtime logs, diesel refills and maintenance records, calculates operating costs and fuel usage, detects operational alerts, and produces monthly CSV reports.

## Features

- Loads telecom site, generator run, refill and maintenance data from CSV files.
- Validates input records and processes them chronologically.
- Calculates runtime, load percentage, fuel consumption, generated energy and fuel cost.
- Tracks diesel balance and tank capacity.
- Detects overload, low-load, refill due, spill, overlap and maintenance conditions.
- Generates detailed run, alert and monthly site reports.
- Provides a command-driven workflow through `data/commands.txt`.

## Technology Stack

| Component | Technology |
| --- | --- |
| Language | Python 3.10+ |
| Input/output | CSV |
| Testing | Python `unittest` |
| Development | Visual Studio Code |

The project uses only the Python standard library. `requirements.txt` is therefore empty.

## Project Structure

```text
capstone_project/
├── src/
│   ├── main.py
│   ├── command_parser.py
│   ├── data_loader.py
│   ├── engine.py
│   ├── calculations.py
│   ├── alerts.py
│   └── report_generator.py
├── tests/
│   ├── test_calculations.py
│   ├── test_engine.py
│   └── verify_sample.py
├── data/
│   ├── commands.txt
│   ├── sites.csv
│   ├── run_logs.csv
│   ├── refills.csv
│   └── services.csv
├── output/
│   ├── run_costs.csv
│   ├── alerts.csv
│   └── site_report.csv
├── docs/
│   └── design_document.md
├── requirements.txt
└── decision_log.md
```

## Installation

### 1. Prerequisites

- Python 3.10 or later
- Git

Check Python:

```bash
python --version
```

### 2. Clone the repository

```bash
git clone https://github.com/athika2302/Diesel_generator.git
cd Diesel_generator
```

### 3. Verify setup

This project has no third-party dependencies.

```bash
python -m pip install -r requirements.txt
```

## Running the Application

Run the command-driven workflow:

```bash
python -m src.main
```

The application reads `data/commands.txt`, processes the input CSV files and saves reports in the `output/` directory.

### Command File

The default `data/commands.txt` contains:

```text
LOAD_SITES|sites.csv
LOAD_RUNS|run_logs.csv
LOAD_REFILLS|refills.csv
LOAD_SERVICES|services.csv
PROCESS
REPORT|2026-09
REPORT|2026-10
```

| Command | Description |
| --- | --- |
| `LOAD_SITES` | Loads site and generator details |
| `LOAD_RUNS` | Loads generator runtime records |
| `LOAD_REFILLS` | Loads diesel refill records |
| `LOAD_SERVICES` | Loads maintenance records |
| `PROCESS` | Processes all events chronologically |
| `REPORT\|YYYY-MM` | Generates a monthly report |

Load commands must reference CSV files inside `data/`. Run `PROCESS` before generating any report.

## Input CSV Files

### `data/sites.csv`

Contains site name, city, DG rating, tank capacity, diesel rate, opening fuel and maintenance meter information.

### `data/run_logs.csv`

Contains run ID, site ID, start time, end time and average load in kW.

### `data/refills.csv`

Contains refill ID, site ID, refill time and quantity in litres.

### `data/services.csv`

Contains maintenance service ID, site ID and service time.

CSV values should use the formats and column names shown in the supplied sample files.

## Generated Outputs

| File | Description |
| --- | --- |
| `output/run_costs.csv` | Accepted runs with runtime, load, fuel, energy and cost calculations |
| `output/alerts.csv` | Overload, overlap, refill, low-load and maintenance alerts |
| `output/site_report.csv` | Monthly site-wise runtime, fuel, cost and alert summary |

The console also prints each monthly report after generation.

## Business Rules

### Load Percentage

```text
Load % = (Average kW / (DG Rating in kVA × 0.8)) × 100
```

The result is rounded to the nearest whole number using half-up rounding.

### Fuel Consumption Bands

| Load Percentage | Fuel Rate |
| --- | --- |
| 0–25% | 0.08 litres/kVA/hour |
| 26–50% | 0.12 litres/kVA/hour |
| 51–75% | 0.17 litres/kVA/hour |
| 76–100% | 0.22 litres/kVA/hour |

Additional rules include:

- Runs above 100% load are rejected with `OVERLOAD`.
- 91–100% load for more than 60 continuous minutes produces `OVERLOAD_WARNING`.
- Load below 30% for more than four hours produces `LOW_LOAD`.
- Refill volume above tank capacity produces `SPILL_ERROR`.
- Overlapping runtime records for the same site produce `OVERLAP_ERROR`.
- Fuel remaining for eight hours or less produces `REFILL_DUE`.
- Maintenance is due after 250 operating hours or 180 elapsed days.
- Each service costs ₹4,500 and resets the maintenance counters.
- If generated energy is zero, cost per kWh is reported as `NA`.

## Testing

Run the unittest suite:

```bash
python -m unittest discover -s tests -v
```

Run the calculation checks separately:

```bash
python tests/test_calculations.py
```

Run sample-data verification:

```bash
python -m tests.verify_sample
```

The unit suite currently contains 13 passing tests. They cover normal runs, overload handling, high and low load, overlapping runs, tank capacity, refills, maintenance thresholds and counter resets.

## Sample Dataset

The supplied sample data contains:

- 12 telecom sites
- 906 runtime records
- 80 refill records
- 2 maintenance records

The verified execution accepts 904 runtime records and generates 64 alerts. It produces September 2026 and October 2026 reports.

## Troubleshooting

**Module not found**

Run the application from the project root:

```bash
python -m src.main
```

**CSV or command errors**

- Confirm that all CSV files are inside `data/`.
- Match the command filename exactly.
- Preserve the pipe (`|`) separator in `commands.txt`.
- Run `LOAD_SITES` and `LOAD_RUNS` before `PROCESS`.
- Run `PROCESS` before `REPORT`.

**Python version errors**

Use Python 3.10 or later. Create a virtual environment if needed:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

## Documentation

- [Design Document](docs/design_document.md)
- [Decision Log](decision_log.md)
