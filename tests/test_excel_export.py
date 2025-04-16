"""
Testes para a funcionalidade de exportação para Excel.

Este arquivo contém testes para verificar o funcionamento correto
da exportação de dados consolidados para Excel implementado no comando sync.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from peopleanalytics.cli_commands.sync_commands import DataSync


class TestExcelExport(unittest.TestCase):
    """Testes para a funcionalidade de exportação para Excel"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        # Criar diretórios temporários
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.output_dir = Path(self.temp_dir) / "output"

        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # Estrutura de dados para os testes
        self._create_test_directory_structure()

        # Criar instância de DataSync
        self.sync = DataSync()
        self.sync.data_dir = self.data_dir
        self.sync.output_dir = self.output_dir
        self.sync.verbose = True  # Facilita depuração

    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir)

    def _create_test_directory_structure(self):
        """Cria uma estrutura de diretórios e arquivos para os testes"""
        # Estrutura:
        # - pessoa1
        #   - 2023
        #     - resultado.json
        # - pessoa2
        #   - 2023
        #     - resultado.json

        # Pessoa 1 - Ano 2023
        pessoa1_dir = self.data_dir / "pessoa1"
        pessoa1_dir.mkdir(exist_ok=True)

        ano_2023_dir = pessoa1_dir / "2023"
        ano_2023_dir.mkdir(exist_ok=True)

        test_data = {
            "success": True,
            "pessoa": "pessoa1",
            "ano": "2023",
            "data": {
                "competencies": [
                    {"name": "Liderança", "score": 3.5},
                    {"name": "Comunicação", "score": 4.0},
                    {"name": "Inovação", "score": 3.8},
                ],
                "overall_score": 3.77,
                "profile": {
                    "department": "Tecnologia",
                    "position": "Desenvolvedor Senior",
                    "team": "Alpha",
                },
            },
        }

        with open(ano_2023_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(test_data, f, indent=4)

        # Pessoa 2 - Ano 2023
        pessoa2_dir = self.data_dir / "pessoa2"
        pessoa2_dir.mkdir(exist_ok=True)

        ano_2023_dir = pessoa2_dir / "2023"
        ano_2023_dir.mkdir(exist_ok=True)

        test_data = {
            "success": True,
            "pessoa": "pessoa2",
            "ano": "2023",
            "data": {
                "competencies": [
                    {"name": "Liderança", "score": 4.2},
                    {"name": "Comunicação", "score": 3.9},
                    {"name": "Inovação", "score": 4.5},
                ],
                "overall_score": 4.2,
                "profile": {
                    "department": "Tecnologia",
                    "position": "Arquiteto de Software",
                    "team": "Beta",
                },
            },
        }

        with open(ano_2023_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(test_data, f, indent=4)

    def _find_excel_file(self):
        """Encontra o arquivo Excel exportado na pasta de consolidação"""
        consolidation_dir = self.output_dir / "consolidacao"
        if not consolidation_dir.exists():
            return None

        excel_files = list(consolidation_dir.glob("*.xlsx"))
        if excel_files:
            return excel_files[0]

        return None

    def test_export_excel_enabled(self):
        """Testa se a opção de exportação para Excel funciona corretamente"""
        # Habilitar exportação para Excel
        self.sync.export_excel = True

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se o arquivo Excel foi criado
        excel_file = self._find_excel_file()
        self.assertIsNotNone(excel_file, "Arquivo Excel não foi criado")

        # Verificar se o arquivo pode ser lido como um DataFrame
        try:
            df_pessoas = pd.read_excel(excel_file, sheet_name="Pessoas")
            self.assertGreater(len(df_pessoas), 0, "A planilha 'Pessoas' está vazia")

            # Verificar se contém as duas pessoas do teste
            pessoas = df_pessoas["pessoa"].values
            self.assertIn("pessoa1", pessoas)
            self.assertIn("pessoa2", pessoas)

            # Verificar se as competências estão presentes
            self.assertIn("Liderança", df_pessoas.columns)
            self.assertIn("Comunicação", df_pessoas.columns)
            self.assertIn("Inovação", df_pessoas.columns)

        except Exception as e:
            self.fail(f"Não foi possível ler o arquivo Excel: {str(e)}")

    def test_export_excel_disabled(self):
        """Testa se a opção de exportação para Excel está desabilitada por padrão"""
        # Não habilitar exportação para Excel (padrão)
        self.sync.export_excel = False

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se o arquivo Excel NÃO foi criado
        excel_file = self._find_excel_file()
        self.assertIsNone(
            excel_file, "Arquivo Excel foi criado mesmo com a opção desabilitada"
        )

    def test_export_excel_with_filters(self):
        """Testa exportação para Excel com filtros"""
        # Habilitar exportação para Excel e filtrar por pessoa
        self.sync.export_excel = True
        self.sync.pessoa_filter = "pessoa1"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se o arquivo Excel foi criado
        excel_file = self._find_excel_file()
        self.assertIsNotNone(excel_file, "Arquivo Excel não foi criado")

        # Verificar se o arquivo contém apenas dados da pessoa1
        try:
            df_pessoas = pd.read_excel(excel_file, sheet_name="Pessoas")
            self.assertEqual(
                len(df_pessoas), 1, "A planilha 'Pessoas' deve conter apenas uma pessoa"
            )
            self.assertEqual(df_pessoas["pessoa"].values[0], "pessoa1")
            self.assertNotIn("pessoa2", df_pessoas["pessoa"].values)

        except Exception as e:
            self.fail(f"Não foi possível ler o arquivo Excel: {str(e)}")

    def test_excel_file_structure(self):
        """Testa a estrutura do arquivo Excel exportado"""
        # Habilitar exportação para Excel
        self.sync.export_excel = True

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se o arquivo Excel foi criado
        excel_file = self._find_excel_file()
        self.assertIsNotNone(excel_file, "Arquivo Excel não foi criado")

        # Verificar a estrutura do arquivo
        try:
            # Verificar se as planilhas esperadas estão presentes
            excel = pd.ExcelFile(excel_file)
            sheet_names = excel.sheet_names

            # Deve ter ao menos a planilha "Pessoas"
            self.assertIn(
                "Pessoas",
                sheet_names,
                "A planilha 'Pessoas' não está presente no arquivo Excel",
            )

            # Verificar a estrutura da planilha Pessoas
            df_pessoas = excel.parse("Pessoas")
            expected_columns = [
                "pessoa",
                "ano",
                "department",
                "position",
                "team",
                "overall_score",
                "Liderança",
                "Comunicação",
                "Inovação",
            ]

            for col in expected_columns:
                self.assertIn(
                    col,
                    df_pessoas.columns,
                    f"A coluna '{col}' não está presente na planilha 'Pessoas'",
                )

            # Verificar se há dados para ambas as pessoas
            self.assertEqual(
                len(df_pessoas), 2, "A planilha 'Pessoas' deve conter duas linhas"
            )

        except Exception as e:
            self.fail(f"Erro ao verificar a estrutura do arquivo Excel: {str(e)}")


if __name__ == "__main__":
    unittest.main()
