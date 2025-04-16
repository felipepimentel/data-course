"""
Testes unitários para o comando sync.

Este módulo contém testes para verificar o funcionamento correto do comando sync
com diferentes opções e formatos de dados.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from peopleanalytics.cli_commands.sync_commands import DataSync, SyncCommand


class TestSyncCommand(unittest.TestCase):
    """Testes para o comando SyncCommand"""

    def test_add_arguments(self):
        """Testa se os argumentos são adicionados corretamente ao parser"""
        parser = MagicMock()
        command = SyncCommand()
        command.add_arguments(parser)

        # Verificar se todos os argumentos esperados foram adicionados
        calls = parser.add_argument.call_args_list
        arg_names = [call[0][0] if call[0] else call[1]["dest"] for call in calls]

        expected_args = [
            "data_dir",
            "output_dir",
            "--reprocess",
            "--skip-viz",
            "--ignore-errors",
            "--compress",
            "--formatos",
            "--pessoa",
            "--ano",
            "--export-excel",
            "--verbose",
        ]

        for arg in expected_args:
            self.assertTrue(
                any(arg in str(call) for call in calls),
                f"Argumento '{arg}' não encontrado nos argumentos do parser",
            )


class TestDataSync(unittest.TestCase):
    """Testes para a classe DataSync"""

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

        # Criar estrutura de testes básica
        self._create_test_structure()

    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir)

    def _create_test_structure(self):
        """Cria estrutura de diretórios e arquivos para testes"""
        # Estrutura:
        # - pessoa1
        #   - 2022
        #     - resultado.json
        #   - 2023
        #     - resultado.json
        # - pessoa2
        #   - 2023
        #     - resultado.json
        #     - resultado.yaml

        # Pessoa 1 - Ano 2022
        pessoa1_dir = self.data_dir / "pessoa1"
        pessoa1_dir.mkdir(exist_ok=True)

        ano_2022_dir = pessoa1_dir / "2022"
        ano_2022_dir.mkdir(exist_ok=True)

        test_data_2022 = {
            "success": True,
            "pessoa": "pessoa1",
            "ano": "2022",
            "data": {
                "competencies": [
                    {"name": "Liderança", "score": 3.2},
                    {"name": "Comunicação", "score": 3.8},
                    {"name": "Inovação", "score": 3.5},
                ],
                "overall_score": 3.5,
                "profile": {
                    "department": "Tecnologia",
                    "position": "Desenvolvedor Pleno",
                    "team": "Alpha",
                },
            },
        }

        with open(ano_2022_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(test_data_2022, f, indent=4)

        # Pessoa 1 - Ano 2023
        ano_2023_dir = pessoa1_dir / "2023"
        ano_2023_dir.mkdir(exist_ok=True)

        test_data_2023 = {
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
            json.dump(test_data_2023, f, indent=4)

        # Pessoa 2 - Ano 2023
        pessoa2_dir = self.data_dir / "pessoa2"
        pessoa2_dir.mkdir(exist_ok=True)

        ano_2023_dir_p2 = pessoa2_dir / "2023"
        ano_2023_dir_p2.mkdir(exist_ok=True)

        test_data_p2 = {
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
                    "department": "Produto",
                    "position": "Product Owner",
                    "team": "Beta",
                },
            },
        }

        # Salvar em JSON
        with open(ano_2023_dir_p2 / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(test_data_p2, f, indent=4)

        # Salvar em YAML também para testar múltiplos formatos
        with open(ano_2023_dir_p2 / "resultado.yaml", "w", encoding="utf-8") as f:
            yaml.dump(test_data_p2, f)

    def test_init_default_values(self):
        """Testa se os valores padrão são configurados corretamente"""
        sync = DataSync()

        # Verificar valores padrão
        self.assertFalse(sync.reprocess)
        self.assertFalse(sync.skip_viz)
        self.assertFalse(sync.ignore_errors)
        self.assertFalse(sync.compress)
        self.assertEqual(sync.selected_formats, "all")
        self.assertIsNone(sync.pessoa_filter)
        self.assertIsNone(sync.ano_filter)
        self.assertFalse(sync.export_excel)
        self.assertFalse(sync.verbose)

    def test_process_pessoa_ano_structure(self):
        """Testa o processamento da estrutura pessoa/ano"""
        # Executar o processamento
        valid_dirs = self.sync._process_pessoa_ano_structure()

        # Verificar que 3 diretórios foram encontrados (pessoa1/2022, pessoa1/2023, pessoa2/2023)
        self.assertEqual(len(valid_dirs), 3)

        # Verificar que os diretórios corretos foram encontrados
        expected_dirs = [
            self.data_dir / "pessoa1" / "2022",
            self.data_dir / "pessoa1" / "2023",
            self.data_dir / "pessoa2" / "2023",
        ]

        for expected_dir in expected_dirs:
            self.assertIn(expected_dir, valid_dirs)

    def test_process_pessoa_ano_structure_with_filters(self):
        """Testa o processamento da estrutura pessoa/ano com filtros aplicados"""
        # Configurar filtros
        self.sync.pessoa_filter = "pessoa1"
        self.sync.ano_filter = "2023"

        # Executar o processamento
        valid_dirs = self.sync._process_pessoa_ano_structure()

        # Verificar que apenas 1 diretório foi encontrado (pessoa1/2023)
        self.assertEqual(len(valid_dirs), 1)
        self.assertEqual(valid_dirs[0], self.data_dir / "pessoa1" / "2023")

        # Resetar filtros
        self.sync.pessoa_filter = None
        self.sync.ano_filter = "2022"

        # Executar o processamento
        valid_dirs = self.sync._process_pessoa_ano_structure()

        # Verificar que apenas pessoa1/2022 foi encontrado
        self.assertEqual(len(valid_dirs), 1)
        self.assertEqual(valid_dirs[0], self.data_dir / "pessoa1" / "2022")

    def test_format_filtering(self):
        """Testa o filtro de formatos de arquivo"""
        # Configurar filtro de formato para apenas JSON
        self.sync.selected_formats = "json"

        # Processar os arquivos
        result = self.sync.execute()

        # Verificar que o processamento foi bem-sucedido
        self.assertEqual(result, 0)

        # Verificar que os arquivos de saída foram criados (para cada entrada JSON)
        output_files = list(self.output_dir.glob("**/*.html"))
        self.assertGreaterEqual(
            len(output_files), 3
        )  # Pelo menos 3 relatórios (1 por arquivo JSON)

        # Limpar diretório de saída
        shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Configurar filtro de formato para apenas YAML
        self.sync.selected_formats = "yaml"

        # Processar os arquivos
        result = self.sync.execute()

        # Verificar que o processamento foi bem-sucedido
        self.assertEqual(result, 0)

        # Verificar que os arquivos de saída foram criados (para cada entrada YAML)
        output_files = list(self.output_dir.glob("**/*.html"))
        self.assertGreaterEqual(
            len(output_files), 1
        )  # Pelo menos 1 relatório (1 arquivo YAML)

    def test_skip_visualization(self):
        """Testa a opção de pular visualizações"""
        # Configurar para pular visualizações
        self.sync.skip_viz = True

        # Processar os arquivos
        result = self.sync.execute()

        # Verificar que o processamento foi bem-sucedido
        self.assertEqual(result, 0)

        # Verificar que os relatórios foram criados
        reports = list(self.output_dir.glob("**/report_*.html"))
        self.assertGreaterEqual(len(reports), 3)

        # Verificar que as visualizações não foram criadas
        viz_files = list(self.output_dir.glob("**/radar_*.html")) + list(
            self.output_dir.glob("**/heatmap_*.html")
        )
        self.assertEqual(len(viz_files), 0)

    def test_ignore_errors(self):
        """Testa a opção de ignorar erros"""
        # Criar um arquivo JSON inválido
        invalid_dir = self.data_dir / "pessoa_invalida" / "2023"
        invalid_dir.mkdir(parents=True, exist_ok=True)

        with open(invalid_dir / "resultado.json", "w", encoding="utf-8") as f:
            f.write("{invalid json")

        # Processar com a opção ignore_errors desativada
        self.sync.ignore_errors = False

        # O processamento deve falhar devido ao arquivo inválido
        with self.assertRaises(Exception):
            self.sync.execute()

        # Ativar a opção ignore_errors
        self.sync.ignore_errors = True

        # Agora o processamento deve concluir com sucesso apesar do erro
        result = self.sync.execute()
        self.assertEqual(result, 0)

    def test_consolidation(self):
        """Testa a criação da dashboard de consolidação"""
        # Processar os arquivos
        result = self.sync.execute()

        # Verificar que o processamento foi bem-sucedido
        self.assertEqual(result, 0)

        # Verificar que o arquivo de dashboard foi criado
        dashboard_file = self.output_dir / "consolidacao" / "dashboard.html"
        self.assertTrue(dashboard_file.exists())

        # Verificar o conteúdo do dashboard
        with open(dashboard_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Dashboard deve conter referências às pessoas
        self.assertIn("pessoa1", content)
        self.assertIn("pessoa2", content)

        # Dashboard deve conter referências aos anos
        self.assertIn("2022", content)
        self.assertIn("2023", content)

    def test_reprocess_option(self):
        """Testa a opção de reprocessamento"""
        # Primeiro processamento
        result = self.sync.execute()
        self.assertEqual(result, 0)

        # Obter data de modificação dos arquivos
        initial_files = list(self.output_dir.glob("**/*.html"))
        initial_mtimes = {str(file): file.stat().st_mtime for file in initial_files}

        # Aguardar um pouco para garantir timestamps diferentes
        import time

        time.sleep(1)

        # Segundo processamento sem reprocess
        self.sync.reprocess = False
        result = self.sync.execute()
        self.assertEqual(result, 0)

        # Verificar que os arquivos não foram modificados
        for file in initial_files:
            current_mtime = file.stat().st_mtime
            self.assertEqual(current_mtime, initial_mtimes[str(file)])

        # Terceiro processamento com reprocess
        self.sync.reprocess = True
        result = self.sync.execute()
        self.assertEqual(result, 0)

        # Verificar que os arquivos foram modificados
        for file in initial_files:
            current_mtime = file.stat().st_mtime
            self.assertGreater(current_mtime, initial_mtimes[str(file)])

    def test_multiple_formats_same_directory(self):
        """Testa o processamento de múltiplos formatos no mesmo diretório"""
        # A pessoa2 tem tanto JSON quanto YAML
        self.sync.pessoa_filter = "pessoa2"

        # Processar todos os formatos
        self.sync.selected_formats = "all"
        result = self.sync.execute()
        self.assertEqual(result, 0)

        # Verificar que ambos os formatos foram processados
        reports = list((self.output_dir / "pessoa2").glob("**/report_*.html"))
        self.assertEqual(len(reports), 2)  # Um para JSON e um para YAML

    def test_command_execution(self):
        """Testa o fluxo completo do comando"""
        # Criar argumentos simulados
        args = MagicMock()
        args.data_dir = self.data_dir
        args.output_dir = self.output_dir
        args.reprocess = True
        args.skip_viz = False
        args.ignore_errors = True
        args.compress = False
        args.formatos = "all"
        args.pessoa = None
        args.ano = None
        args.export_excel = True
        args.verbose = True

        # Criar e executar o comando
        command = SyncCommand()
        with patch("builtins.print") as mock_print:
            result = command.execute(args)

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar se os parâmetros foram passados corretamente para DataSync
        self.assertTrue(command.sync.reprocess)
        self.assertFalse(command.sync.skip_viz)
        self.assertTrue(command.sync.ignore_errors)
        self.assertFalse(command.sync.compress)
        self.assertEqual(command.sync.selected_formats, "all")
        self.assertIsNone(command.sync.pessoa_filter)
        self.assertIsNone(command.sync.ano_filter)
        self.assertTrue(command.sync.export_excel)
        self.assertTrue(command.sync.verbose)

        # Verificar que o arquivo de dashboard foi criado
        dashboard_file = self.output_dir / "consolidacao" / "dashboard.html"
        self.assertTrue(dashboard_file.exists())

        # Se export_excel está ativo, verificar que o Excel foi criado
        excel_files = list((self.output_dir / "consolidacao").glob("*.xlsx"))
        self.assertEqual(len(excel_files), 1)


if __name__ == "__main__":
    unittest.main()
