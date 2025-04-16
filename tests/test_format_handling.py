"""
Testes de processamento de múltiplos formatos.

Este arquivo contém testes que verificam a capacidade do comando sync
de processar diferentes formatos de arquivo (JSON, YAML, CSV, Excel).
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import yaml

from peopleanalytics.cli_commands.sync_commands import DataSync


class TestFormatHandling(unittest.TestCase):
    """Testes para o processamento de múltiplos formatos de arquivo"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        # Criar diretórios temporários
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.output_dir = Path(self.temp_dir) / "output"

        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # Criar uma instância de DataSync
        self.sync = DataSync()
        self.sync.data_dir = self.data_dir
        self.sync.output_dir = self.output_dir
        self.sync.verbose = True  # Facilita depuração
        self.sync.skip_dashboard = True  # Simplifica os testes

        # Criar estrutura de diretórios para testes
        self._create_test_data()

    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir)

    def _create_test_data(self):
        """Cria dados de teste em diferentes formatos"""
        # Dados de base para todos os formatos
        base_data = {
            "success": True,
            "status_code": 200,
            "data": {
                "competencies": [
                    {"name": "Liderança", "score": 4.2},
                    {"name": "Comunicação", "score": 3.8},
                    {"name": "Tomada de Decisão", "score": 4.0},
                    {"name": "Execução", "score": 4.5},
                ],
                "overall_score": 4.1,
            },
        }

        # Criar diretório para JSON
        json_dir = self.data_dir / "JsonTest"
        json_ano_dir = json_dir / "2023"
        json_dir.mkdir(exist_ok=True)
        json_ano_dir.mkdir(exist_ok=True)

        with open(json_ano_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(base_data, f, indent=4)

        # Criar diretório para YAML
        yaml_dir = self.data_dir / "YamlTest"
        yaml_ano_dir = yaml_dir / "2023"
        yaml_dir.mkdir(exist_ok=True)
        yaml_ano_dir.mkdir(exist_ok=True)

        with open(yaml_ano_dir / "resultado.yaml", "w", encoding="utf-8") as f:
            yaml.dump(base_data, f)

        # Criar diretório para CSV
        csv_dir = self.data_dir / "CsvTest"
        csv_ano_dir = csv_dir / "2023"
        csv_dir.mkdir(exist_ok=True)
        csv_ano_dir.mkdir(exist_ok=True)

        # Transformar para DataFrame e salvar como CSV
        competencies = base_data["data"]["competencies"]
        df = pd.DataFrame(competencies)
        df.to_csv(csv_ano_dir / "resultado.csv", index=False)

        # Criar diretório para Excel
        excel_dir = self.data_dir / "ExcelTest"
        excel_ano_dir = excel_dir / "2023"
        excel_dir.mkdir(exist_ok=True)
        excel_ano_dir.mkdir(exist_ok=True)

        # Criar arquivo Excel com múltiplas planilhas
        with pd.ExcelWriter(excel_ano_dir / "resultado.xlsx") as writer:
            df.to_excel(writer, sheet_name="Competências", index=False)

            # Adicionar uma planilha com pontuação geral
            overall_df = pd.DataFrame(
                [
                    {
                        "metric": "overall_score",
                        "value": base_data["data"]["overall_score"],
                    }
                ]
            )
            overall_df.to_excel(writer, sheet_name="Pontuação", index=False)

        # Criar diretório com múltiplos formatos
        multi_dir = self.data_dir / "MultiFormat"
        multi_ano_dir = multi_dir / "2023"
        multi_dir.mkdir(exist_ok=True)
        multi_ano_dir.mkdir(exist_ok=True)

        # Adicionar um arquivo de cada formato
        with open(multi_ano_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(base_data, f, indent=4)

        with open(multi_ano_dir / "resultado.yaml", "w", encoding="utf-8") as f:
            yaml.dump(base_data, f)

        df.to_csv(multi_ano_dir / "resultado.csv", index=False)

        with pd.ExcelWriter(multi_ano_dir / "resultado.xlsx") as writer:
            df.to_excel(writer, sheet_name="Competências", index=False)

    def test_json_processing(self):
        """Testa o processamento de arquivos JSON"""
        # Configurar para processar apenas JSON
        self.sync.selected_formats = "json"
        self.sync.pessoa_filter = "JsonTest"

        # Executar processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)
        self.assertIn("JsonTest/2023", self.sync.processed_directories)

        # Verificar se gerou os relatórios corretos
        reports_dir = self.output_dir / "JsonTest" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())

        # Verificar o conteúdo do relatório individual
        individual_report_path = reports_dir / "individual_report.json"
        self.assertTrue(individual_report_path.exists())

        with open(individual_report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
            self.assertEqual(report_data["pessoa"], "JsonTest")
            self.assertEqual(report_data["ano"], "2023")

    def test_yaml_processing(self):
        """Testa o processamento de arquivos YAML"""
        # Configurar para processar apenas YAML
        self.sync.selected_formats = "yaml"
        self.sync.pessoa_filter = "YamlTest"

        # Executar processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)
        self.assertIn("YamlTest/2023", self.sync.processed_directories)

        # Verificar se gerou os relatórios corretos
        reports_dir = self.output_dir / "YamlTest" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())

    def test_csv_processing(self):
        """Testa o processamento de arquivos CSV"""
        # Configurar para processar apenas CSV
        self.sync.selected_formats = "csv"
        self.sync.pessoa_filter = "CsvTest"

        # Executar processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)
        self.assertIn("CsvTest/2023", self.sync.processed_directories)

        # Verificar se gerou os relatórios corretos
        reports_dir = self.output_dir / "CsvTest" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())

    def test_excel_processing(self):
        """Testa o processamento de arquivos Excel"""
        # Configurar para processar apenas Excel
        self.sync.selected_formats = "excel"
        self.sync.pessoa_filter = "ExcelTest"

        # Executar processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)
        self.assertIn("ExcelTest/2023", self.sync.processed_directories)

        # Verificar se gerou os relatórios corretos
        reports_dir = self.output_dir / "ExcelTest" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())

    def test_multi_format_processing(self):
        """Testa o processamento de múltiplos formatos juntos"""
        # Configurar para processar todos os formatos
        self.sync.selected_formats = "all"
        self.sync.pessoa_filter = "MultiFormat"

        # Executar processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)
        self.assertIn("MultiFormat/2023", self.sync.processed_directories)

        # Verificar se gerou os relatórios corretos
        reports_dir = self.output_dir / "MultiFormat" / "2023" / "reports"
        self.assertTrue(reports_dir.exists())

        # Verificar se combinou dados de diferentes formatos
        summary_report_path = reports_dir / "summary_report.json"
        self.assertTrue(summary_report_path.exists())

        with open(summary_report_path, "r", encoding="utf-8") as f:
            summary_data = json.load(f)
            # Verifica se as métricas existem (devem ter sido combinadas dos diferentes formatos)
            self.assertIn("metrics", summary_data)

    def test_format_filtering(self):
        """Testa o filtro de formatos (processar apenas formatos especificados)"""
        # Configurar para processar apenas JSON e YAML
        self.sync.selected_formats = "json,yaml"
        self.sync.pessoa_filter = "MultiFormat"

        # Executar processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se processou os arquivos relevantes
        with open(
            self.output_dir
            / "MultiFormat"
            / "2023"
            / "reports"
            / "individual_report.json",
            "r",
            encoding="utf-8",
        ) as f:
            report_data = json.load(f)
            # Verifica se os dados JSON foram processados
            self.assertEqual(report_data["data"]["success"], True)

    def test_invalid_format(self):
        """Testa o comportamento com formato inválido"""
        # Configurar com formato inválido
        self.sync.selected_formats = "invalid_format"

        # Executar processamento (não deve quebrar, mas pode falhar)
        result = self.sync.execute()

        # Verificar que não processou nenhum diretório
        self.assertEqual(len(self.sync.processed_directories), 0)


class TestExcelExport(unittest.TestCase):
    """Testes para a exportação para Excel"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        # Criar diretórios temporários
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.output_dir = Path(self.temp_dir) / "output"

        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # Criar dados de teste
        self._create_test_data_for_excel()

        # Criar instância para teste
        self.sync = DataSync()
        self.sync.data_dir = self.data_dir
        self.sync.output_dir = self.output_dir
        self.sync.verbose = True
        self.sync.export_excel = True

    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir)

    def _create_test_data_for_excel(self):
        """Cria dados de teste para teste de exportação para Excel"""
        # Criar alguns diretórios de teste
        for pessoa_idx in range(1, 4):
            pessoa_name = f"Person{pessoa_idx}"
            pessoa_dir = self.data_dir / pessoa_name
            pessoa_dir.mkdir(exist_ok=True)

            for ano in [2022, 2023]:
                ano_dir = pessoa_dir / str(ano)
                ano_dir.mkdir(exist_ok=True)

                # Dados básicos
                resultado_data = {
                    "success": True,
                    "data": {
                        "competencies": [
                            {"name": "Skill1", "score": 3.0 + pessoa_idx * 0.5},
                            {"name": "Skill2", "score": 4.0 - pessoa_idx * 0.2},
                        ],
                        "overall_score": 3.5 + pessoa_idx * 0.1,
                    },
                }

                with open(ano_dir / "resultado.json", "w", encoding="utf-8") as f:
                    json.dump(resultado_data, f, indent=4)

    def test_excel_export(self):
        """Testa se os dados consolidados são exportados para Excel"""
        # Executar com exportação para Excel
        result = self.sync.execute()

        # Verificar se teve sucesso
        self.assertEqual(result, 0)

        # Verificar se o arquivo Excel foi gerado
        consolidated_dir = self.output_dir / "consolidated"
        excel_files = list(consolidated_dir.glob("dados_consolidados_*.xlsx"))

        self.assertGreater(len(excel_files), 0, "Nenhum arquivo Excel foi gerado")

        # Verificar conteúdo do Excel
        excel_path = excel_files[0]

        # Carregar o Excel e verificar as planilhas
        excel_data = pd.read_excel(excel_path, sheet_name=None)

        # Deve ter pelo menos uma planilha Pessoas
        self.assertIn("Pessoas", excel_data)

        # Verificar conteúdo da planilha Pessoas
        pessoas_df = excel_data["Pessoas"]
        self.assertEqual(len(pessoas_df), 6)  # 3 pessoas x 2 anos = 6 linhas

        # Verificar se as métricas foram incluídas
        self.assertTrue(any(col.startswith("metric_") for col in pessoas_df.columns))


if __name__ == "__main__":
    unittest.main()
