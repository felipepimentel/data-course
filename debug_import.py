try:
    import sys
    import traceback

    print("Attempting to import sync_commands...")
    from peopleanalytics.cli_commands.sync_commands import SyncCommand

    print("Success! SyncCommand imported correctly.")
    print(f"SyncCommand class: {SyncCommand}")

except Exception as e:
    print(f"\nError type: {type(e).__name__}")
    print(f"Error message: {e}")
    print("\nTraceback:")
    traceback.print_exc()

    print("\nPython path:")
    for path in sys.path:
        print(f"  - {path}")
