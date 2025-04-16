"""
Testes para as funcionalidades de filtro por pessoa e ano.

Este arquivo contém testes para verificar o funcionamento correto
dos filtros pessoa e ano implementados no comando sync.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from peopleanalytics.cli_commands.sync_commands import DataSync


class TestFilterOptions(unittest.TestCase):
    """Testes para as funcionalidades de filtro por pessoa e ano"""

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
        #   - 2022
        #     - resultado.json
        #   - 2023
        #     - resultado.json
        # - pessoa2
        #   - 2023
        #     - resultado.json
        # - pessoa1_sobrenome
        #   - 2023
        #     - resultado.json

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
                    {"name": "Liderança", "score": 3.0},
                    {"name": "Comunicação", "score": 3.5},
                    {"name": "Inovação", "score": 3.2},
                ],
                "overall_score": 3.23,
                "profile": {
                    "department": "Tecnologia",
                    "position": "Desenvolvedor",
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
                    "team": "Alpha",
                },
            },
        }

        with open(ano_2023_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(test_data, f, indent=4)

        # Pessoa com nome similar - Ano 2023
        pessoa_similar_dir = self.data_dir / "pessoa1_sobrenome"
        pessoa_similar_dir.mkdir(exist_ok=True)

        ano_2023_dir = pessoa_similar_dir / "2023"
        ano_2023_dir.mkdir(exist_ok=True)

        test_data = {
            "success": True,
            "pessoa": "pessoa1_sobrenome",
            "ano": "2023",
            "data": {
                "competencies": [
                    {"name": "Liderança", "score": 3.8},
                    {"name": "Comunicação", "score": 4.1},
                    {"name": "Inovação", "score": 3.9},
                ],
                "overall_score": 3.93,
                "profile": {
                    "department": "Tecnologia",
                    "position": "Desenvolvedor Senior",
                    "team": "Beta",
                },
            },
        }

        with open(ano_2023_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(test_data, f, indent=4)

    def _count_report_files(self, pessoa=None, ano=None):
        """Conta o número de arquivos de relatório gerados"""
        count = 0
        base_path = self.output_dir

        if pessoa and ano:
            # Pasta específica para pessoa e ano
            report_path = base_path / pessoa / ano / "reports"
            if report_path.exists():
                count += len(list(report_path.glob("*.html")))
        elif pessoa:
            # Todas as pastas para uma pessoa
            for year_dir in (base_path / pessoa).glob("*"):
                if year_dir.is_dir():
                    report_path = year_dir / "reports"
                    if report_path.exists():
                        count += len(list(report_path.glob("*.html")))
        elif ano:
            # Todas as pastas para um ano específico
            for person_dir in base_path.glob("*"):
                if person_dir.is_dir():
                    year_path = person_dir / ano
                    if year_path.exists() and year_path.is_dir():
                        report_path = year_path / "reports"
                        if report_path.exists():
                            count += len(list(report_path.glob("*.html")))
        else:
            # Contar todos os relatórios
            for person_dir in base_path.glob("*"):
                if person_dir.is_dir() and person_dir.name != "consolidacao":
                    for year_dir in person_dir.glob("*"):
                        if year_dir.is_dir():
                            report_path = year_dir / "reports"
                            if report_path.exists():
                                count += len(list(report_path.glob("*.html")))

        return count

    def test_without_filters(self):
        """Testa processamento sem filtros (todos os diretórios são processados)"""
        # Configurar sem filtros
        self.sync.pessoa_filter = None
        self.sync.ano_filter = None

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar que todos os diretórios foram processados
        # Esperamos 4 diretórios de resultados: pessoa1/2022, pessoa1/2023, pessoa2/2023, pessoa1_sobrenome/2023
        self.assertGreater(self._count_report_files(), 0)

        # Verificar que pessoa1 tem relatórios para 2022 e 2023
        self.assertGreater(self._count_report_files(pessoa="pessoa1", ano="2022"), 0)
        self.assertGreater(self._count_report_files(pessoa="pessoa1", ano="2023"), 0)

        # Verificar que pessoa2 tem relatórios para 2023
        self.assertGreater(self._count_report_files(pessoa="pessoa2", ano="2023"), 0)

        # Verificar que pessoa1_sobrenome tem relatórios para 2023
        self.assertGreater(
            self._count_report_files(pessoa="pessoa1_sobrenome", ano="2023"), 0
        )

    def test_filter_by_pessoa(self):
        """Testa filtro por pessoa"""
        # Configurar filtro para pessoa1
        self.sync.pessoa_filter = "pessoa1"
        self.sync.ano_filter = None

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar que apenas os diretórios de pessoa1 foram processados
        self.assertGreater(self._count_report_files(pessoa="pessoa1"), 0)

        # Verificar que pessoa1 tem relatórios para 2022 e 2023
        self.assertGreater(self._count_report_files(pessoa="pessoa1", ano="2022"), 0)
        self.assertGreater(self._count_report_files(pessoa="pessoa1", ano="2023"), 0)

        # Verificar que pessoa2 não tem relatórios
        self.assertEqual(self._count_report_files(pessoa="pessoa2"), 0)

        # Verificar que pessoa1_sobrenome não tem relatórios
        self.assertEqual(self._count_report_files(pessoa="pessoa1_sobrenome"), 0)

    def test_filter_by_ano(self):
        """Testa filtro por ano"""
        # Configurar filtro para 2023
        self.sync.pessoa_filter = None
        self.sync.ano_filter = "2023"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar que todos os diretórios de 2023 foram processados
        self.assertGreater(self._count_report_files(ano="2023"), 0)

        # Verificar que pessoa1 tem relatórios apenas para 2023
        self.assertEqual(self._count_report_files(pessoa="pessoa1", ano="2022"), 0)
        self.assertGreater(self._count_report_files(pessoa="pessoa1", ano="2023"), 0)

        # Verificar que pessoa2 tem relatórios para 2023
        self.assertGreater(self._count_report_files(pessoa="pessoa2", ano="2023"), 0)

        # Verificar que pessoa1_sobrenome tem relatórios para 2023
        self.assertGreater(
            self._count_report_files(pessoa="pessoa1_sobrenome", ano="2023"), 0
        )

    def test_filter_by_pessoa_and_ano(self):
        """Testa filtro por pessoa e ano simultaneamente"""
        # Configurar filtro para pessoa1 e 2023
        self.sync.pessoa_filter = "pessoa1"
        self.sync.ano_filter = "2023"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar que apenas o diretório pessoa1/2023 foi processado
        self.assertGreater(self._count_report_files(pessoa="pessoa1", ano="2023"), 0)

        # Verificar que pessoa1 não tem relatórios para 2022
        self.assertEqual(self._count_report_files(pessoa="pessoa1", ano="2022"), 0)

        # Verificar que pessoa2 não tem relatórios para 2023
        self.assertEqual(self._count_report_files(pessoa="pessoa2", ano="2023"), 0)

        # Verificar que pessoa1_sobrenome não tem relatórios para 2023
        self.assertEqual(
            self._count_report_files(pessoa="pessoa1_sobrenome", ano="2023"), 0
        )

    def test_non_existent_pessoa_filter(self):
        """Testa filtro com pessoa inexistente"""
        # Configurar filtro para pessoa inexistente
        self.sync.pessoa_filter = "pessoa_que_nao_existe"
        self.sync.ano_filter = None

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado - o processamento deve ser concluído sem erros
        self.assertEqual(result, 0)

        # Verificar que nenhum relatório foi gerado
        self.assertEqual(self._count_report_files(), 0)

    def test_non_existent_ano_filter(self):
        """Testa filtro com ano inexistente"""
        # Configurar filtro para ano inexistente
        self.sync.pessoa_filter = None
        self.sync.ano_filter = "2024"

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado - o processamento deve ser concluído sem erros
        self.assertEqual(result, 0)

        # Verificar que nenhum relatório foi gerado
        self.assertEqual(self._count_report_files(), 0)

    def test_exact_pessoa_match(self):
        """Testa que o filtro pessoa faz correspondência exata"""
        # Configurar filtro para verificar correspondência exata
        self.sync.pessoa_filter = "pessoa1"
        self.sync.ano_filter = None

        # Executar o processamento
        result = self.sync.execute()

        # Verificar resultado
        self.assertEqual(result, 0)

        # Verificar que pessoa1 tem relatórios
        self.assertGreater(self._count_report_files(pessoa="pessoa1"), 0)

        # Verificar que pessoa1_sobrenome (que contém "pessoa1" em seu nome) não tem relatórios
        self.assertEqual(self._count_report_files(pessoa="pessoa1_sobrenome"), 0)


if __name__ == "__main__":
    unittest.main()
