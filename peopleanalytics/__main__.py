#!/usr/bin/env python
"""
Main module for People Analytics.
Provides the entry point for the application CLI.
"""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from peopleanalytics.cli_commands import COMMANDS
from peopleanalytics.cli_commands.talent_development_commands import (
    TalentDevelopmentCommands,
)
from peopleanalytics.data_pipeline import DataPipeline

# Outros módulos de comandos serão importados aqui conforme necessário


def main():
    """Função principal da CLI."""
    console = Console()

    # Banner de boas-vindas
    console.print(
        Panel.fit(
            "[bold cyan]People Analytics Platform[/bold cyan]\n"
            "[green]Um sistema avançado para analytics e desenvolvimento de talentos[/green]",
            border_style="blue",
        )
    )

    # Verificar diretório de dados
    data_dir = Path("data")
    output_dir = Path("output")

    if not data_dir.exists():
        console.print("[yellow]Diretório de dados não encontrado. Criando...[/yellow]")
        data_dir.mkdir(exist_ok=True)

    if not output_dir.exists():
        console.print("[yellow]Diretório de saída não encontrado. Criando...[/yellow]")
        output_dir.mkdir(exist_ok=True)

    # Configurar o pipeline de dados
    try:
        data_pipeline = DataPipeline(str(data_dir))
        console.print("[green]Pipeline de dados inicializado com sucesso.[/green]")
    except Exception as e:
        console.print(f"[red]Erro ao inicializar pipeline de dados:[/red] {str(e)}")
        data_pipeline = None

    # Configurar o parser de argumentos
    parser = argparse.ArgumentParser(
        description="People Analytics Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a ser executado")

    # Adicionar todos os comandos registrados no dicionário COMMANDS
    registered_commands = {}
    for command_name, command_class in COMMANDS.items():
        # Evitamos duplicação de parsers
        if command_name not in registered_commands:
            command_parser = subparsers.add_parser(
                command_name, help=command_class.__doc__
            )
            command_instance = command_class()
            command_instance.add_arguments(command_parser)
            registered_commands[command_name] = command_instance

    # Adicionar comandos de desenvolvimento de talentos
    # (Apenas para comandos que não foram registrados em COMMANDS)
    talent_dev_commands = TalentDevelopmentCommands(console, data_pipeline)
    talent_dev_commands.add_parser(subparsers, exclude=registered_commands.keys())

    # Comando de ajuda para todos os módulos
    if "help" not in registered_commands:
        help_parser = subparsers.add_parser(
            "help", help="Mostrar ajuda sobre comandos disponíveis"
        )

    # Comando de versão
    if "version" not in registered_commands:
        version_parser = subparsers.add_parser(
            "version", help="Mostrar versão do sistema"
        )

    # Parsear argumentos
    if len(sys.argv) <= 1:
        parser.print_help()
        return

    args = parser.parse_args()

    # Executar comandos
    if args.command == "help":
        parser.print_help()
    elif args.command == "version":
        from peopleanalytics import __version__

        console.print(f"[bold]People Analytics Platform[/bold] versão {__version__}")
    elif args.command in registered_commands:
        # Executar comandos diretos
        exit_code = registered_commands[args.command].execute(args)
        sys.exit(exit_code)
    else:
        # Tentar comandos dos módulos registrados
        handled = talent_dev_commands.handle_command(args)

        # Se nenhum módulo tratou o comando
        if not handled:
            console.print(f"[red]Comando não reconhecido:[/red] {args.command}")
            parser.print_help()


if __name__ == "__main__":
    main()
