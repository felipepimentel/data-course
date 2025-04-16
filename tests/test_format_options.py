"""
Testes de processamento de diferentes formatos de arquivo.

Este arquivo contém testes para verificar a funcionalidade de processamento
de vários formatos (JSON, YAML, CSV, Excel) implementados no comando sync.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import yaml

from peopleanalytics.cli_commands.sync_commands import DataSync


class TestFormatOptions(unittest.TestCase):
    """Testes para as opções de formato de arquivo"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        # Criar diretórios temporários
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.output_dir = Path(self.temp_dir) / "output"

        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # Criar instância de DataSync
        self.sync = DataSync()
        self.sync.data_dir = self.data_dir
        self.sync.output_dir = self.output_dir
        self.sync.verbose = True  # Facilita depuração
        self.sync.skip_dashboard = True  # Simplifica os testes

    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir)

    def _create_test_directory_structure_with_format(self, format_type="json"):
        """
        Cria uma estrutura de diretórios/arquivos para testar formatos específicos

        Args:
            format_type (str): Tipo de formato a ser criado (json, yaml, csv, excel)
        """
        # Criar estrutura básica
        pessoa_dir = self.data_dir / "pessoa1"
        pessoa_dir.mkdir(exist_ok=True)

        ano_dir = pessoa_dir / "2023"
        ano_dir.mkdir(exist_ok=True)

        # Dados de exemplo
        test_data = {
            "success": True,
            "pessoa": "pessoa1",
            "ano": "2023",
            "data": {
                "competencies": [
                    {"name": "Competência1", "score": 3.5},
                    {"name": "Competência2", "score": 4.0},
                ],
                "overall_score": 3.75,
            },
        }

        # Salvar no formato apropriado
        if format_type == "json":
            with open(ano_dir / "resultado.json", "w", encoding="utf-8") as f:
                json.dump(test_data, f, indent=4)

        elif format_type == "yaml":
            with open(ano_dir / "resultado.yaml", "w", encoding="utf-8") as f:
                yaml.dump(test_data, f)

        elif format_type == "csv":
            # Para CSV, precisamos estruturar os dados de forma tabular
            df = pd.DataFrame(
                [
                    {
                        "competency": "Competência1",
                        "score": 3.5,
                        "pessoa": "pessoa1",
                        "ano": "2023",
                    },
                    {
                        "competency": "Competência2",
                        "score": 4.0,
                        "pessoa": "pessoa1",
                        "ano": "2023",
                    },
                ]
            )
            df.to_csv(ano_dir / "resultado.csv", index=False)

        elif format_type == "excel":
            # Similar ao CSV, mas em Excel
            df = pd.DataFrame(
                [
                    {
                        "competency": "Competência1",
                        "score": 3.5,
                        "pessoa": "pessoa1",
                        "ano": "2023",
                    },
                    {
                        "competency": "Competência2",
                        "score": 4.0,
                        "pessoa": "pessoa1",
                        "ano": "2023",
                    },
                ]
            )
            df.to_excel(ano_dir / "resultado.xlsx", index=False)

    def test_process_json_format(self):
        """Testa o processamento de arquivos no formato JSON"""
        # Criar estrutura com arquivo JSON
        self._create_test_directory_structure_with_format("json")

        # Configurar para processar apenas JSON
        self.sync.selected_formats = "json"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se o diretório foi processado
        self.assertIn("pessoa1/2023", self.sync.processed_directories)

        # Verificar se os relatórios foram gerados
        reports_dir = self.output_dir / "pessoa1" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())
        self.assertTrue((reports_dir / "individual_report.json").exists())

    def test_process_yaml_format(self):
        """Testa o processamento de arquivos no formato YAML"""
        # Criar estrutura com arquivo YAML
        self._create_test_directory_structure_with_format("yaml")

        # Configurar para processar apenas YAML
        self.sync.selected_formats = "yaml"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se o diretório foi processado
        self.assertIn("pessoa1/2023", self.sync.processed_directories)

        # Verificar se os relatórios foram gerados
        reports_dir = self.output_dir / "pessoa1" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())
        self.assertTrue((reports_dir / "individual_report.json").exists())

    def test_process_csv_format(self):
        """Testa o processamento de arquivos no formato CSV"""
        # Criar estrutura com arquivo CSV
        self._create_test_directory_structure_with_format("csv")

        # Configurar para processar apenas CSV
        self.sync.selected_formats = "csv"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se o diretório foi processado
        self.assertIn("pessoa1/2023", self.sync.processed_directories)

        # Verificar se os relatórios foram gerados
        reports_dir = self.output_dir / "pessoa1" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())
        self.assertTrue((reports_dir / "individual_report.json").exists())

    def test_process_excel_format(self):
        """Testa o processamento de arquivos no formato Excel"""
        # Criar estrutura com arquivo Excel
        self._create_test_directory_structure_with_format("excel")

        # Configurar para processar apenas Excel
        self.sync.selected_formats = "excel"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se o diretório foi processado
        self.assertIn("pessoa1/2023", self.sync.processed_directories)

        # Verificar se os relatórios foram gerados
        reports_dir = self.output_dir / "pessoa1" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())
        self.assertTrue((reports_dir / "individual_report.json").exists())

    def test_process_multiple_formats(self):
        """Testa o processamento de múltiplos formatos ao mesmo tempo"""
        # Criar estrutura com diferentes formatos
        # Pessoa 1 com JSON
        pessoa1_dir = self.data_dir / "pessoa1"
        pessoa1_dir.mkdir(exist_ok=True)
        ano1_dir = pessoa1_dir / "2023"
        ano1_dir.mkdir(exist_ok=True)

        # Pessoa 2 com YAML
        pessoa2_dir = self.data_dir / "pessoa2"
        pessoa2_dir.mkdir(exist_ok=True)
        ano2_dir = pessoa2_dir / "2023"
        ano2_dir.mkdir(exist_ok=True)

        # Dados para cada pessoa
        data1 = {
            "success": True,
            "pessoa": "pessoa1",
            "ano": "2023",
            "data": {
                "competencies": [{"name": "Competência1", "score": 3.5}],
                "overall_score": 3.5,
            },
        }

        data2 = {
            "success": True,
            "pessoa": "pessoa2",
            "ano": "2023",
            "data": {
                "competencies": [{"name": "Competência1", "score": 4.0}],
                "overall_score": 4.0,
            },
        }

        # Salvar nos formatos respectivos
        with open(ano1_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(data1, f, indent=4)

        with open(ano2_dir / "resultado.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data2, f)

        # Configurar para processar JSON e YAML
        self.sync.selected_formats = "json,yaml"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se ambos os diretórios foram processados
        self.assertIn("pessoa1/2023", self.sync.processed_directories)
        self.assertIn("pessoa2/2023", self.sync.processed_directories)

        # Verificar se os relatórios foram gerados para ambos
        reports_dir1 = self.output_dir / "pessoa1" / "2023" / "reports"
        reports_dir2 = self.output_dir / "pessoa2" / "2023" / "reports"

        self.assertTrue(reports_dir1.exists())
        self.assertTrue(reports_dir2.exists())

        self.assertTrue((reports_dir1 / "individual_report.json").exists())
        self.assertTrue((reports_dir2 / "individual_report.json").exists())

    def test_filter_formats_with_all_option(self):
        """Testa a opção 'all' para processar todos os formatos"""
        # Criar estrutura com diferentes formatos
        # Pessoa 1 com JSON
        pessoa1_dir = self.data_dir / "pessoa1"
        pessoa1_dir.mkdir(exist_ok=True)
        ano1_dir = pessoa1_dir / "2023"
        ano1_dir.mkdir(exist_ok=True)

        # Pessoa 2 com YAML
        pessoa2_dir = self.data_dir / "pessoa2"
        pessoa2_dir.mkdir(exist_ok=True)
        ano2_dir = pessoa2_dir / "2023"
        ano2_dir.mkdir(exist_ok=True)

        # Dados para cada pessoa
        data1 = {
            "success": True,
            "pessoa": "pessoa1",
            "ano": "2023",
            "data": {
                "competencies": [{"name": "Competência1", "score": 3.5}],
                "overall_score": 3.5,
            },
        }

        data2 = {
            "success": True,
            "pessoa": "pessoa2",
            "ano": "2023",
            "data": {
                "competencies": [{"name": "Competência1", "score": 4.0}],
                "overall_score": 4.0,
            },
        }

        # Salvar nos formatos respectivos
        with open(ano1_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(data1, f, indent=4)

        with open(ano2_dir / "resultado.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data2, f)

        # Configurar para processar todos os formatos
        self.sync.selected_formats = "all"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se ambos os diretórios foram processados
        self.assertIn("pessoa1/2023", self.sync.processed_directories)
        self.assertIn("pessoa2/2023", self.sync.processed_directories)

        # Verificar se os relatórios foram gerados para ambos
        reports_dir1 = self.output_dir / "pessoa1" / "2023" / "reports"
        reports_dir2 = self.output_dir / "pessoa2" / "2023" / "reports"

        self.assertTrue(reports_dir1.exists())
        self.assertTrue(reports_dir2.exists())

    def test_invalid_format_filter(self):
        """Testa o comportamento com um filtro de formato inválido"""
        # Criar estrutura com arquivo JSON
        self._create_test_directory_structure_with_format("json")

        # Configurar para processar um formato inexistente
        self.sync.selected_formats = "invalid_format"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado (deve completar sem erro, mas sem processar nada)
        self.assertEqual(result, 0)

        # Verificar que nenhum diretório foi processado
        self.assertEqual(len(self.sync.processed_directories), 0)

    def test_mixed_valid_invalid_formats(self):
        """Testa o processamento com uma mistura de formatos válidos e inválidos"""
        # Criar estrutura com arquivo JSON
        self._create_test_directory_structure_with_format("json")

        # Configurar para processar JSON e um formato inválido
        self.sync.selected_formats = "json,invalid_format"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se o diretório com JSON foi processado
        self.assertIn("pessoa1/2023", self.sync.processed_directories)

        # Verificar se os relatórios foram gerados
        reports_dir = self.output_dir / "pessoa1" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())


if __name__ == "__main__":
    unittest.main()
