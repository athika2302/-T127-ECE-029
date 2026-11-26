# Technical Design Document
## T127-ECE-029
### Diesel Generator Fuel, Runtime and Maintenance Cost Engine for Telecom Sites

**Developed by:** Syeda Athika S A

**Programming Language:** Python 3.15.2

---

## 1. Introduction

The Diesel Generator Fuel, Runtime and Maintenance Cost Engine is a Python-based application developed to monitor diesel generator operations across multiple telecom sites.

The system processes site information, generator runtime logs, diesel refill records, and maintenance service records. It calculates fuel consumption, energy generation, operational costs, remaining fuel, and maintenance requirements.

The application uses CSV files for input and output and follows a command-driven execution approach.

## 2. System Objectives

The main objectives are:

- Process generator runtime records from multiple sites.
- Calculate generator load percentage.
- Estimate diesel consumption using predefined load bands.
- Calculate generated energy in kWh.
- Calculate fuel operating costs.
- Maintain the remaining fuel balance.
- Identify abnormal operating conditions.
- Track maintenance requirements.
- Generate monthly site-wise reports.

## 3. System Architecture

The application follows a modular architecture in which each Python module has a specific responsibility.

### Architecture Diagram

```text
          INPUT CSV FILES
                 |
                 v
          COMMAND FILE
                 |
                 v
          COMMAND PARSER
                 |
                 v
           DATA LOADER
                 |
                 v
        DATA VALIDATION
                 |
                 v
          PROCESSING ENGINE
                 |
        +--------+--------+
        |        |        |
        v        v        v
   Calculations Alerts  Fuel and
                       Maintenance
                       Tracking
        |        |        |
        +--------+--------+
                 |
                 v
         REPORT GENERATOR
                 |
                 v
           OUTPUT CSV FILES
```

## 4. Module Design

### 4.1 Main Module

File: `src/main.py`

Responsibilities:

- Start application execution.
- Read the command file.
- Coordinate data loading.
- Initialize the processing engine.
- Generate monthly reports.
- Save output files.

### 4.2 Command Parser

File: `src/command_parser.py`

Responsibilities:

- Read commands from `commands.txt`.
- Identify supported commands.
- Validate command arguments.
- Reject unknown or incorrectly formatted commands.

### 4.3 Data Loader

File: `src/data_loader.py`

Responsibilities:

- Load site records.
- Load generator runtime records.
- Load refill records.
- Load maintenance records.
- Validate required fields, dates, identifiers, and numeric values.

### 4.4 Calculation Module

File: `src/calculations.py`

Responsibilities:

- Calculate generator runtime.
- Calculate load percentage.
- Identify the applicable fuel consumption band.
- Calculate fuel consumption.
- Calculate generated energy.
- Calculate fuel cost.
- Apply half-up rounding where required.

### 4.5 Processing Engine

File: `src/engine.py`

The processing engine is the central component of the application.

Responsibilities:

- Process operational events chronologically.
- Maintain site-wise fuel balances.
- Calculate fuel consumption for accepted runs.
- Track accepted generator runtime.
- Detect overlapping runtime records.
- Monitor refill requirements.
- Track maintenance counters.
- Generate operational records and alerts.

Events are processed in chronological order. When timestamps are equal, the processing priority is:

1. Service
2. Refill
3. Generator run

### 4.6 Alert Module

File: `src/alerts.py`

Responsibilities:

- Identify overload conditions.
- Generate high-load warnings.
- Detect prolonged low-load operation.
- Support operational alert generation.

The processing engine also generates fuel, refill, overlap, and maintenance-related alerts.

### 4.7 Report Generator

File: `src/report_generator.py`

Responsibilities:

- Generate run cost records.
- Generate alert records.
- Calculate monthly site-wise summaries.
- Calculate cost per kWh.
- Save reports in CSV format.

## 5. Data Flow

The system follows these processing stages:

**Stage 1: Data Input**

The application receives four CSV files containing site details, generator runs, diesel refills, and maintenance records.

**Stage 2: Command Processing**

The command parser reads `commands.txt` and identifies which operations must be performed.

**Stage 3: Data Validation**

The data loader checks required fields, record formats, numeric values, and duplicate identifiers.

**Stage 4: Event Processing**

The engine combines operational events and processes them chronologically.

**Stage 5: Business Rule Execution**

The system calculates fuel consumption, generated energy, operating costs, fuel balance, and maintenance requirements.

**Stage 6: Alert Generation**

The system identifies conditions requiring operational attention.

**Stage 7: Report Generation**

The report generator creates run-level, alert-level, and monthly site-level CSV files.

## 6. Important Calculations

### 6.1 Load Percentage

Load percentage is calculated using:

Load % = (Average Load in kW / (DG Rating in kVA × 0.8)) × 100

### 6.2 Fuel Consumption

Fuel consumption is calculated using:

Fuel Consumed = Fuel Band Rate × DG Rating × Runtime in Hours

### 6.3 Generated Energy

Generated Energy (kWh) = Average Load (kW) × Runtime (Hours)

### 6.4 Fuel Cost

Fuel Cost = Fuel Consumed × Diesel Rate per Litre

### 6.5 Cost per kWh

Cost per kWh = (Fuel Cost + Maintenance Cost) / Generated Energy

If generated energy is zero, the report displays `NA`.

## 7. Alert Handling

The system identifies the following operational conditions:

| Alert | Description |
|---|---|
| OVERLOAD | Generator load exceeds 100% |
| OVERLOAD_WARNING | Load between 91% and 100% for more than 60 minutes |
| LOW_LOAD | Load below 30% for more than four hours |
| REFILL_DUE | Remaining fuel is sufficient for eight hours or less at the estimated operating rate |
| SPILL_ERROR | Refill exceeds available tank capacity |
| SERVICE_DUE | Maintenance threshold reached |
| OVERLAP_ERROR | Runtime records overlap for the same site |

## 8. Maintenance Tracking

Maintenance is required when either of these conditions is met:

- 250 generator operating hours.
- 180 days since the previous service.

The maintenance cost is ₹4,500 per service.

After processing a service event, the maintenance counters are reset.

## 9. Testing Strategy

The application uses Python's built-in `unittest` framework.

Testing includes:

- Normal generator operation.
- Load percentage boundaries.
- Overload rejection.
- High-load warning conditions.
- Low-load conditions.
- Overlapping runtime records.
- Adjacent runtime records.
- Exact tank-capacity refills.
- Refill spill conditions.
- Maintenance based on operating hours.
- Maintenance based on elapsed days.
- Maintenance counter resets.

**Current unit test result:** 13 tests passed.

The supplied sample dataset is also used to verify large-scale processing and business-rule edge cases.

## 10. Output Design

The application generates the following files:

### run_costs.csv

Stores accepted generator run calculations, including runtime, load percentage, fuel consumption, generated energy, fuel cost, and remaining fuel.

### alerts.csv

Stores operational alerts with timestamps, site identifiers, alert types, references, and descriptions.

### site_report.csv

Stores monthly site-wise summaries, including runtime hours, fuel consumption, fuel cost, maintenance cost, energy generation, cost per kWh, and alert counts.

## 11. Conclusion

The system provides a modular and command-driven solution for monitoring diesel generator operations across telecom sites.

Its design separates data loading, validation, calculations, event processing, alert handling, and report generation. This improves code organization, maintainability, testing, and future extensibility.