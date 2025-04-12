"""
Comandos CLI para o módulo de desenvolvimento de talentos.
"""
import os
import argparse
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.talent_development.matrix_9box import DynamicMatrix9Box


class TalentDevelopmentCommands:
    """
    Classe que implementa os comandos CLI para o módulo de desenvolvimento de talentos.
    """
    
    def __init__(self, console: Console, data_pipeline: DataPipeline):
        """
        Inicializa os comandos de desenvolvimento de talentos.
        
        Args:
            console: Console rich para exibição
            data_pipeline: Pipeline de dados
        """
        self.console = console
        self.data_pipeline = data_pipeline
        
    def add_parser(self, subparsers):
        """
        Adiciona parsers para comandos relacionados a desenvolvimento de talentos.
        
        Args:
            subparsers: Objeto de subparsers do parser principal
        """
        # Comando da matriz 9-box
        matrix_parser = subparsers.add_parser(
            'nine-box', 
            help='Matriz 9-Box para análise de desempenho e potencial'
        )
        matrix_subparsers = matrix_parser.add_subparsers(dest='nine_box_command')
        
        # Subcomando para visualizar
        visualize_parser = matrix_subparsers.add_parser(
            'visualize', 
            help='Visualizar matriz 9-box para uma pessoa'
        )
        visualize_parser.add_argument(
            'person_id', 
            type=str, 
            help='ID da pessoa'
        )
        visualize_parser.add_argument(
            '--quarters', 
            type=int, 
            default=8, 
            help='Número de trimestres para análise (padrão: 8)'
        )
        visualize_parser.add_argument(
            '--output', 
            type=str, 
            help='Caminho para salvar a visualização'
        )
        visualize_parser.add_argument(
            '--show-future', 
            action='store_true', 
            help='Mostrar projeção futura'
        )
        
        # Subcomando para relatório
        report_parser = matrix_subparsers.add_parser(
            'report', 
            help='Gerar relatório de matriz 9-box para uma pessoa'
        )
        report_parser.add_argument(
            'person_id', 
            type=str, 
            help='ID da pessoa'
        )
        report_parser.add_argument(
            '--quarters', 
            type=int, 
            default=8, 
            help='Número de trimestres para análise (padrão: 8)'
        )
        report_parser.add_argument(
            '--output', 
            type=str, 
            help='Diretório para salvar o relatório'
        )
        
        # Subcomando para adicionar posição
        add_parser = matrix_subparsers.add_parser(
            'add-position', 
            help='Adicionar nova posição na matriz 9-box'
        )
        add_parser.add_argument(
            'person_id', 
            type=str, 
            help='ID da pessoa'
        )
        add_parser.add_argument(
            '--performance', 
            type=float, 
            required=True, 
            help='Valor de desempenho (0-10)'
        )
        add_parser.add_argument(
            '--potential', 
            type=float, 
            required=True, 
            help='Valor de potencial (0-10)'
        )
        add_parser.add_argument(
            '--date', 
            type=str, 
            help='Data da avaliação (formato: YYYY-MM-DD, padrão: hoje)'
        )
        add_parser.add_argument(
            '--source', 
            type=str, 
            help='Fonte da avaliação (ex: "Avaliação Anual 2024")'
        )
        
        # Comando de ciclo de feedback
        feedback_parser = subparsers.add_parser(
            'feedback-cycle', 
            help='Ciclo de feedback integrado ao desenvolvimento'
        )
        feedback_subparsers = feedback_parser.add_subparsers(dest='feedback_command')
        
        # Comando de análise de rede de influência
        network_parser = subparsers.add_parser(
            'influence-network', 
            help='Análise de redes de influência e impacto'
        )
        network_subparsers = network_parser.add_subparsers(dest='network_command')
        
        # Comando para simulação de carreira
        simulation_parser = subparsers.add_parser(
            'career-sim', 
            help='Simulação de cenários de carreira'
        )
        simulation_subparsers = simulation_parser.add_subparsers(dest='simulation_command')
    
    def handle_command(self, args):
        """
        Manipula os comandos de desenvolvimento de talentos.
        
        Args:
            args: Argumentos parseados
            
        Returns:
            True se o comando foi encontrado e executado, False caso contrário
        """
        if hasattr(args, 'command') and args.command == 'nine-box':
            return self._handle_nine_box(args)
        elif hasattr(args, 'command') and args.command == 'feedback-cycle':
            return self._handle_feedback_cycle(args)
        elif hasattr(args, 'command') and args.command == 'influence-network':
            return self._handle_influence_network(args)
        elif hasattr(args, 'command') and args.command == 'career-sim':
            return self._handle_career_simulation(args)
        
        return False
    
    def _handle_nine_box(self, args):
        """
        Manipula os comandos relacionados à matriz 9-box.
        
        Args:
            args: Argumentos parseados
            
        Returns:
            True se o comando foi encontrado e executado, False caso contrário
        """
        matrix = DynamicMatrix9Box(self.data_pipeline)
        
        if hasattr(args, 'nine_box_command'):
            if args.nine_box_command == 'visualize':
                self._handle_nine_box_visualize(args, matrix)
                return True
            elif args.nine_box_command == 'report':
                self._handle_nine_box_report(args, matrix)
                return True
            elif args.nine_box_command == 'add-position':
                self._handle_nine_box_add_position(args, matrix)
                return True
        
        self.console.print(
            Panel("[yellow]Comando da Matriz 9-Box incompleto.[/yellow] "
                  "Use os subcomandos: visualize, report, add-position")
        )
        return True
    
    def _handle_nine_box_visualize(self, args, matrix: DynamicMatrix9Box):
        """
        Manipula o comando para visualizar a matriz 9-box.
        
        Args:
            args: Argumentos parseados
            matrix: Instância da matriz 9-box
        """
        self.console.print(f"[bold]Visualizando Matriz 9-Box para:[/bold] {args.person_id}")
        
        output_path = None
        if args.output:
            output_path = Path(args.output)
        
        try:
            # Carregar dados se não carregados ainda
            if args.person_id not in matrix.historical_data:
                positions = matrix.load_data(args.person_id)
                if not positions:
                    self.console.print(
                        f"[red]Nenhuma posição encontrada para {args.person_id}.[/red]"
                    )
                    return
            
            viz_path = matrix.visualize_matrix(
                args.person_id,
                output_path=output_path,
                show_future=args.show_future,
                timespan_quarters=args.quarters
            )
            
            self.console.print(f"[green]Visualização gerada:[/green] {viz_path}")
            
        except Exception as e:
            self.console.print(f"[red]Erro ao gerar visualização:[/red] {str(e)}")
    
    def _handle_nine_box_report(self, args, matrix: DynamicMatrix9Box):
        """
        Manipula o comando para gerar relatório da matriz 9-box.
        
        Args:
            args: Argumentos parseados
            matrix: Instância da matriz 9-box
        """
        self.console.print(f"[bold]Gerando Relatório de Matriz 9-Box para:[/bold] {args.person_id}")
        
        output_path = None
        if args.output:
            output_path = Path(args.output)
            os.makedirs(output_path, exist_ok=True)
        
        try:
            # Carregar dados se não carregados ainda
            if args.person_id not in matrix.historical_data:
                positions = matrix.load_data(args.person_id)
                if not positions:
                    self.console.print(
                        f"[red]Nenhuma posição encontrada para {args.person_id}.[/red]"
                    )
                    return
            
            report_path, viz_path = matrix.generate_report(
                args.person_id,
                output_path=output_path,
                timespan_quarters=args.quarters
            )
            
            self.console.print(f"[green]Relatório gerado:[/green] {report_path}")
            self.console.print(f"[green]Visualização gerada:[/green] {viz_path}")
            
            # Mostrar prévia do relatório
            try:
                with open(report_path, 'r') as f:
                    report_content = f.read()
                    # Mostrar apenas o início do relatório
                    report_preview = '\n'.join(report_content.split('\n')[:20])
                    if len(report_content.split('\n')) > 20:
                        report_preview += "\n...\n(Relatório completo no arquivo)"
                    
                    self.console.print("\n[bold]Prévia do Relatório:[/bold]")
                    self.console.print(Markdown(report_preview))
            except Exception as e:
                self.console.print(f"[yellow]Não foi possível mostrar prévia do relatório:[/yellow] {str(e)}")
            
        except Exception as e:
            self.console.print(f"[red]Erro ao gerar relatório:[/red] {str(e)}")
    
    def _handle_nine_box_add_position(self, args, matrix: DynamicMatrix9Box):
        """
        Manipula o comando para adicionar posição na matriz 9-box.
        
        Args:
            args: Argumentos parseados
            matrix: Instância da matriz 9-box
        """
        self.console.print(f"[bold]Adicionando posição na Matriz 9-Box para:[/bold] {args.person_id}")
        
        # Validar valores
        if not 0 <= args.performance <= 10:
            self.console.print("[red]Erro: O valor de desempenho deve estar entre 0 e 10.[/red]")
            return
        
        if not 0 <= args.potential <= 10:
            self.console.print("[red]Erro: O valor de potencial deve estar entre 0 e 10.[/red]")
            return
        
        # Processar data
        if args.date:
            try:
                date = datetime.datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                self.console.print("[red]Erro: Formato de data inválido. Use YYYY-MM-DD.[/red]")
                return
        else:
            date = datetime.datetime.now()
        
        # Criar source_data
        source_data = {
            "source": args.source or "Avaliação Manual",
            "added_by": "CLI",
            "added_at": datetime.datetime.now().isoformat()
        }
        
        try:
            # Adicionar posição
            position = matrix.add_position(
                args.person_id,
                args.performance,
                args.potential,
                date,
                source_data
            )
            
            # Salvar no data_pipeline, se disponível
            if self.data_pipeline:
                # Converter para formato do pipeline
                position_data = {
                    "person_id": args.person_id,
                    "performance": args.performance,
                    "potential": args.potential,
                    "date": date.strftime('%Y-%m-%d'),
                    "source": args.source or "Avaliação Manual",
                    "quadrant": f"{position.quadrant[0]},{position.quadrant[1]}",
                    "quadrant_name": position.quadrant_name
                }
                
                self.data_pipeline.save_nine_box_position(position_data)
                self.console.print("[green]Posição salva com sucesso no banco de dados.[/green]")
            
            # Exibir informações da posição
            table = Table(title=f"Nova Posição para {args.person_id}")
            table.add_column("Atributo", style="cyan")
            table.add_column("Valor")
            
            table.add_row("Desempenho", f"{args.performance:.2f}/10")
            table.add_row("Potencial", f"{args.potential:.2f}/10")
            table.add_row("Data", date.strftime('%Y-%m-%d'))
            table.add_row("Quadrante", position.quadrant_name)
            table.add_row("Fonte", args.source or "Avaliação Manual")
            
            self.console.print(table)
            
            # Sugerir próximos passos
            self.console.print("\n[bold]Próximos passos:[/bold]")
            self.console.print("1. Visualizar matriz atualizada:")
            self.console.print(f"   [green]python -m peopleanalytics nine-box visualize {args.person_id} --show-future[/green]")
            self.console.print("2. Gerar relatório completo:")
            self.console.print(f"   [green]python -m peopleanalytics nine-box report {args.person_id}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Erro ao adicionar posição:[/red] {str(e)}")
    
    def _handle_feedback_cycle(self, args):
        """
        Manipula os comandos relacionados ao ciclo de feedback.
        
        Args:
            args: Argumentos parseados
            
        Returns:
            True se o comando foi encontrado e executado, False caso contrário
        """
        self.console.print(
            Panel("[yellow]Funcionalidade Ciclo de Feedback em desenvolvimento.[/yellow]",
                 title="Em Construção")
        )
        return True
    
    def _handle_influence_network(self, args):
        """
        Manipula os comandos relacionados à rede de influência.
        
        Args:
            args: Argumentos parseados
            
        Returns:
            True se o comando foi encontrado e executado, False caso contrário
        """
        self.console.print(
            Panel("[yellow]Funcionalidade Rede de Influência em desenvolvimento.[/yellow]",
                 title="Em Construção")
        )
        return True
    
    def _handle_career_simulation(self, args):
        """
        Manipula os comandos relacionados à simulação de carreira.
        
        Args:
            args: Argumentos parseados
            
        Returns:
            True se o comando foi encontrado e executado, False caso contrário
        """
        self.console.print(
            Panel("[yellow]Funcionalidade Simulação de Carreira em desenvolvimento.[/yellow]",
                 title="Em Construção")
        )
        return True 