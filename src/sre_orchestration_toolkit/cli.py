from __future__ import annotations

import click

from .config.loader import load_config
from .core.aws_client import build_aws_context
from .core.executor import execute_config
from .core.logging_utils import configure_logging


@click.group()
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR).",
)
def cli(log_level: str) -> None:
    """SRE Orchestration Toolkit CLI."""
    configure_logging(level=log_level)


@cli.command(name="run")
@click.argument("config_path", type=click.Path(exists=True))
def run(config_path: str) -> None:
    """Run an orchestration worksheet from a YAML file."""
    cfg = load_config(config_path)
    aws = build_aws_context(cfg.aws)
    execute_config(cfg, aws)
