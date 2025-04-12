"""
Base command class for all CLI commands.

This module provides a base class that all command modules should inherit from
to ensure consistent implementation and behavior.
"""

import argparse
from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """Base class for all CLI commands."""

    def __init__(self):
        """Initialize the command."""
        pass

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.

        Args:
            parser: The argparse parser or subparser to add arguments to
        """
        pass

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """
        Execute the command.

        Args:
            args: The parsed command-line arguments

        Returns:
            int: Return code (0 for success, non-zero for errors)
        """
        pass
