"""
Testes para a solução DuckDB.
"""

import os
import json
import shutil
import unittest
from pathlib import Path
from datetime import datetime
from duckdb_solution import DuckDBAnalyzer

class TestDuckDBAnalyzer(unittest.TestCase):
    """Testes para o DuckDBAnalyzer."""
    
    def setUp(self):
        """Configuração dos testes."""
        # Criar diretórios temporários para teste
        self.test_data_dir = Path("test_data")
        self.test_output_dir = Path("test_output")
        self.test_db_path = "test_analytics.duckdb"
        
        # Limpar diretórios se existirem
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)
        if Path(self.test_db_path).exists():
            os.remove(self.test_db_path)
            
        # Criar diretórios
        self.test_data_dir.mkdir()
        self.test_output_dir.mkdir()
        
        # Criar dados de teste
        self._create_test_data()
        
        # Inicializar analisador
        self.analyzer = DuckDBAnalyzer(
            data_dir=str(self.test_data_dir),
            output_dir=str(self.test_output_dir),
            db_path=self.test_db_path
        )
    
    def tearDown(self):
        """Limpeza após os testes."""
        # Fechar conexão com o banco
        if hasattr(self, 'analyzer'):
            self.analyzer.conn.close()
            
        # Remover diretórios e arquivos de teste
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)
        if Path(self.test_db_path).exists():
            os.remove(self.test_db_path)
    
    def _create_test_data(self):
        """Cria dados de teste."""
        # Criar estrutura para uma pessoa
        person_dir = self.test_data_dir / "Test Person" / "2023"
        person_dir.mkdir(parents=True)
        
        # Criar arquivo resultado.json (formato legado)
        resultado_data = {
            "nome": "Test Person",
            "ano": 2023,
            "frequencias": [
                {
                    "data": "2023-01-01",
                    "status": "presente",
                    "justificativa": ""
                },
                {
                    "data": "2023-01-02",
                    "status": "ausente",
                    "justificativa": "Feriado"
                }
            ],
            "pagamentos": [
                {
                    "data": "2023-01-15",
                    "valor": 1000,
                    "descricao": "Pagamento 1"
                },
                {
                    "data": "2023-02-15",
                    "valor": 1200,
                    "descricao": "Pagamento 2"
                }
            ]
        }
        
        with open(person_dir / "resultado.json", "w", encoding="utf-8") as f:
            json.dump(resultado_data, f, indent=2)
        
        # Criar estrutura para outra pessoa (novo formato)
        new_person_dir = self.test_data_dir / "New Person" / "2023"
        new_person_dir.mkdir(parents=True)
        
        # Criar perfil.json
        profile_data = {
            "nome_completo": "New Person",
            "funcional": "12345",
            "cargo": "Analista",
            "departamento": "TI"
        }
        
        with open(new_person_dir / "perfil.json", "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2)
        
        # Criar frequencias.json
        attendance_data = [
            {
                "data": "2023-01-01",
                "status": "presente",
                "justificativa": ""
            },
            {
                "data": "2023-01-02",
                "status": "presente",
                "justificativa": ""
            }
        ]
        
        with open(new_person_dir / "frequencias.json", "w", encoding="utf-8") as f:
            json.dump(attendance_data, f, indent=2)
        
        # Criar pagamentos.json
        payment_data = [
            {
                "data": "2023-01-15",
                "valor": 2000,
                "descricao": "Pagamento 1"
            },
            {
                "data": "2023-02-15",
                "valor": 2200,
                "descricao": "Pagamento 2"
            }
        ]
        
        with open(new_person_dir / "pagamentos.json", "w", encoding="utf-8") as f:
            json.dump(payment_data, f, indent=2)
    
    def test_import_data(self):
        """Testa importação de dados."""
        # Importar dados
        imported_count = self.analyzer.import_data()
        
        # Verificar número de arquivos importados
        self.assertEqual(imported_count, 4)  # 1 resultado.json + 3 arquivos do novo formato
        
        # Verificar se os dados foram importados corretamente
        attendance_df = self.analyzer.analyze_attendance()
        payment_df = self.analyzer.analyze_payments()
        
        # Verificar dados de frequência
        self.assertEqual(len(attendance_df), 2)  # 2 pessoas
        
        test_person = attendance_df[attendance_df['name'] == 'Test Person'].iloc[0]
        self.assertEqual(test_person['total_days'], 2)
        self.assertEqual(test_person['present_days'], 1)
        self.assertEqual(test_person['attendance_rate'], 50.0)
        
        new_person = attendance_df[attendance_df['name'] == 'New Person'].iloc[0]
        self.assertEqual(new_person['total_days'], 2)
        self.assertEqual(new_person['present_days'], 2)
        self.assertEqual(new_person['attendance_rate'], 100.0)
        
        # Verificar dados de pagamento
        self.assertEqual(len(payment_df), 2)  # 2 pessoas
        
        test_person = payment_df[payment_df['name'] == 'Test Person'].iloc[0]
        self.assertEqual(test_person['total_payments'], 2)
        self.assertEqual(test_person['total_amount'], 2200.0)
        self.assertEqual(test_person['avg_amount'], 1100.0)
        
        new_person = payment_df[payment_df['name'] == 'New Person'].iloc[0]
        self.assertEqual(new_person['total_payments'], 2)
        self.assertEqual(new_person['total_amount'], 4200.0)
        self.assertEqual(new_person['avg_amount'], 2100.0)
    
    def test_generate_summary(self):
        """Testa geração de resumo."""
        # Importar dados primeiro
        self.analyzer.import_data()
        
        # Gerar resumo HTML
        html_file = self.analyzer.generate_summary(output_format='html')
        self.assertTrue(Path(html_file).exists())
        
        # Gerar resumo JSON
        json_file = self.analyzer.generate_summary(output_format='json')
        self.assertTrue(Path(json_file).exists())
        
        # Verificar conteúdo do JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)
        
        self.assertIn('attendance', summary_data)
        self.assertIn('payments', summary_data)
        self.assertEqual(len(summary_data['attendance']), 2)
        self.assertEqual(len(summary_data['payments']), 2)
    
    def test_plot_generation(self):
        """Testa geração de gráficos."""
        # Importar dados primeiro
        self.analyzer.import_data()
        
        # Gerar gráficos
        attendance_plot = self.analyzer.plot_attendance()
        payment_plot = self.analyzer.plot_payments()
        
        # Verificar se os arquivos foram criados
        self.assertTrue(Path(attendance_plot).exists())
        self.assertTrue(Path(payment_plot).exists())

if __name__ == '__main__':
    unittest.main() 