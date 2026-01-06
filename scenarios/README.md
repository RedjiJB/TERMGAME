# Mission Scenarios

This directory contains all mission scenarios organized by technology type.

## Structure

```
scenarios/
├── linux/          # Linux command-line missions
├── ios/            # Cisco IOS network device missions
└── powershell/     # Windows PowerShell missions
```

## Creating Scenarios

See [docs/mission-design.md](../docs/mission-design.md) for detailed guidance.

## Validation

Run the scenario validator:

```bash
python scripts/validate_scenarios.py
```
