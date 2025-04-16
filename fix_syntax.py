import py_compile
import sys
import traceback


def check_syntax(file_path):
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"No syntax errors found in {file_path}")
        return True
    except py_compile.PyCompileError:
        print(f"Syntax error in {file_path}:")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Error checking syntax: {e}")
        return False


if __name__ == "__main__":
    file_path = "peopleanalytics/cli_commands/sync_commands.py"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    check_syntax(file_path)
