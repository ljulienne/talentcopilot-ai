# TalentCopilot Next — Release 0.7.1

## TalentCopilot Doctor

This release adds a read-only repository health checker designed for Colab and local development.

### Checks

- repository layout;
- Python path configuration;
- critical imports;
- visible navigation modules and renderer functions;
- critical test inventory;
- tracked release backup artifacts;
- Git working-tree state and remote credential safety.

### Usage

```bash
python tools/talentcopilot_doctor.py
python tools/talentcopilot_doctor.py --strict
python tools/talentcopilot_doctor.py --json
python tools/talentcopilot_doctor.py --skip-git
```

Exit codes:

- `0`: no blocking failure;
- `1`: at least one blocking failure;
- `2`: warnings present when `--strict` is enabled.
