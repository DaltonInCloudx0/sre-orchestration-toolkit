from __future__ import annotations

from ..core.logging_utils import get_logger
from ..core.aws_client import AwsContext

logger = get_logger(__name__)


def start_instance(*, aws: AwsContext, dry_run: bool, instance_id: str) -> None:
    logger.info("Request to start instance %s (dry_run=%s)", instance_id, dry_run)
    try:
        aws.ec2.start_instances(
            InstanceIds=[instance_id],
            DryRun=dry_run,
        )
        logger.info("Start_instances call issued for %s", instance_id)
    except Exception as exc:
        logger.exception("Failed to start instance %s: %s", instance_id, exc)
        raise
