# Decision Log

## Project: T127-ECE-029
**Project Name:** Diesel Generator Fuel, Runtime and Maintenance Cost Engine for Telecom Sites  
**Developer:** Syeda Athika S A

This document records the major technical and design decisions made during development.

| No. | Decision | Reason |
|---|---|---|
| 1 | Use Python 3.10+ | Python provides a simple and suitable environment for data processing and calculations. |
| 2 | Use CSV files for input and output | CSV files make operational records easy to store, read, and exchange. |
| 3 | Use a command-file-driven approach | The assignment requires execution through commands without a user interface. |
| 4 | Divide the application into separate modules | Modular design improves readability, testing, and maintainability. |
| 5 | Process events chronologically | This ensures fuel balances and maintenance information are updated in the correct sequence. |
| 6 | Apply half-up rounding for load percentage | This follows the specified business rule for load-band selection. |
| 7 | Reject overloaded and overlapping runs | Invalid runtime records must not be included in accepted run calculations. |
| 8 | Use the last five accepted runs for refill projection | This follows the specified fuel refill requirement. |
| 9 | Track maintenance using both runtime hours and elapsed days | This ensures maintenance is identified when either threshold is reached. |
| 10 | Use Python's built-in unittest framework | It allows automated testing without requiring an additional testing library. |

## Conclusion

These decisions were made to meet the assignment requirements while keeping the application modular, reliable, and easy to test.