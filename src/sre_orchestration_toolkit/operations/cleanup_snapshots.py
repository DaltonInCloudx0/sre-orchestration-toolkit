from __future__ import annotations

import datetime as dt
from typing import Optional

from ..core.logging_utils import get_logger
from ..core.aws_client import AwsContext

logger = get_logger(__name__)


def cleanup_snapshots(
    *,
    aws: AwsContext,
    dry_run: bool,
    retention_days: int,
    owner_id: Optional[str] = None,
) -> None:
    logger.info(
        "Cleaning up snapshots older than %s days (dry_run=%s)",
        retention_days,
        dry_run,
    )

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=retention_days)

    params = {"OwnerIds": [owner_id]} if owner_id else {"OwnerIds": ["self"]}
    resp = aws.ec2.describe_snapshots(**params)
    snapshots = resp.get("Snapshots", [])

    for snap in snapshots:
        snap_id = snap["SnapshotId"]
        start_time: dt.datetime = snap["StartTime"]
        if start_time < cutoff:
            logger.info(
                "Snapshot %s (%s) is older than cutoff (%s). Deleting.",
                snap_id,
                start_time,
                cutoff,
            )
            try:
                aws.ec2.delete_snapshot(
                    SnapshotId=snap_id,
                    DryRun=dry_run,
                )
            except Exception as exc:
                logger.exception("Failed to delete snapshot %s: %s", snap_id, exc)
                continue
