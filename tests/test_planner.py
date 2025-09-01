from asg_scaling_manager.models import AsgInfo
from asg_scaling_manager.planner import plan_zero, plan_equal_split


def make_asgs(n: int, max_size: int = 10):
    return [
        AsgInfo(name=f"asg-{i}", min_size=0, max_size=max_size, desired_capacity=0)
        for i in range(n)
    ]


def make_zero_asgs(n: int):
    return [
        AsgInfo(name=f"asg-{i}", min_size=0, max_size=0, desired_capacity=0)
        for i in range(n)
    ]


def test_plan_zero_sets_all_to_zero():
    asgs = make_asgs(3, max_size=5)
    plan = plan_zero(asgs)
    assert len(plan.updates) == 3
    for u in plan.updates:
        assert u.desired == 0
        assert u.min_size == 0
        assert u.max_size == 0


def test_equal_split_basic_distribution():
    asgs = make_asgs(3, max_size=10)
    plan = plan_equal_split(asgs, total_desired=8, per_asg_max_cap=None)
    desireds = sorted(u.desired for u in plan.updates if u.desired is not None)
    assert desireds == [2, 3, 3]


def test_equal_split_respects_per_asg_cap():
    asgs = make_asgs(2, max_size=10)
    plan = plan_equal_split(asgs, total_desired=10, per_asg_max_cap=4)
    desireds = sorted(u.desired for u in plan.updates if u.desired is not None)
    assert desireds == [4, 4]
    # When cap is set, we also propagate max_size in updates
    for u in plan.updates:
        assert u.max_size == 4


def test_equal_split_respects_current_asg_max():
    asgs = [
        AsgInfo(name="a", min_size=0, max_size=2, desired_capacity=0),
        AsgInfo(name="b", min_size=0, max_size=10, desired_capacity=0),
    ]
    plan = plan_equal_split(asgs, total_desired=5, per_asg_max_cap=None)
    # base=2, remainder=1; a limited to 2, b gets 3
    mapping = {u.name: u.desired for u in plan.updates}
    assert mapping == {"a": 2, "b": 3}


def test_equal_split_from_zero_capacity():
    asgs = make_zero_asgs(3)
    plan = plan_equal_split(asgs, total_desired=6, per_asg_max_cap=None)
    # All ASGs start with max_size=0, so they can't accept any capacity
    # The plan should be limited by the combined capacity (0)
    assert len(plan.updates) == 3
    for u in plan.updates:
        assert u.desired == 0
    assert plan.total_desired == 0


def test_equal_split_from_zero_with_cap():
    asgs = make_zero_asgs(2)
    plan = plan_equal_split(asgs, total_desired=4, per_asg_max_cap=3)
    # Even though ASGs start with max_size=0, the per_asg_max_cap=3 allows them to scale up
    assert len(plan.updates) == 2
    for u in plan.updates:
        assert u.desired == 2
        assert u.max_size == 3
    assert plan.total_desired == 4


