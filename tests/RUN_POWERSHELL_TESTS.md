# PowerShell Mission Test Suite

Comprehensive automated testing for all 66 PowerShell missions.

## Test Files

### `test_powershell_mission_schema.py` (26 tests)
Tests YAML structure, fields, and organization:
- ✅ Valid YAML syntax
- ✅ Required fields (mission, environment, steps, completion)
- ✅ Mission metadata (id, title, difficulty, description, estimated_time, tags)
- ✅ Difficulty values (beginner/intermediate/advanced)
- ✅ Mission ID format (powershell/topic/name)
- ✅ Windows Server Core image configuration
- ✅ PowerShell environment setup (workdir, execution policy)
- ✅ Step structure and validation fields
- ✅ Topic organization (15 expected topics)
- ✅ Mission counts (66 total, correct distribution by topic)
- ✅ Difficulty distribution (22 beginner, 31 intermediate, 13 advanced)
- ✅ Total XP (16,750 ± 750)

### `test_powershell_content_quality.py` (15 tests)
Tests content quality and best practices:
- ✅ PowerShell cmdlet usage in validation commands
- ✅ No Linux commands in PowerShell missions
- ✅ Windows file paths (C:/ not /home)
- ✅ PowerShell syntax in setup commands
- ✅ Code examples in step descriptions
- ✅ Helpful hints for each step
- ✅ Descriptive step titles
- ✅ Valid unlock chains (no broken references)
- ✅ First mission has no prerequisites
- ✅ Final mission has no unlocks
- ✅ Difficulty progression within topics
- ✅ Estimated time correlates with step count
- ✅ Core PowerShell concepts coverage
- ✅ Windows administration topics coverage

## Running Tests

### Run All PowerShell Tests
```bash
pytest tests/unit/test_powershell_*.py -v
```

### Run Schema Tests Only
```bash
pytest tests/unit/test_powershell_mission_schema.py -v
```

### Run Content Quality Tests Only
```bash
pytest tests/unit/test_powershell_content_quality.py -v
```

### Run Specific Test Class
```bash
# Schema tests
pytest tests/unit/test_powershell_mission_schema.py::TestPowerShellMissionSchema -v
pytest tests/unit/test_powershell_mission_schema.py::TestPowerShellEnvironment -v
pytest tests/unit/test_powershell_mission_schema.py::TestPowerShellMissionCounts -v

# Content quality tests
pytest tests/unit/test_powershell_content_quality.py::TestPowerShellCommandQuality -v
pytest tests/unit/test_powershell_content_quality.py::TestPowerShellDescriptionQuality -v
pytest tests/unit/test_powershell_content_quality.py::TestPowerShellProgressionQuality -v
```

### Run With Coverage
```bash
pytest tests/unit/test_powershell_*.py --cov=scenarios/powershell --cov-report=html
```

## Test Results

All 41 tests pass successfully:
- **26 schema tests** - All passing ✅
- **15 content quality tests** - All passing ✅

## What These Tests Validate

### Schema Validation
- Ensures all 66 missions have valid YAML structure
- Verifies required fields are present and correctly typed
- Confirms Windows Server Core container configuration
- Validates PowerShell-specific setup (execution policy, workdir)
- Checks mission organization and topic structure
- Verifies correct mission counts per topic

### Content Quality
- Ensures PowerShell cmdlets are used (not Linux commands)
- Validates Windows file path format (C:/ not Unix paths)
- Confirms code examples exist in step descriptions
- Verifies helpful hints are provided
- Checks unlock chains reference existing missions
- Validates difficulty progression within topics
- Ensures core PowerShell and Windows admin concepts are covered

### Why These Tests Matter
1. **Consistency**: All missions follow the same high-quality structure
2. **Completeness**: No missing fields or broken references
3. **Quality**: Content meets educational standards
4. **Maintainability**: Easy to catch regressions when editing missions
5. **Documentation**: Tests serve as specification for mission format

## Adding New Missions

When creating new PowerShell missions, run these tests to ensure they meet quality standards:

```bash
# Quick validation
pytest tests/unit/test_powershell_*.py

# Detailed output if issues found
pytest tests/unit/test_powershell_*.py -v --tb=short
```

Common issues caught by tests:
- Missing required fields
- Incorrect difficulty values
- Wrong container image
- Missing execution policy setup
- Broken unlock references
- Linux commands in PowerShell missions
- Unix-style file paths
- Missing code examples or hints
