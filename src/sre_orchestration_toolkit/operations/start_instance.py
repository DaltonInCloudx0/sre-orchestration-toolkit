from __future__ import annotations

from botocore.exceptions import ClientError

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
        logger.info("StartInstances call issued for %s", instance_id)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        msg = exc.response.get("Error", {}).get("Message", str(exc))

        # Treat DryRunOperation as success
        if code == "DryRunOperation":
            logger.info("Dry-run success for start_instance on %s: %s", instance_id, msg)
            return

        # For fake or malformed IDs during experimentation, just log and move on
        if code in ("InvalidInstanceID.Malformed", "InvalidInstanceID.NotFound") and dry_run:
            logger.warning(
                "Dry-run start_instance: instance id %s is invalid or not found: %s",
                instance_id,
                msg,
            )
            return

        logger.exception("Failed to start instance %s: %s", instance_id, exc)
        raise
