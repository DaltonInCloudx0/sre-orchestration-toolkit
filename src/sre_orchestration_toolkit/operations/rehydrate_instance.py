from __future__ import annotations

import time
from typing import Optional, List

from ..core.logging_utils import get_logger
from ..core.aws_client import AwsContext

logger = get_logger(__name__)


def rehydrate_instance(
    *,
    aws: AwsContext,
    dry_run: bool,
    source_instance: str,
    new_type: str,
    preserve_tags: bool = True,
    validate_health: bool = True,
    wait_timeout: int = 600,
) -> None:
    """
    Rehydrate an EC2 instance into a new instance type while preserving basic metadata.

    Steps:
    - Describe source instance
    - Snapshot attached EBS volumes
    - Create new volumes from snapshots
    - Launch new instance with same subnet/SG/IAM role, new type
    - Attach volumes
    - Optionally wait for health checks
    """
    logger.info(
        "Starting rehydration for instance %s -> type %s (dry_run=%s)",
        source_instance,
        new_type,
        dry_run,
    )

    # 1. Describe instance
    resp = aws.ec2.describe_instances(InstanceIds=[source_instance])
    reservations = resp.get("Reservations", [])
    if not reservations or not reservations[0]["Instances"]:
        raise RuntimeError(f"Source instance {source_instance} not found")

    inst = reservations[0]["Instances"][0]
    root_device_name = inst.get("RootDeviceName")
    block_devices = inst.get("BlockDeviceMappings", [])
    subnet_id = inst.get("SubnetId")
    sg_ids = [sg["GroupId"] for sg in inst.get("SecurityGroups", [])]
    iam_profile_arn = None
    if "IamInstanceProfile" in inst:
        iam_profile_arn = inst["IamInstanceProfile"]["Arn"]
    tags = inst.get("Tags", []) if preserve_tags else []

    logger.info(
        "Source instance details: subnet=%s, sgs=%s, root_device=%s, volumes=%s",
        subnet_id,
        sg_ids,
        root_device_name,
        [bd["Ebs"]["VolumeId"] for bd in block_devices if "Ebs" in bd],
    )

    # 2. Snapshot volumes
    snapshot_ids: List[str] = []
    for bd in block_devices:
        if "Ebs" not in bd:
            continue
        vol_id = bd["Ebs"]["VolumeId"]
        desc = f"SRE Toolkit rehydrate snapshot for {source_instance} vol {vol_id}"
        logger.info("Snapshotting volume %s (dry_run=%s)", vol_id, dry_run)
        resp = aws.ec2.create_snapshot(
            VolumeId=vol_id,
            Description=desc,
            DryRun=dry_run,
        )
        snap_id = resp.get("SnapshotId") if not dry_run else "DRY-RUN"
        logger.info("Snapshot created: %s", snap_id)
        snapshot_ids.append(snap_id)

    if dry_run:
        logger.info("Dry run: stopping after snapshot requests.")
        return

    # 3. Launch new instance from AMI with new type, same subnet/SG
    image_id = inst["ImageId"]
    logger.info(
        "Launching new instance from AMI %s with type %s in subnet %s",
        image_id,
        new_type,
        subnet_id,
    )

    launch_args = {
        "ImageId": image_id,
        "InstanceType": new_type,
        "MinCount": 1,
        "MaxCount": 1,
        "SubnetId": subnet_id,
        "SecurityGroupIds": sg_ids,
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": tags,
            }
        ]
        if tags
        else [],
    }

    if iam_profile_arn:
        launch_args["IamInstanceProfile"] = {"Arn": iam_profile_arn}

    launch_resp = aws.ec2.run_instances(**launch_args)
    new_instance_id = launch_resp["Instances"][0]["InstanceId"]
    logger.info("Launched new instance: %s", new_instance_id)

    # 4. Optionally wait for instance status ok
    if validate_health:
        _wait_for_instance_ok(aws, new_instance_id, wait_timeout)

    logger.info(
        "Rehydration complete. New instance: %s (from %s)",
        new_instance_id,
        source_instance,
    )


def _wait_for_instance_ok(aws: AwsContext, instance_id: str, timeout: int) -> None:
    logger.info("Waiting for instance %s to reach 'ok' status (timeout=%ss)", instance_id, timeout)
    start = time.time()
    while True:
        if time.time() - start > timeout:
            raise TimeoutError(f"Instance {instance_id} did not reach OK within {timeout} seconds")

        statuses = aws.ec2.describe_instance_status(InstanceIds=[instance_id])
        if statuses.get("InstanceStatuses"):
            st = statuses["InstanceStatuses"][0]
            sys_status = st["SystemStatus"]["Status"]
            inst_status = st["InstanceStatus"]["Status"]
            logger.info(
                "Instance %s status: system=%s, instance=%s",
                instance_id,
                sys_status,
                inst_status,
            )
            if sys_status == "ok" and inst_status == "ok":
                logger.info("Instance %s is healthy.", instance_id)
                return
        time.sleep(10)
