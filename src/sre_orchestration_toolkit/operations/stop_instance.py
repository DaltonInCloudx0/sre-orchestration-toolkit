from __future__ import annotations

from ..core.logging_utils import get_logger
from ..core.aws_client import AwsContext

logger = get_logger(__name__)


def stop_instance(*, aws: AwsContext, dry_run: bool, instance_id: str) -> None:
    logger.info("Request to stop instance %s (dry_run=%s)", instance_id, dry_run)
    try:
        aws.ec2.stop_instances(
            InstanceIds=[instance_id],
            DryRun=dry_run,
        )
        logger.info("Stop_instances call issued for %s", instance_id)
    except Exception as exc:
        logger.exception("Failed to stop instance %s: %s", instance_id, exc)
        raise
