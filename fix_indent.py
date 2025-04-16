#!/usr/bin/env python
"""Fix indentation in sync_commands.py."""


def fix_indentation():
    """Fix indentation error in the sync_commands.py file."""
    file_path = "peopleanalytics/cli_commands/sync_commands.py"

    with open(file_path, "r") as f:
        lines = f.readlines()

    # Looking at the surrounding lines (4046-4052), the correct indentation should be 16 spaces
    # Line 4050 is index 4049 (0-based)
    line_number = 4049

    if len(lines) > line_number:
        # Get the content of the line without leading whitespace
        content = lines[line_number].lstrip()
        # Apply the correct indentation (16 spaces)
        lines[line_number] = "                " + content

    with open(file_path, "w") as f:
        f.writelines(lines)

    print(f"Indentation fixed in {file_path}")


if __name__ == "__main__":
    fix_indentation()
