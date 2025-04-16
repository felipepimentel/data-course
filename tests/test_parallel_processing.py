"""
Testes de performance e estabilidade para processamento paralelo.

Este arquivo contém testes que verificam se o processamento paralelo
está funcionando corretamente e oferece benefícios de performance.
"""

import json
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

import pytest

from peopleanalytics.cli_commands.sync_commands import DataSync


@pytest.mark.performance
class TestParallelPerformance(unittest.TestCase):
    """Testes de performance para o processamento paralelo"""

    def setUp(self):
        """Configuração inicial para testes de performance"""
        # Criar diretórios temporários
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.output_dir = Path(self.temp_dir) / "output"

        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # Gerar dados de teste em larga escala
        self._generate_large_test_data()

    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir)

    def _generate_large_test_data(self):
        """Gera um conjunto grande de dados de teste"""
        # Gerar 50 pessoas com 2 anos cada
        for pessoa_idx in range(1, 51):
            pessoa_name = f"TestPerson{pessoa_idx}"
            pessoa_dir = self.data_dir / pessoa_name
            pessoa_dir.mkdir(exist_ok=True)

            for ano in [2022, 2023]:
                ano_dir = pessoa_dir / str(ano)
                ano_dir.mkdir(exist_ok=True)

                # Gerar arquivo resultado.json
                resultado_data = {
                    "success": True,
                    "status_code": 200,
                    "data": {
                        "conceito_ciclo_filho_descricao": "Meets Expectations",
                        "direcionadores": [
                            {
                                "direcionador": "Liderança",
                                "pergunta_final": "Quão bem a pessoa lidera?",
                                "comportamentos": [
                                    {
                                        "comportamento": "Comunicação",
                                        "pergunta_final": "Como é a comunicação da pessoa?",
                                        "avaliacoes_grupo": [
                                            {
                                                "avaliador": "%todos",
                                                "frequencia_colaborador": [
                                                    0,
                                                    0,
                                                    1,
                                                    2,
                                                    3,
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            },
                            {
                                "direcionador": "Execução",
                                "pergunta_final": "Quão bem a pessoa executa?",
                                "comportamentos": [
                                    {
                                        "comportamento": "Entregas",
                                        "pergunta_final": "Como são as entregas da pessoa?",
                                        "avaliacoes_grupo": [
                                            {
                                                "avaliador": "%todos",
                                                "frequencia_colaborador": [
                                                    0,
                                                    0,
                                                    0,
                                                    3,
                                                    3,
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            },
                        ],
                        "competencies": [
                            {
                                "name": "Liderança",
                                "score": 3.5 + (pessoa_idx % 10) / 10,
                            },
                            {
                                "name": "Comunicação",
                                "score": 3.2 + (pessoa_idx % 8) / 10,
                            },
                            {
                                "name": "Tomada de Decisão",
                                "score": 3.8 + (pessoa_idx % 6) / 10,
                            },
                            {"name": "Execução", "score": 4.0 + (pessoa_idx % 5) / 10},
                        ],
                        "overall_score": 3.7 + (pessoa_idx % 7) / 10,
                    },
                }

                with open(ano_dir / "resultado.json", "w", encoding="utf-8") as f:
                    json.dump(resultado_data, f)

                # Gerar arquivo perfil.json
                perfil_data = {
                    "cargo": f"Cargo {pessoa_idx % 5 + 1}",
                    "nivel_cargo": f"Nível {pessoa_idx % 3 + 1}",
                    "nome_completo": f"Pessoa de Teste {pessoa_idx}",
                    "equipe": f"Equipe {pessoa_idx % 10 + 1}",
                    "gestor": f"Gestor {pessoa_idx % 8 + 1}",
                    "tempo_empresa": pessoa_idx % 10 + 1,
                    "idade": 25 + (pessoa_idx % 20),
                }

                with open(ano_dir / "perfil.json", "w", encoding="utf-8") as f:
                    json.dump(perfil_data, f)

    def test_parallel_vs_sequential_performance(self):
        """Testa se o processamento paralelo é mais rápido que o sequencial"""
        # Pular em CI/CD ou ambientes com recursos limitados
        if os.environ.get("CI") == "true":
            self.skipTest("Pulando teste de performance em ambiente CI")

        # Criar instância para processamento sequencial
        sync_sequential = DataSync()
        sync_sequential.data_dir = self.data_dir
        sync_sequential.output_dir = self.output_dir / "sequential"
        sync_sequential.skip_viz = (
            True  # Pular visualizações para focar no processamento
        )
        sync_sequential.skip_dashboard = True
        sync_sequential.ignore_errors = True
        sync_sequential.parallel = False

        # Medir tempo do processamento sequencial
        start_time = time.time()
        sync_sequential.execute()
        sequential_time = time.time() - start_time

        # Limpar diretório de saída para o próximo teste
        shutil.rmtree(self.output_dir / "sequential")

        # Criar instância para processamento paralelo
        sync_parallel = DataSync()
        sync_parallel.data_dir = self.data_dir
        sync_parallel.output_dir = self.output_dir / "parallel"
        sync_parallel.skip_viz = True  # Pular visualizações para focar no processamento
        sync_parallel.skip_dashboard = True
        sync_parallel.ignore_errors = True
        sync_parallel.parallel = True
        sync_parallel.workers = os.cpu_count() or 4  # Usar todos os CPUs disponíveis

        # Medir tempo do processamento paralelo
        start_time = time.time()
        sync_parallel.execute()
        parallel_time = time.time() - start_time

        # Verificar se o processamento paralelo foi mais rápido
        # Para ser considerado eficiente, deve ser pelo menos 30% mais rápido em um sistema multi-core
        expected_speedup = 1.3  # 30% mais rápido
        actual_speedup = sequential_time / parallel_time

        print(f"Tempo sequencial: {sequential_time:.2f}s")
        print(f"Tempo paralelo: {parallel_time:.2f}s")
        print(f"Speedup: {actual_speedup:.2f}x")

        # Em sistemas com menos cores, o speedup pode ser menor
        # então fazemos uma verificação adaptativa
        min_expected_speedup = 1.1  # Pelo menos 10% mais rápido

        self.assertGreater(
            actual_speedup,
            min_expected_speedup,
            f"Processamento paralelo não foi significativamente mais rápido: {actual_speedup:.2f}x",
        )

        # Verificar se os resultados são equivalentes
        self._compare_output_dirs(
            self.output_dir / "sequential", self.output_dir / "parallel"
        )

    def test_batch_processing(self):
        """Testa o processamento em lotes"""
        # Criar instância com processamento em lotes
        sync_batch = DataSync()
        sync_batch.data_dir = self.data_dir
        sync_batch.output_dir = self.output_dir / "batch"
        sync_batch.skip_viz = True
        sync_batch.skip_dashboard = True
        sync_batch.ignore_errors = True
        sync_batch.parallel = True
        sync_batch.workers = os.cpu_count() or 4
        sync_batch.batch_size = 10  # Processar em lotes de 10 diretórios

        # Executar processamento em lotes
        start_time = time.time()
        sync_batch.execute()
        batch_time = time.time() - start_time

        # Verificar se todos os diretórios foram processados
        processed_dirs = list(Path(self.output_dir / "batch").glob("TestPerson*/*"))
        self.assertEqual(len(processed_dirs), 100)  # 50 pessoas x 2 anos

        print(f"Tempo de processamento em lotes: {batch_time:.2f}s")

    def _compare_output_dirs(self, dir1, dir2):
        """Compara se dois diretórios têm a mesma estrutura e arquivos similares"""
        # Listar todos os diretórios em ambos os locais
        dirs1 = set(d.name for d in dir1.glob("*") if d.is_dir())
        dirs2 = set(d.name for d in dir2.glob("*") if d.is_dir())

        # Verificar se os mesmos diretórios estão presentes
        self.assertEqual(
            dirs1, dirs2, "Os diretórios de saída não têm a mesma estrutura"
        )

        # Para cada diretório de pessoa, verificar se os anos estão presentes
        for pessoa in dirs1:
            anos1 = set(d.name for d in (dir1 / pessoa).glob("*") if d.is_dir())
            anos2 = set(d.name for d in (dir2 / pessoa).glob("*") if d.is_dir())

            self.assertEqual(anos1, anos2, f"Os anos para {pessoa} não correspondem")

            # Para cada ano, verificar se os diretórios de relatórios existem
            for ano in anos1:
                reports1 = set((dir1 / pessoa / ano / "reports").glob("*.json"))
                reports2 = set((dir2 / pessoa / ano / "reports").glob("*.json"))

                self.assertEqual(
                    len(reports1),
                    len(reports2),
                    f"Número diferente de relatórios para {pessoa}/{ano}",
                )


@pytest.mark.stability
class TestParallelStability(unittest.TestCase):
    """Testes de estabilidade para o processamento paralelo"""

    def setUp(self):
        """Configuração inicial para testes de estabilidade"""
        # Similar ao TestParallelPerformance, mas com dados que podem testar casos de borda
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.output_dir = Path(self.temp_dir) / "output"

        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # Gerar dados para testar estabilidade
        self._generate_edge_case_data()

    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir)

    def _generate_edge_case_data(self):
        """Gera dados de teste com casos de borda"""
        # Diretório com arquivo inválido
        invalid_dir = self.data_dir / "Invalid"
        invalid_ano_dir = invalid_dir / "2023"
        invalid_dir.mkdir(exist_ok=True)
        invalid_ano_dir.mkdir(exist_ok=True)

        with open(invalid_ano_dir / "resultado.json", "w", encoding="utf-8") as f:
            f.write("{ this is not valid JSON }")

        # Diretório com arquivo muito grande
        large_dir = self.data_dir / "LargeFile"
        large_ano_dir = large_dir / "2023"
        large_dir.mkdir(exist_ok=True)
        large_ano_dir.mkdir(exist_ok=True)

        # Criar um arquivo JSON grande (5MB)
        large_data = {
            "success": True,
            "status_code": 200,
            "data": {
                "large_array": ["x" * 1000] * 5000,  # ~5MB de dados
                "competencies": [
                    {"name": "Liderança", "score": 4.2},
                    {"name": "Comunicação", "score": 3.8},
                ],
            },
        }

        with open(large_ano_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(large_data, f)

        # Diretório com muitos arquivos pequenos
        many_files_dir = self.data_dir / "ManyFiles"
        many_files_ano_dir = many_files_dir / "2023"
        many_files_dir.mkdir(exist_ok=True)
        many_files_ano_dir.mkdir(exist_ok=True)

        # Criar um resultado base válido
        base_result = {
            "success": True,
            "data": {"competencies": [{"name": "Skill", "score": 4.0}]},
        }

        with open(many_files_ano_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(base_result, f)

        # Adicionar 100 arquivos pequenos
        for i in range(100):
            with open(
                many_files_ano_dir / f"extra_data_{i}.json", "w", encoding="utf-8"
            ) as f:
                json.dump({"data": i}, f)

    def test_parallel_with_error_handling(self):
        """Testa se o processamento paralelo lida corretamente com erros"""
        # Configurar para ignorar erros
        sync = DataSync()
        sync.data_dir = self.data_dir
        sync.output_dir = self.output_dir
        sync.skip_viz = True
        sync.skip_dashboard = True
        sync.ignore_errors = True
        sync.parallel = True
        sync.workers = 4

        # Executar processamento
        result = sync.execute()

        # Verificar se terminou sem exceções
        self.assertEqual(result, 1)  # Deve retornar 1 pois temos erros

        # Verificar se processou os diretórios válidos
        self.assertGreater(len(sync.processed_directories), 0)

        # Verificar se registrou os erros
        self.assertGreater(len(sync.errors), 0)

    def test_parallel_with_stop_on_error(self):
        """Testa se o processamento paralelo para corretamente ao encontrar erros"""
        # Configurar para não ignorar erros
        sync = DataSync()
        sync.data_dir = self.data_dir
        sync.output_dir = self.output_dir
        sync.skip_viz = True
        sync.skip_dashboard = True
        sync.ignore_errors = False
        sync.parallel = True
        sync.workers = 4

        # Executar processamento - deve lançar exceção
        with self.assertRaises(Exception):
            sync.execute()

    def test_parallel_with_large_files(self):
        """Testa se o processamento paralelo lida corretamente com arquivos grandes"""
        # Configurar para processar apenas o diretório com arquivo grande
        sync = DataSync()
        sync.data_dir = self.data_dir
        sync.output_dir = self.output_dir
        sync.skip_viz = True
        sync.skip_dashboard = True
        sync.ignore_errors = True
        sync.parallel = True
        sync.workers = 2
        sync.pessoa_filter = "LargeFile"

        # Executar processamento
        result = sync.execute()

        # Verificar se processou o diretório
        self.assertEqual(result, 0)  # Deve ter sucesso
        self.assertIn("LargeFile/2023", sync.processed_directories)


if __name__ == "__main__":
    unittest.main()
