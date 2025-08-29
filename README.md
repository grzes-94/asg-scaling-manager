# ASG Scaling Manager

Manage AWS Auto Scaling Group capacities by tag filters with a simple, reliable CLI/library.

## Install

```bash
py -3.12 -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

## CLI

```bash
python -m asg_scaling_manager.cli --help
```

- set desired capacity across ASGs that match a tag (optional name filter)
- supports dry-run and optional per-ASG max cap

## Examples

```bash
# Distribute desired=12 equally across ASGs tagged env=prod (dry-run)
python -m asg_scaling_manager.cli \
  --tag-key env --tag-value prod --desired 12 --dry-run

# Apply in eu-west-1 with an optional per-ASG cap
python -m asg_scaling_manager.cli \
  --tag-key team --tag-value payments \
  --desired 8 --max-size 5 --region eu-west-1

# Zero all matching ASGs (min/max/desired -> 0)
python -m asg_scaling_manager.cli --tag-key env --tag-value test --desired 0
```

## Notes
- **Filters**: required `--tag-key`, `--tag-value`; optional `--name-contains`.
- **Auth/Region**: `--profile` and/or `--region`.
- **Dry-run**: logs the plan; no changes applied.
 - **Desired vs. max-size**: `--desired` is the total across all matched ASGs.
   `--max-size` is a per-ASG cap. If total desired exceeds the sum of caps, the
   plan will be limited by the combined capacity and cannot reach the target.

## Library
Use `asg_scaling_manager` programmatically to build plans or apply updates.
