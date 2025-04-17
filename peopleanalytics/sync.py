"""
Sync module for People Analytics.

This module provides a wrapper around the DataSync class for data synchronization.
"""

import logging
from pathlib import Path
from typing import Any, List, Union

from peopleanalytics.cli_commands.sync_commands import DataSync


class Sync:
    """
    Wrapper for DataSync class providing core synchronization functionality.

    This class provides a simplified interface to the DataSync functionality
    for use in scripts and applications.
    """

    def __init__(
        self,
        data_dir: Union[str, Path] = "data",
        output_dir: Union[str, Path] = "output",
        force: bool = False,
        ignore_errors: bool = False,
    ):
        """
        Initialize the Sync wrapper.

        Args:
            data_dir: Directory containing data files
            output_dir: Directory to store output files
            force: Force reprocessing of files
            ignore_errors: Ignore errors and continue processing
        """
        self.data_sync = DataSync()
        self.data_sync.data_dir = Path(data_dir)
        self.data_sync.output_dir = Path(output_dir)
        self.data_sync.force = force
        self.data_sync.ignore_errors = ignore_errors

        # Initialize logger
        self.logger = logging.getLogger("sync")

    def sync(self, **kwargs) -> List[str]:
        """
        Execute the sync process.

        Args:
            **kwargs: Additional options to pass to the DataSync instance

        Returns:
            List of result messages
        """
        # Update any additional options
        for key, value in kwargs.items():
            if hasattr(self.data_sync, key):
                setattr(self.data_sync, key, value)

        try:
            # Ensure directories exist
            self.data_sync._ensure_directories()

            # Execute sync
            return self.data_sync.sync()
        except Exception as e:
            self.logger.error(f"Error during sync: {e}")
            if not self.data_sync.ignore_errors:
                raise
            return [f"ERROR: {str(e)}"]

    def set_option(self, option_name: str, value: Any) -> bool:
        """
        Set an option on the underlying DataSync instance.

        Args:
            option_name: Name of the option to set
            value: Value to set

        Returns:
            True if option was set, False otherwise
        """
        if hasattr(self.data_sync, option_name):
            setattr(self.data_sync, option_name, value)
            return True
        return False
