from __future__ import annotations

from typing import Optional

from ..core.logging_utils import get_logger
from ..core.aws_client import AwsContext

logger = get_logger(__name__)


def snapshot_volume(
    *,
    aws: AwsContext,
    dry_run: bool,
    volume_id: str,
    description: Optional[str] = None,
) -> None:
    desc = description or f"SRE Toolkit snapshot for {volume_id}"
    logger.info(
        "Creating snapshot for volume %s (dry_run=%s, description=%s)",
        volume_id,
        dry_run,
        desc,
    )

    try:
        resp = aws.ec2.create_snapshot(
            VolumeId=volume_id,
            Description=desc,
            DryRun=dry_run,
        )
        snapshot_id = resp.get("SnapshotId") if not dry_run else "DRY-RUN"
        logger.info("Snapshot requested: %s", snapshot_id)
    except Exception as exc:
        logger.exception("Failed to snapshot volume %s: %s", volume_id, exc)
        raise
