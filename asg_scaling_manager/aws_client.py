"""AWS client wrapper for Auto Scaling Group operations."""

from __future__ import annotations

from typing import Iterable, List, Optional

import boto3
from botocore.config import Config

from .logging import get_logger
from .models import AsgInfo, CapacityUpdate


def create_session(profile: Optional[str] = None) -> boto3.session.Session:
    log = get_logger()
    if profile:
        log.debug("aws.session.create_with_profile", profile=profile)
        return boto3.session.Session(profile_name=profile)
    log.debug("aws.session.create_default")
    return boto3.session.Session()


def get_asg_client(session: boto3.session.Session, region: Optional[str] = None):
    log = get_logger()
    cfg = Config(retries={"max_attempts": 10, "mode": "standard"})
    client = session.client("autoscaling", region_name=region, config=cfg)
    log.debug("aws.client.created", service="autoscaling", region=region)
    return client


def list_asgs(session: boto3.session.Session, region: Optional[str]) -> List[AsgInfo]:
    log = get_logger()
    client = get_asg_client(session, region)
    paginator = client.get_paginator("describe_auto_scaling_groups")
    asgs: List[AsgInfo] = []
    
    log.info("aws.asg.list.start")
    page_count = 0
    for page in paginator.paginate():
        page_count += 1
        page_asgs = page.get("AutoScalingGroups", [])
        asgs.extend([
            AsgInfo(
                name=g["AutoScalingGroupName"],
                min_size=g.get("MinSize", 0),
                max_size=g.get("MaxSize", 0),
                desired_capacity=g.get("DesiredCapacity", 0),
            )
            for g in page_asgs
        ])
        log.debug("aws.asg.list.page", page_num=page_count, asg_count=len(page_asgs))
    
    log.info("aws.asg.list.complete", total_asgs=len(asgs), pages=page_count)
    return asgs


def apply_plan(session: boto3.session.Session, region: Optional[str], updates: Iterable[CapacityUpdate]) -> None:
    log = get_logger()
    client = get_asg_client(session, region)
    
    update_list = list(updates)
    log.info("aws.apply.start", update_count=len(update_list))
    
    for i, upd in enumerate(update_list):
        kwargs = {"AutoScalingGroupName": upd.name}
        if upd.min_size is not None:
            kwargs["MinSize"] = upd.min_size
        if upd.max_size is not None:
            kwargs["MaxSize"] = upd.max_size
        if upd.desired is not None:
            kwargs["DesiredCapacity"] = upd.desired
        
        if len(kwargs) > 1:  # More than just the name
            log.info(
                "aws.asg.update",
                name=upd.name,
                desired=upd.desired,
                min_size=upd.min_size,
                max_size=upd.max_size,
                update_num=i + 1,
                total_updates=len(update_list)
            )
            try:
                client.update_auto_scaling_group(**kwargs)
                log.info("aws.asg.update.success", name=upd.name)
            except Exception as e:
                log.error("aws.asg.update.failed", name=upd.name, error=str(e))
                raise
        else:
            log.debug("aws.asg.update.skipped", name=upd.name, reason="no_changes")
    
    log.info("aws.apply.complete", update_count=len(update_list))


