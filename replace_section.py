#!/usr/bin/env python
"""Replace the problematic section in sync_commands.py."""


def replace_section():
    """Replace the problematic section in sync_commands.py."""
    file_path = "peopleanalytics/cli_commands/sync_commands.py"

    # Define the replacement section (properly indented)
    replacement = '''                title Member Performance Comparison
                x-axis ["""
                
                # Add member names to x-axis
                member_names = [f'"{m}"' for m, _ in sorted_members]
                markdown_content += ", ".join(member_names) + "]\\n"
                
                markdown_content += '    y-axis "Score" 0 --> 5\\n    bar ['
'''

    with open(file_path, "r") as f:
        content = f.read()

    # Find the section to replace
    start_marker = "                title Member Performance Comparison"
    end_marker = (
        "                markdown_content += '    y-axis \"Score\" 0 --> 5\\n    bar ['"
    )

    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Error: Could not find start marker.")
        return

    end_idx = content.find(end_marker, start_idx)
    if end_idx == -1:
        print("Error: Could not find end marker.")
        return

    # Ensure we capture the entire line for the end marker
    end_idx = content.find("\n", end_idx) + 1

    # Replace the section
    new_content = content[:start_idx] + replacement + content[end_idx:]

    with open(file_path, "w") as f:
        f.write(new_content)

    print(f"Replaced problematic section in {file_path}")


if __name__ == "__main__":
    replace_section()
