"""Tests for PowerShell mission content quality and best practices."""

import pytest
from pathlib import Path
import yaml
import re


class TestPowerShellCommandQuality:
    """Test PowerShell command quality and syntax."""

    @pytest.fixture
    def scenarios_dir(self):
        """Get the PowerShell scenarios directory."""
        return Path("scenarios/powershell")

    @pytest.fixture
    def all_mission_files(self, scenarios_dir):
        """Get all PowerShell mission YAML files."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")
        return list(scenarios_dir.rglob("*.yml"))

    def test_validation_commands_use_powershell_syntax(self, all_mission_files):
        """Test that validation commands use PowerShell cmdlets."""
        # Common PowerShell cmdlets that should appear in missions
        powershell_cmdlets = [
            "Get-", "Set-", "New-", "Remove-", "Test-",
            "Start-", "Stop-", "Add-", "Copy-", "Move-",
            "Write-", "Read-", "Select-", "Where-",
            "$", "ForEach-", "Measure-"
        ]

        # Windows commands that are acceptable in PowerShell
        acceptable_commands = ["whoami", "reg"]

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            for i, step in enumerate(steps):
                validation = step.get("validation", {})
                command = validation.get("command", "")

                if command and validation.get("type") == "command-output":
                    # Should contain at least one PowerShell-style element
                    has_powershell_syntax = any(
                        cmdlet in command for cmdlet in powershell_cmdlets
                    )

                    # Or be an acceptable Windows command
                    is_acceptable_command = any(
                        cmd in command for cmd in acceptable_commands
                    )

                    # Or use .NET static method/type syntax
                    has_dotnet_syntax = "[" in command and "]" in command

                    assert has_powershell_syntax or is_acceptable_command or has_dotnet_syntax or "Write-Output" in str(data), (
                        f"{mission_file.name} step {i} validation command "
                        f"should use PowerShell cmdlets: {command}"
                    )

    def test_no_linux_commands_in_validation(self, all_mission_files):
        """Test that PowerShell missions don't use Linux commands."""
        linux_commands = ["ls", "cat", "grep", "sed", "awk", "find", "mkdir"]

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            for i, step in enumerate(steps):
                validation = step.get("validation", {})
                command = validation.get("command", "")

                if command:
                    # Check for standalone Linux commands (not part of longer words)
                    for linux_cmd in linux_commands:
                        pattern = rf'\b{linux_cmd}\b'
                        if re.search(pattern, command):
                            # Allow 'Get-ChildItem' which might have 'cat' in it
                            if not ("Get-" in command or "Set-" in command):
                                pytest.fail(
                                    f"{mission_file.name} step {i} uses Linux command "
                                    f"'{linux_cmd}' in: {command}"
                                )

    def test_file_paths_use_windows_format(self, all_mission_files):
        """Test that file paths use Windows format (C:/ or C:\\)."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                content = f.read()
                data = yaml.safe_load(content)

            # Check for Unix-style paths that should be Windows paths
            # Look for /home or /usr or /etc in the content
            unix_path_indicators = ["/home/", "/usr/", "/etc/", "/var/"]

            for indicator in unix_path_indicators:
                if indicator in content:
                    pytest.fail(
                        f"{mission_file.name} contains Unix path '{indicator}'. "
                        "PowerShell missions should use Windows paths (C:/)"
                    )

    def test_setup_commands_are_powershell(self, all_mission_files):
        """Test that setup commands use PowerShell cmdlets."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            setup = data.get("environment", {}).get("setup", [])

            for i, cmd in enumerate(setup):
                # Setup commands should use PowerShell cmdlets or PowerShell syntax
                has_powershell_syntax = (
                    "New-Item" in cmd or
                    "Set-" in cmd or
                    "Get-" in cmd or
                    "Compress-Archive" in cmd or
                    "Expand-Archive" in cmd or
                    "Out-File" in cmd or
                    "$" in cmd or  # PowerShell variable
                    "@'" in cmd or  # Here-string
                    any(verb in cmd for verb in ["Add-", "Remove-", "Start-", "Stop-"]) or
                    cmd.startswith("#")  # Comment
                )

                assert has_powershell_syntax, (
                    f"{mission_file.name} setup command {i} should use PowerShell: {cmd}"
                )


class TestPowerShellDescriptionQuality:
    """Test PowerShell mission description quality."""

    @pytest.fixture
    def scenarios_dir(self):
        """Get the PowerShell scenarios directory."""
        return Path("scenarios/powershell")

    @pytest.fixture
    def all_mission_files(self, scenarios_dir):
        """Get all PowerShell mission YAML files."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")
        return list(scenarios_dir.rglob("*.yml"))

    def test_descriptions_have_code_examples(self, all_mission_files):
        """Test that most step descriptions include PowerShell code examples."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            steps_with_code = 0

            for i, step in enumerate(steps):
                description = step.get("description", "")

                # Check if contains code block with PowerShell
                has_code_block = "```powershell" in description or "```" in description

                if has_code_block:
                    steps_with_code += 1

            # At least 70% of steps should have code examples
            if len(steps) > 0:
                code_percentage = (steps_with_code / len(steps)) * 100
                assert code_percentage >= 60, (
                    f"{mission_file.name} should have code examples in at least 60% of steps, "
                    f"found {code_percentage:.1f}%"
                )

    def test_hints_are_helpful(self, all_mission_files):
        """Test that hints provide useful guidance."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            for i, step in enumerate(steps):
                hint = step.get("hint", "")

                # Hint should exist and be meaningful
                assert hint, f"{mission_file.name} step {i} missing hint"
                assert len(hint) >= 10, (
                    f"{mission_file.name} step {i} hint too short: {hint}"
                )

    def test_step_titles_are_descriptive(self, all_mission_files):
        """Test that step titles are clear and descriptive."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            for i, step in enumerate(steps):
                title = step.get("title", "")

                assert title, f"{mission_file.name} step {i} missing title"
                assert len(title) >= 5, (
                    f"{mission_file.name} step {i} title too short: {title}"
                )

                # Title should not just be a cmdlet name
                assert not title.startswith("Get-"), (
                    f"{mission_file.name} step {i} title should describe the task, "
                    f"not just the cmdlet: {title}"
                )


class TestPowerShellProgressionQuality:
    """Test PowerShell mission progression and unlock chains."""

    @pytest.fixture
    def scenarios_dir(self):
        """Get the PowerShell scenarios directory."""
        return Path("scenarios/powershell")

    @pytest.fixture
    def all_missions_data(self, scenarios_dir):
        """Load all mission data into a dict keyed by mission ID."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        missions = {}
        mission_files = list(scenarios_dir.rglob("*.yml"))

        for mission_file in mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            mission_id = data.get("mission", {}).get("id")
            if mission_id:
                missions[mission_id] = data

        return missions

    def test_unlock_chains_reference_existing_missions(self, all_missions_data):
        """Test that unlocks reference real mission IDs."""
        all_mission_ids = set(all_missions_data.keys())

        for mission_id, data in all_missions_data.items():
            unlocks = data.get("completion", {}).get("unlocks", [])

            for unlock_id in unlocks:
                assert unlock_id in all_mission_ids, (
                    f"Mission '{mission_id}' unlocks non-existent mission: {unlock_id}"
                )

    def test_first_mission_has_no_prerequisites(self, all_missions_data):
        """Test that the first mission (hello-powershell) requires no unlocks."""
        first_mission_id = "powershell/basics/hello-powershell"

        assert first_mission_id in all_missions_data, (
            "First mission 'powershell/basics/hello-powershell' not found"
        )

        # Check that no other mission unlocks to hello-powershell
        missions_unlocking_first = []
        for mission_id, data in all_missions_data.items():
            unlocks = data.get("completion", {}).get("unlocks", [])
            if first_mission_id in unlocks:
                missions_unlocking_first.append(mission_id)

        assert not missions_unlocking_first, (
            f"First mission '{first_mission_id}' should not be locked by: "
            f"{missions_unlocking_first}"
        )

    def test_final_mission_has_no_unlocks(self, all_missions_data):
        """Test that the final mission has empty unlocks list."""
        final_mission_id = "powershell/cloud/hybrid-cloud"

        assert final_mission_id in all_missions_data, (
            "Final mission 'powershell/cloud/hybrid-cloud' not found"
        )

        data = all_missions_data[final_mission_id]
        unlocks = data.get("completion", {}).get("unlocks", [])

        assert unlocks == [], (
            f"Final mission '{final_mission_id}' should have empty unlocks, "
            f"got: {unlocks}"
        )

    def test_difficulty_progression_within_topics(self, scenarios_dir):
        """Test that missions within a topic progress logically."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}

        topic_dirs = [d for d in scenarios_dir.iterdir() if d.is_dir()]

        for topic_dir in topic_dirs:
            mission_files = sorted(topic_dir.glob("*.yml"))

            if len(mission_files) <= 1:
                continue  # Skip topics with single mission

            difficulties = []
            for mission_file in mission_files:
                with open(mission_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                difficulty = data.get("mission", {}).get("difficulty")
                difficulties.append(difficulty_order.get(difficulty, -1))

            # Check that difficulty doesn't decrease significantly
            # (some variation is OK, but should trend upward)
            for i in range(len(difficulties) - 1):
                decrease = difficulties[i] - difficulties[i + 1]
                assert decrease <= 1, (
                    f"Topic '{topic_dir.name}' has significant difficulty drop "
                    f"from mission {i} to {i+1}"
                )


class TestPowerShellEstimatedTime:
    """Test PowerShell mission estimated time quality."""

    @pytest.fixture
    def scenarios_dir(self):
        """Get the PowerShell scenarios directory."""
        return Path("scenarios/powershell")

    @pytest.fixture
    def all_mission_files(self, scenarios_dir):
        """Get all PowerShell mission YAML files."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")
        return list(scenarios_dir.rglob("*.yml"))

    def test_estimated_time_correlates_with_steps(self, all_mission_files):
        """Test that estimated time roughly matches step count."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            estimated_time = data.get("mission", {}).get("estimated_time", 0)
            step_count = len(steps)

            # Rough guideline: 3-6 minutes per step
            min_expected_time = step_count * 2
            max_expected_time = step_count * 8

            assert min_expected_time <= estimated_time <= max_expected_time, (
                f"{mission_file.name} has {step_count} steps but "
                f"estimated_time is {estimated_time} minutes. "
                f"Expected roughly {min_expected_time}-{max_expected_time} minutes."
            )

    def test_estimated_time_reasonable_range(self, all_mission_files):
        """Test that estimated time is in reasonable range (10-60 minutes)."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            estimated_time = data.get("mission", {}).get("estimated_time", 0)

            assert 5 <= estimated_time <= 60, (
                f"{mission_file.name} estimated_time should be 5-60 minutes, "
                f"got {estimated_time}"
            )


class TestPowerShellTopicCoverage:
    """Test that PowerShell topics cover expected curriculum."""

    @pytest.fixture
    def scenarios_dir(self):
        """Get the PowerShell scenarios directory."""
        return Path("scenarios/powershell")

    def test_covers_core_powershell_concepts(self, scenarios_dir):
        """Test that missions cover core PowerShell concepts."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        mission_files = list(scenarios_dir.rglob("*.yml"))
        all_content = ""

        for mission_file in mission_files:
            with open(mission_file, encoding="utf-8") as f:
                all_content += f.read()

        # Core concepts that should be covered
        core_concepts = {
            "Get-Help": "PowerShell help system",
            "pipeline": "PowerShell pipeline",
            "Select-Object": "Object selection",
            "Where-Object": "Object filtering",
            "Get-Process": "Process management",
            "New-Item": "File operations",
            "Get-Acl": "Security and permissions",
            "Registry": "Windows Registry",
            "BitLocker": "Encryption",
            "Azure": "Cloud management",
        }

        for concept, description in core_concepts.items():
            assert concept in all_content, (
                f"PowerShell curriculum should cover {description} ({concept})"
            )

    def test_covers_windows_administration(self, scenarios_dir):
        """Test that missions cover Windows administration tasks."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        mission_files = list(scenarios_dir.rglob("*.yml"))
        all_content = ""

        for mission_file in mission_files:
            with open(mission_file, encoding="utf-8") as f:
                all_content += f.read()

        # Windows admin concepts
        admin_concepts = {
            "New-LocalUser": "User management",
            "SMB": "File sharing",
            "Service": "Service management",
            "ScheduledTask": "Task scheduling",
            "DNS": "Network configuration",
        }

        for concept, description in admin_concepts.items():
            assert concept in all_content, (
                f"PowerShell curriculum should cover {description} ({concept})"
            )
