"""Capacity distribution planner."""

from __future__ import annotations

from typing import List, Optional

from .models import AsgInfo, CapacityUpdate, Plan
from .logging import get_logger


def plan_zero(asgs: List[AsgInfo]) -> Plan:
    log = get_logger()
    log.info("planner.zero_mode", asg_count=len(asgs))
    return Plan(
        updates=[CapacityUpdate(name=a.name, desired=0, min_size=0, max_size=0) for a in asgs]
    )


def plan_equal_split(asgs: List[AsgInfo], total_desired: int, per_asg_max_cap: Optional[int]) -> Plan:
    log = get_logger()
    
    if not asgs:
        log.info("planner.no_asgs")
        return Plan(updates=[])
    
    n = len(asgs)
    log.info("planner.equal_split.start", total_desired=total_desired, asg_count=n, per_asg_max_cap=per_asg_max_cap)

    # Compute effective caps per ASG considering existing MaxSize and optional per-ASG cap
    caps: List[int] = []
    for a in asgs:
        effective_cap = a.max_size
        if per_asg_max_cap is not None:
            effective_cap = per_asg_max_cap
        caps.append(max(0, effective_cap))
        log.debug("planner.asg.cap", name=a.name, original_max=a.max_size, effective_cap=effective_cap)

    log.info("planner.caps.computed", total_capacity=sum(caps), caps=caps)

    # Initial fair share
    base = total_desired // n
    remainder = total_desired % n
    log.debug("planner.fair_share", base=base, remainder=remainder)
    
    assigned: List[int] = []
    for idx, cap in enumerate(caps):
        want = base + (1 if idx < remainder else 0)
        actual = min(want, cap)
        assigned.append(actual)
        log.debug("planner.asg.initial", name=asgs[idx].name, want=want, cap=cap, assigned=actual)

    remaining = total_desired - sum(assigned)
    log.info("planner.initial_assignment", total_assigned=sum(assigned), remaining=remaining)
    
    if remaining > 0:
        # Top-up pass: allocate remaining to ASGs that still have headroom
        log.info("planner.topup.start", remaining=remaining)
        for idx, cap in enumerate(caps):
            if remaining <= 0:
                break
            headroom = cap - assigned[idx]
            if headroom <= 0:
                continue
            add = min(headroom, remaining)
            assigned[idx] += add
            remaining -= add
            log.debug("planner.asg.topup", name=asgs[idx].name, headroom=headroom, add=add, new_total=assigned[idx])

    log.info("planner.final_assignment", total_assigned=sum(assigned), requested=total_desired)

    updates: List[CapacityUpdate] = []
    for idx, a in enumerate(asgs):
        u = CapacityUpdate(name=a.name, desired=assigned[idx])
        if per_asg_max_cap is not None:
            u.max_size = per_asg_max_cap
        updates.append(u)
        log.debug("planner.update.created", name=a.name, desired=assigned[idx], max_size=u.max_size)

    log.info("planner.complete", update_count=len(updates), total_desired=sum(assigned))
    return Plan(updates=updates)


