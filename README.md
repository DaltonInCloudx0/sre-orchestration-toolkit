# SRE Orchestration Toolkit

YAML-driven SRE toolkit for AWS.

Describe what you want done in a YAML file – start/stop instances, create snapshots, clean old ones, or even fully rehydrate an instance – and the toolkit orchestrates the steps for you with dry-run safety.

## Status

Early WIP. Core features:

- Read operations from a YAML file
- Start and stop EC2 instances
- Create EBS volume snapshots
- Cleanup old snapshots based on retention
- Rehydrate an EC2 instance into a new type while preserving metadata (experimental)

## Example YAML

```yaml
aws_profile: default
region: us-east-1
dry_run: true

operations:
  - type: start_instance
    instance_id: i-0123456789abcdef0

  - type: snapshot_volume
    volume_id: vol-0123456789abcdef0
    description: "Pre-change snapshot"

  - type: rehydrate_instance
    source_instance: i-0123456789abcdef0
    new_type: t3.large
    preserve_tags: true
    validate_health: true

## Quickstart

```bash
# Clone
git clone https://github.com/DaltonInCloudx0/sre-orchestration-toolkit.git
cd sre-orchestration-toolkit

# Create a virtualenv
python -m venv .venv
source .venv/Scripts/activate  # Git Bash on Windows

# Install in editable mode
pip install -e .

# Run a sample worksheet (dry-run, safe)
sre-toolkit run examples/simple-start-stop.yaml


## Roadmap

- Add snapshot_volume and cleanup_snapshots operations
- Add EC2 rehydrate_instance (experimental)
- Add input validation for operation parameters
- Add status and result reporting per operation
- Add CI workflow for linting and tests

