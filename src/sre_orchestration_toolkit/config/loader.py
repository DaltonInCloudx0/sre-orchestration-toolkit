from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AwsConfig:
    profile: str
    region: str


@dataclass
class ToolkitConfig:
    aws: AwsConfig
    dry_run: bool
    operations: list[Dict[str, Any]]


def load_yaml(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(path: str) -> ToolkitConfig:
    raw = load_yaml(path)

    aws_profile = raw.get("aws_profile") or os.getenv("AWS_PROFILE") or "default"
    aws_region = raw.get("region") or os.getenv("AWS_REGION") or "us-east-1"

    # env var override
    env_dry_run = os.getenv("SRE_TOOLKIT_DRY_RUN")
    if env_dry_run is not None:
        dry_run = env_dry_run.lower() in ("1", "true", "yes")
    else:
        dry_run = bool(raw.get("dry_run", True))

    operations = raw.get("operations", [])
    if not isinstance(operations, list):
        raise ValueError("`operations` must be a list in the YAML config.")

    aws_cfg = AwsConfig(profile=aws_profile, region=aws_region)
    return ToolkitConfig(aws=aws_cfg, dry_run=dry_run, operations=operations)
