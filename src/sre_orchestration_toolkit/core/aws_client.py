from __future__ import annotations

from dataclasses import dataclass

import boto3

from ..config.loader import AwsConfig


@dataclass
class AwsContext:
    session: boto3.session.Session
    ec2: any  # typed loosely here to avoid heavy imports
    region: str


def build_aws_context(cfg: AwsConfig) -> AwsContext:
    session = boto3.Session(profile_name=cfg.profile, region_name=cfg.region)
    ec2 = session.client("ec2")
    return AwsContext(session=session, ec2=ec2, region=cfg.region)
