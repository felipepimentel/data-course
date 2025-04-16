#!/usr/bin/env python
"""Fix indentation in sync_commands.py by replacing the problematic line."""


def fix_indentation():
    """Fix indentation error in the sync_commands.py file by replacing the problematic line."""
    file_path = "peopleanalytics/cli_commands/sync_commands.py"
    problem_line_number = 4050

    with open(file_path, "r") as f:
        lines = f.readlines()

    # Replace the problematic line with a correctly formatted version
    if len(lines) >= problem_line_number:
        # The line index is 0-based, but line numbers are 1-based
        lines[problem_line_number - 1] = (
            "                member_names = [f'\"m\"' for m, _ in sorted_members]\n"
        )

    with open(file_path, "w") as f:
        f.writelines(lines)

    print(f"Fixed line {problem_line_number} in {file_path}")


if __name__ == "__main__":
    fix_indentation()
