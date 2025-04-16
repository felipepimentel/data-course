#!/usr/bin/env python
"""Fix the specific problematic line in sync_commands.py."""


def fix_line():
    """Fix the problematic line in sync_commands.py."""
    file_path = "peopleanalytics/cli_commands/sync_commands.py"
    line_num = 4050
    replacement_line = (
        "                member_names = [f'\"m\"' for m, _ in sorted_members]\n"
    )

    # Read all lines
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Replace just the problematic line
    if len(lines) >= line_num:
        lines[line_num - 1] = replacement_line

    # Write the file back
    with open(file_path, "w") as f:
        f.writelines(lines)

    print(f"Fixed line {line_num} in {file_path}")


if __name__ == "__main__":
    fix_line()
