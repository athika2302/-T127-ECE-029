
from pathlib import Path
import re


COMMAND_ARGUMENTS = {
    "LOAD_SITES": 1,
    "LOAD_RUNS": 1,
    "LOAD_REFILLS": 1,
    "LOAD_SERVICES": 1,
    "PROCESS": 0,
    "REPORT": 1
}


def parse_commands(file_path):
    """
    Read commands.txt and convert each command
    into a structured Python list.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Command file not found: {path}")

    commands = []

    with path.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):

            line = line.strip()

            # Ignore blank lines and comments
            if not line or line.startswith("#"):
                continue

            parts = [part.strip() for part in line.split("|")]

            command_name = parts[0]
            arguments = parts[1:]

            # Validate command name
            if command_name not in COMMAND_ARGUMENTS:
                raise ValueError(
                    f"Unknown command '{command_name}' "
                    f"at line {line_number}"
                )

            # Validate number of arguments
            expected = COMMAND_ARGUMENTS[command_name]

            if len(arguments) != expected or any(not arg for arg in arguments):
                raise ValueError(
                    f"Invalid arguments for {command_name} "
                    f"at line {line_number}"
                )

            # Validate report month
            if command_name == "REPORT":
                if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", arguments[0]):
                    raise ValueError(
                        f"Invalid report month at line {line_number}"
                    )

            commands.append((command_name, arguments))

    return commands
