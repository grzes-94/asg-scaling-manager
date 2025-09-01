# ASG Scaling Manager

Manage AWS Auto Scaling Group capacities by tag filters with a simple, reliable CLI.

## Quick Install

```bash
pip install asg-scaling-manager
```

## Usage

```bash
# Get help
asg-sm --help

# Scale ASGs tagged with eks:cluster-name=my-cluster to 6 instances total
asg-sm --tag-value my-cluster --desired 6 --dry-run

# Apply changes with optional per-ASG max cap
asg-sm --tag-value my-cluster --desired 8 --max-size 5 --region eu-west-1

# Scale down to zero (sets min/max/desired to 0)
asg-sm --tag-value my-cluster --desired 0
```

## Features

- **Tag-based filtering**: Target ASGs by `eks:cluster-name` (default) or custom tags
- **Smart distribution**: Evenly distributes desired capacity across matched ASGs
- **Safety first**: Dry-run mode to preview changes
- **EKS optimized**: Defaults to `eks:cluster-name` tag for easy EKS cluster management
- **Flexible caps**: Optional per-ASG max size limits
- **Human-readable logging**: Color-coded logs with detailed execution flow

## Examples

```bash
# Preview scaling for production cluster
asg-sm --tag-value prod-cluster --desired 12 --dry-run

# Scale with name filter and custom tag
asg-sm --tag-key team --tag-value payments --name-contains web --desired 4

# Emergency scale down
asg-sm --tag-value staging --desired 0
```

## Logging

The tool provides detailed human-readable logging with color support:

```bash
# Default INFO level logging
asg-sm --tag-value my-cluster --desired 6 --dry-run

# Enable DEBUG level for detailed execution flow
ASG_SCALING_MANAGER_LOG_LEVEL=DEBUG asg-sm --tag-value my-cluster --desired 6 --dry-run
```

Log events include:
- **cli.start**: Command arguments and configuration
- **asg.discovery**: ASG discovery and filtering process
- **planning**: Capacity distribution planning details
- **aws.asg.update**: Individual ASG update operations
- **execution**: Overall execution status

## Notes

- **Default tag**: Uses `eks:cluster-name` by default (perfect for EKS clusters)
- **Desired vs max-size**: `--desired` is total across all ASGs, `--max-size` is per-ASG cap
- **AWS auth**: Uses `--profile` and/or `--region` for AWS credentials
- **Dry-run**: Always test with `--dry-run` first
- **Logging**: Set `ASG_SCALING_MANAGER_LOG_LEVEL=DEBUG` for detailed execution flow

## Alternative Installation

```bash
# Isolated install (recommended for CLIs)
pipx install asg-scaling-manager

# Development install
git clone https://github.com/grzes-94/asg-scaling-manage
cd asg-scaling-manage
pip install -e .
```
