import os
import shutil
import tempfile
import unittest
from pathlib import Path

from peopleanalytics.cli_commands.sync_commands import DataSync


class TestPessoaAnoStructure(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.output_dir = Path(self.temp_dir) / "output"

        # Create directory structure
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # Create test directories
        self._create_test_structure()

        # Create DataSync instance
        self.sync = DataSync(
            data_dir=str(self.data_dir),
            output_dir=str(self.output_dir),
            ignore_errors=True,
            verbose=True,
        )

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)

    def _create_test_structure(self):
        # Create pessoas and anos
        pessoas = ["pessoa1", "pessoa2"]
        anos = ["2022", "2023"]

        for pessoa in pessoas:
            for ano in anos:
                # Skip pessoa2/2022 to test filtering
                if pessoa == "pessoa2" and ano == "2022":
                    continue

                # Create directory
                dir_path = self.data_dir / pessoa / ano
                os.makedirs(dir_path, exist_ok=True)

                # Create resultado file
                with open(dir_path / "resultado.json", "w") as f:
                    f.write('{"test": "data"}')

                # Add YAML file for pessoa2/2023
                if pessoa == "pessoa2" and ano == "2023":
                    with open(dir_path / "resultado.yaml", "w") as f:
                        f.write("test: data")

    def test_process_pessoa_ano_structure(self):
        """Test the processing of pessoa/ano structure"""
        # Execute the processing
        valid_dirs = self.sync._process_pessoa_ano_structure()

        # Expected directories
        expected_dirs = [
            self.data_dir / "pessoa1" / "2022",
            self.data_dir / "pessoa1" / "2023",
            self.data_dir / "pessoa2" / "2023",
        ]

        # Check number of directories
        self.assertEqual(len(valid_dirs), len(expected_dirs))

        # Check each expected directory is present
        for expected_dir in expected_dirs:
            self.assertIn(expected_dir, valid_dirs)

    def test_process_pessoa_ano_structure_with_filters(self):
        """Test the processing of pessoa/ano structure with filters"""
        # Set pessoa filter
        self.sync.pessoa = "pessoa1"
        valid_dirs = self.sync._process_pessoa_ano_structure()

        # Check only pessoa1 directories are returned
        self.assertEqual(len(valid_dirs), 2)
        for dir_path in valid_dirs:
            self.assertTrue("pessoa1" in str(dir_path))

        # Reset pessoa filter and set ano filter
        self.sync.pessoa = None
        self.sync.ano = "2022"
        valid_dirs = self.sync._process_pessoa_ano_structure()

        # Check only 2022 directories are returned
        self.assertEqual(len(valid_dirs), 1)
        for dir_path in valid_dirs:
            self.assertTrue("2022" in str(dir_path))


if __name__ == "__main__":
    unittest.main()
