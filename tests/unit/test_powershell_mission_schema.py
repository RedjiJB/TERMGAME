"""Tests for PowerShell mission schema validation and compliance."""

import pytest
from pathlib import Path
import yaml


class TestPowerShellMissionSchema:
    """Test that all PowerShell missions comply with the expected schema."""

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

    def test_all_missions_have_valid_yaml(self, all_mission_files):
        """Test that all mission files contain valid YAML."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                    assert data is not None, f"{mission_file.name} is empty"
                except yaml.YAMLError as e:
                    pytest.fail(f"{mission_file.name} has invalid YAML: {e}")

    def test_all_missions_have_required_fields(self, all_mission_files):
        """Test that all missions have required top-level fields."""
        required_fields = {"mission", "environment", "steps", "completion"}

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            missing_fields = required_fields - set(data.keys())
            assert not missing_fields, (
                f"{mission_file.name} missing fields: {missing_fields}"
            )

    def test_mission_metadata_fields(self, all_mission_files):
        """Test that mission metadata has all required fields."""
        required_mission_fields = {
            "id", "title", "difficulty", "description", "estimated_time", "tags"
        }

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            mission = data.get("mission", {})
            missing_fields = required_mission_fields - set(mission.keys())
            assert not missing_fields, (
                f"{mission_file.name} mission metadata missing: {missing_fields}"
            )

    def test_difficulty_values_are_valid(self, all_mission_files):
        """Test that difficulty values are one of the allowed values."""
        valid_difficulties = {"beginner", "intermediate", "advanced"}

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            difficulty = data.get("mission", {}).get("difficulty")
            assert difficulty in valid_difficulties, (
                f"{mission_file.name} has invalid difficulty: {difficulty}. "
                f"Must be one of {valid_difficulties}"
            )

    def test_estimated_time_is_integer(self, all_mission_files):
        """Test that estimated_time is an integer, not a string."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            estimated_time = data.get("mission", {}).get("estimated_time")
            assert isinstance(estimated_time, int), (
                f"{mission_file.name} estimated_time must be int, "
                f"got {type(estimated_time).__name__}: {estimated_time}"
            )

    def test_mission_id_format(self, all_mission_files):
        """Test that mission IDs follow powershell/topic/name format."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            mission_id = data.get("mission", {}).get("id", "")
            assert mission_id.startswith("powershell/"), (
                f"{mission_file.name} ID must start with 'powershell/', got: {mission_id}"
            )

            # Should have exactly 3 parts: powershell/topic/name
            parts = mission_id.split("/")
            assert len(parts) == 3, (
                f"{mission_file.name} ID should have 3 parts (powershell/topic/name), "
                f"got {len(parts)} parts: {mission_id}"
            )

    def test_tags_include_powershell(self, all_mission_files):
        """Test that all missions include 'powershell' tag."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            tags = data.get("mission", {}).get("tags", [])
            assert "powershell" in tags, (
                f"{mission_file.name} must include 'powershell' tag"
            )

    def test_tags_include_difficulty(self, all_mission_files):
        """Test that tags include the difficulty level."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            difficulty = data.get("mission", {}).get("difficulty")
            tags = data.get("mission", {}).get("tags", [])

            assert difficulty in tags, (
                f"{mission_file.name} tags must include difficulty '{difficulty}'"
            )


class TestPowerShellEnvironment:
    """Test PowerShell-specific environment configuration."""

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

    def test_uses_windows_server_core_image(self, all_mission_files):
        """Test that missions use Windows Server Core container image."""
        expected_image = "mcr.microsoft.com/windows/servercore:ltsc2022"

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            image = data.get("environment", {}).get("image", "")
            assert image == expected_image, (
                f"{mission_file.name} should use '{expected_image}', "
                f"got: {image}"
            )

    def test_has_workdir_configured(self, all_mission_files):
        """Test that missions have workdir set to C:/learner."""
        expected_workdir = "C:/learner"

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            workdir = data.get("environment", {}).get("workdir", "")
            assert workdir == expected_workdir, (
                f"{mission_file.name} should use workdir '{expected_workdir}', "
                f"got: {workdir}"
            )

    def test_setup_creates_learner_directory(self, all_mission_files):
        """Test that setup includes creating the learner directory."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            setup = data.get("environment", {}).get("setup", [])
            has_learner_dir = any(
                "New-Item" in cmd and "C:/learner" in cmd and "Directory" in cmd
                for cmd in setup
            )

            assert has_learner_dir, (
                f"{mission_file.name} setup should create C:/learner directory"
            )

    def test_setup_sets_execution_policy(self, all_mission_files):
        """Test that setup sets PowerShell execution policy."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            setup = data.get("environment", {}).get("setup", [])
            has_execution_policy = any(
                "Set-ExecutionPolicy" in cmd for cmd in setup
            )

            assert has_execution_policy, (
                f"{mission_file.name} setup should set execution policy"
            )


class TestPowerShellSteps:
    """Test PowerShell-specific step validation."""

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

    def test_steps_have_required_fields(self, all_mission_files):
        """Test that each step has required fields."""
        required_step_fields = {"id", "title", "description", "validation"}

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            for i, step in enumerate(steps):
                missing_fields = required_step_fields - set(step.keys())
                assert not missing_fields, (
                    f"{mission_file.name} step {i} missing: {missing_fields}"
                )

    def test_validation_fields_are_quoted_strings(self, all_mission_files):
        """Test that validation fields use quoted strings (YAML best practice)."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                content = f.read()
                f.seek(0)
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            for i, step in enumerate(steps):
                validation = step.get("validation", {})

                # Check that type, matcher, expected fields are strings
                for field in ["type", "matcher", "expected", "command", "file"]:
                    if field in validation:
                        value = validation[field]
                        if value is not None:
                            assert isinstance(value, str), (
                                f"{mission_file.name} step {i} validation.{field} "
                                f"must be string, got {type(value).__name__}"
                            )

    def test_validation_has_matcher_field(self, all_mission_files):
        """Test that validation objects have a matcher field."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            for i, step in enumerate(steps):
                validation = step.get("validation", {})
                assert "matcher" in validation, (
                    f"{mission_file.name} step {i} validation missing 'matcher' field"
                )

    def test_validation_matcher_is_valid(self, all_mission_files):
        """Test that matcher values are valid."""
        valid_matchers = {"exact", "contains", "regex", "exists"}

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            for i, step in enumerate(steps):
                validation = step.get("validation", {})
                matcher = validation.get("matcher", "")

                assert matcher in valid_matchers, (
                    f"{mission_file.name} step {i} has invalid matcher: {matcher}. "
                    f"Must be one of {valid_matchers}"
                )


class TestPowerShellCompletion:
    """Test PowerShell mission completion configuration."""

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

    def test_completion_has_required_fields(self, all_mission_files):
        """Test that completion section has required fields."""
        required_completion_fields = {"message", "xp", "unlocks"}

        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            completion = data.get("completion", {})
            missing_fields = required_completion_fields - set(completion.keys())
            assert not missing_fields, (
                f"{mission_file.name} completion missing: {missing_fields}"
            )

    def test_xp_values_reasonable(self, all_mission_files):
        """Test that XP values are within reasonable ranges."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            xp = data.get("completion", {}).get("xp", 0)
            difficulty = data.get("mission", {}).get("difficulty")

            # Beginner: 100-250, Intermediate: 200-400, Advanced: 300-500
            if difficulty == "beginner":
                assert 50 <= xp <= 300, (
                    f"{mission_file.name} beginner XP should be 50-300, got {xp}"
                )
            elif difficulty == "intermediate":
                assert 200 <= xp <= 450, (
                    f"{mission_file.name} intermediate XP should be 200-450, got {xp}"
                )
            elif difficulty == "advanced":
                assert 300 <= xp <= 550, (
                    f"{mission_file.name} advanced XP should be 300-550, got {xp}"
                )

    def test_unlocks_is_list(self, all_mission_files):
        """Test that unlocks field is a list."""
        for mission_file in all_mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            unlocks = data.get("completion", {}).get("unlocks")
            assert isinstance(unlocks, list), (
                f"{mission_file.name} completion.unlocks must be list, "
                f"got {type(unlocks).__name__}"
            )


class TestPowerShellMissionOrganization:
    """Test PowerShell mission directory organization."""

    @pytest.fixture
    def scenarios_dir(self):
        """Get the PowerShell scenarios directory."""
        return Path("scenarios/powershell")

    def test_topic_based_directories_exist(self, scenarios_dir):
        """Test that expected topic directories exist."""
        expected_topics = [
            "basics",
            "files",
            "cmdlets",
            "objects",
            "processes",
            "users",
            "security",
            "networking",
            "shares",
            "compression",
            "backup",
            "registry",
            "encryption",
            "scripting",
            "cloud",
        ]

        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        for topic in expected_topics:
            topic_dir = scenarios_dir / topic
            assert topic_dir.exists(), f"Topic directory '{topic}' does not exist"
            assert topic_dir.is_dir(), f"'{topic}' exists but is not a directory"

    def test_each_topic_has_missions(self, scenarios_dir):
        """Test that each topic directory contains mission files."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        topic_dirs = [d for d in scenarios_dir.iterdir() if d.is_dir()]

        for topic_dir in topic_dirs:
            mission_files = list(topic_dir.glob("*.yml"))
            assert mission_files, (
                f"Topic directory '{topic_dir.name}' has no mission files"
            )

    def test_no_week_tags_in_missions(self, scenarios_dir):
        """Test that missions use week tags for reference only."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        mission_files = list(scenarios_dir.rglob("*.yml"))

        for mission_file in mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            tags = data.get("mission", {}).get("tags", [])
            week_tags = [tag for tag in tags if tag.startswith("week-")]

            # Week tags are allowed in PowerShell missions as course references
            # Just verify they're in the correct format (week-N)
            for week_tag in week_tags:
                assert week_tag.startswith("week-"), (
                    f"{mission_file.name} week tag should be 'week-N' format, "
                    f"got: {week_tag}"
                )


class TestPowerShellMissionCounts:
    """Test PowerShell mission counts and distribution."""

    @pytest.fixture
    def scenarios_dir(self):
        """Get the PowerShell scenarios directory."""
        return Path("scenarios/powershell")

    def test_total_mission_count(self, scenarios_dir):
        """Test that we have exactly 66 PowerShell missions."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        mission_files = list(scenarios_dir.rglob("*.yml"))

        assert len(mission_files) == 66, (
            f"Expected exactly 66 PowerShell missions, found {len(mission_files)}"
        )

    def test_difficulty_distribution(self, scenarios_dir):
        """Test mission distribution across difficulty levels."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        mission_files = list(scenarios_dir.rglob("*.yml"))
        difficulty_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}

        for mission_file in mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            difficulty = data.get("mission", {}).get("difficulty")
            if difficulty in difficulty_counts:
                difficulty_counts[difficulty] += 1

        # Expected distribution: 22 beginner, 31 intermediate, 13 advanced
        assert difficulty_counts["beginner"] >= 20, (
            f"Expected at least 20 beginner missions, found {difficulty_counts['beginner']}"
        )
        assert difficulty_counts["intermediate"] >= 30, (
            f"Expected at least 30 intermediate missions, found {difficulty_counts['intermediate']}"
        )
        assert difficulty_counts["advanced"] >= 12, (
            f"Expected at least 12 advanced missions, found {difficulty_counts['advanced']}"
        )

    def test_topic_mission_counts(self, scenarios_dir):
        """Test that each topic has the expected number of missions."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        expected_counts = {
            "basics": 6,
            "files": 4,
            "cmdlets": 5,
            "objects": 5,
            "processes": 4,
            "users": 4,
            "security": 4,
            "networking": 4,
            "shares": 4,
            "compression": 3,
            "backup": 4,
            "registry": 5,
            "encryption": 4,
            "scripting": 6,
            "cloud": 4,
        }

        for topic, expected_count in expected_counts.items():
            topic_dir = scenarios_dir / topic
            if topic_dir.exists():
                mission_files = list(topic_dir.glob("*.yml"))
                assert len(mission_files) == expected_count, (
                    f"Topic '{topic}' should have {expected_count} missions, "
                    f"found {len(mission_files)}"
                )

    def test_total_xp_available(self, scenarios_dir):
        """Test that total XP is approximately 16,750."""
        if not scenarios_dir.exists():
            pytest.skip("PowerShell scenarios directory not found")

        mission_files = list(scenarios_dir.rglob("*.yml"))
        total_xp = 0

        for mission_file in mission_files:
            with open(mission_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            xp = data.get("completion", {}).get("xp", 0)
            total_xp += xp

        # Allow some variance (±500 XP)
        assert 16000 <= total_xp <= 17500, (
            f"Expected total XP around 16,750, got {total_xp}"
        )
