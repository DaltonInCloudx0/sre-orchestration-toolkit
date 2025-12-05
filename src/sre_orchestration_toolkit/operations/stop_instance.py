from __future__ import annotations

from botocore.exceptions import ClientError

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
        logger.info("StopInstances call issued for %s", instance_id)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        msg = exc.response.get("Error", {}).get("Message", str(exc))

        if code == "DryRunOperation":
            logger.info("Dry-run success for stop_instance on %s: %s", instance_id, msg)
            return

        if code in ("InvalidInstanceID.Malformed", "InvalidInstanceID.NotFound") and dry_run:
            logger.warning(
                "Dry-run stop_instance: instance id %s is invalid or not found: %s",
                instance_id,
                msg,
            )
            return

        logger.exception("Failed to stop instance %s: %s", instance_id, exc)
        raise

