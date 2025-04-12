#!/usr/bin/env python
"""
Main module for People Analytics.

Provides the entry point for the application.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from rich.console import Console
from rich.panel import Panel

from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.cli_commands.talent_development_commands import TalentDevelopmentCommands
# Outros módulos de comandos serão importados aqui conforme necessário


def main():
    """Função principal da CLI."""
    console = Console()
    
    # Banner de boas-vindas
    console.print(
        Panel.fit(
            "[bold cyan]People Analytics Platform[/bold cyan]\n"
            "[green]Um sistema avançado para analytics e desenvolvimento de talentos[/green]",
            border_style="blue"
        )
    )
    
    # Verificar diretório de dados
    data_dir = Path("data")
    output_dir = Path("output")
    
    if not data_dir.exists():
        console.print(
            "[yellow]Diretório de dados não encontrado. Criando...[/yellow]"
        )
        data_dir.mkdir(exist_ok=True)
        
    if not output_dir.exists():
        console.print(
            "[yellow]Diretório de saída não encontrado. Criando...[/yellow]"
        )
        output_dir.mkdir(exist_ok=True)
    
    # Configurar o pipeline de dados
    try:
        data_pipeline = DataPipeline()
        console.print("[green]Pipeline de dados inicializado com sucesso.[/green]")
    except Exception as e:
        console.print(f"[red]Erro ao inicializar pipeline de dados:[/red] {str(e)}")
        data_pipeline = None
    
    # Configurar o parser de argumentos
    parser = argparse.ArgumentParser(
        description="People Analytics Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Comando a ser executado"
    )
    
    # Adicionar comandos de desenvolvimento de talentos
    talent_dev_commands = TalentDevelopmentCommands(console, data_pipeline)
    talent_dev_commands.add_parser(subparsers)
    
    # Adicionar outros módulos de comandos aqui conforme necessário
    
    # Comando de ajuda para todos os módulos
    help_parser = subparsers.add_parser(
        'help',
        help='Mostrar ajuda sobre comandos disponíveis'
    )
    
    # Comando de versão
    version_parser = subparsers.add_parser(
        'version',
        help='Mostrar versão do sistema'
    )
    
    # Parsear argumentos
    if len(sys.argv) <= 1:
        parser.print_help()
        return
        
    args = parser.parse_args()
    
    # Executar comandos
    if args.command == 'help':
        parser.print_help()
    elif args.command == 'version':
        from peopleanalytics import __version__
        console.print(f"[bold]People Analytics Platform[/bold] versão {__version__}")
    else:
        # Tentar comandos dos módulos registrados
        handled = talent_dev_commands.handle_command(args)
        
        # Se nenhum módulo tratou o comando
        if not handled:
            console.print(f"[red]Comando não reconhecido:[/red] {args.command}")
            parser.print_help()


if __name__ == "__main__":
    main() 