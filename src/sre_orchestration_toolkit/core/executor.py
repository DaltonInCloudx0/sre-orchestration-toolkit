from __future__ import annotations

from typing import Dict, Any

from ..config.loader import ToolkitConfig
from ..core.logging_utils import get_logger
from ..operations import registry
from .aws_client import AwsContext

logger = get_logger(__name__)


def execute_config(cfg: ToolkitConfig, aws: AwsContext) -> None:
    logger.info(
        "Starting SRE Toolkit run (profile=%s, region=%s, dry_run=%s)",
        cfg.aws.profile,
        cfg.aws.region,
        cfg.dry_run,
    )

    for idx, op in enumerate(cfg.operations, start=1):
        op_type = op.get("type")
        if not op_type:
            logger.error("Operation #%s missing 'type' key. Skipping.", idx)
            continue

        handler = registry.get(op_type)
        if not handler:
            logger.error("Unknown operation type '%s' in op #%s. Skipping.", op_type, idx)
            continue

        logger.info("Executing operation #%s: %s", idx, op_type)
        params: Dict[str, Any] = {k: v for k, v in op.items() if k != "type"}

        try:
            handler(aws=aws, dry_run=cfg.dry_run, **params)
        except Exception as exc:
            logger.exception("Operation #%s (%s) failed: %s", idx, op_type, exc)
            # SRE decision: keep going or stop? For now, we continue.
            continue

    logger.info("SRE Toolkit run complete.")
