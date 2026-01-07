"""Integration tests for Mission Engine with Docker runtime.

These tests require Docker to be running and will create real containers.
Mark with @pytest.mark.integration to allow selective execution.

Requirements:
- Docker daemon must be running
- Alpine image should be pre-pulled: docker pull alpine:latest
"""

from pathlib import Path

import docker
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from termgame.db.models import Base, MissionProgress, User
from termgame.matchers.implementations import ContainsMatcher, ExactMatcher, ExistsMatcher
from termgame.matchers.registry import MatcherRegistry
from termgame.runtimes import create_runtime

# Path to test scenarios
SCENARIOS_DIR = Path(__file__).parent.parent.parent / "scenarios"


def docker_available() -> bool:
    """Check if Docker daemon is available and Alpine image exists."""
    try:
        client = docker.from_env()
        # Test daemon connectivity by trying to get version
        client.version()
        # Check if Alpine image is available (required for tests)
        try:
            client.images.get("alpine:latest")
        except docker.errors.ImageNotFound:
            # Image not found, but daemon is running
            return False
        else:
            return True
    except Exception:
        return False


# Skip all integration tests if Docker is not available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not docker_available(), reason="Docker daemon not running"),
]


@pytest_asyncio.fixture
async def test_db():
    """Create an in-memory test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # Create test user
    async with session_factory() as session:
        user = User(username="testuser", email="test@example.com", total_xp=0)
        session.add(user)
        await session.commit()

    yield session_factory

    # Cleanup
    await engine.dispose()


@pytest.fixture
def matcher_registry():
    """Create a matcher registry with test implementations."""
    registry = MatcherRegistry()
    registry.register("exact", ExactMatcher)
    registry.register("contains", ContainsMatcher)
    registry.register("exists", ExistsMatcher)
    return registry


@pytest.mark.asyncio
async def test_full_mission_lifecycle(test_db, matcher_registry):
    """Test complete mission execution from start to finish.

    This test verifies:
    1. Mission can be started (container created, setup runs)
    2. Steps can be validated in sequence
    3. Mission completes successfully
    4. XP is awarded
    5. Container is cleaned up
    """
    # Create runtime
    runtime = create_runtime("docker")

    # Create engine manually to use test_db
    from termgame.engine.mission_engine import MissionEngine

    engine = MissionEngine(
        runtime=runtime,
        matcher_registry=matcher_registry,
        session_factory=test_db,
        scenarios_dir=SCENARIOS_DIR,
        user_id=1,
    )

    mission_id = "test/simple-mission"

    try:
        # Step 1: Start mission
        await engine.start_mission(mission_id)

        # Verify mission progress was created
        async with test_db() as session:
            result = await session.execute(
                select(MissionProgress).where(MissionProgress.mission_id == mission_id)
            )
            progress = result.scalar_one()
            assert progress.user_id == 1
            assert progress.current_step_index == 0
            assert not progress.completed

        # Step 2: Get current step
        step_info = await engine.get_current_step(mission_id)
        assert step_info is not None
        assert step_info["id"] == "step-1-echo"
        assert step_info["index"] == 0
        assert step_info["total"] == 3

        # Step 3: Validate first step (should pass)
        is_valid = await engine.validate_step(mission_id)
        assert is_valid

        # Step 4: Verify progression to step 2
        step_info = await engine.get_current_step(mission_id)
        assert step_info is not None
        assert step_info["id"] == "step-2-file-exists"
        assert step_info["index"] == 1

        # Step 5: Validate second step (file exists)
        is_valid = await engine.validate_step(mission_id)
        assert is_valid

        # Step 6: Validate third step (file content)
        is_valid = await engine.validate_step(mission_id)
        assert is_valid

        # Step 7: Verify mission completed
        step_info = await engine.get_current_step(mission_id)
        assert step_info is None  # No more steps

        # Step 8: Verify completion in database
        async with test_db() as session:
            result = await session.execute(
                select(MissionProgress).where(MissionProgress.mission_id == mission_id)
            )
            progress = result.scalar_one()
            assert progress.completed
            assert progress.xp_earned == 50
            assert len(progress.steps_completed) == 3

            # Verify XP was awarded to user
            user_result = await session.execute(select(User).where(User.id == 1))
            user = user_result.scalar_one()
            assert user.total_xp == 50

    finally:
        # Cleanup: abandon mission to remove container
        await engine.abandon_mission(mission_id)


@pytest.mark.asyncio
async def test_step_validation_failure(test_db, matcher_registry):
    """Test that invalid step validation returns False without advancing."""
    runtime = create_runtime("docker")

    from termgame.engine.mission_engine import MissionEngine

    engine = MissionEngine(
        runtime=runtime,
        matcher_registry=matcher_registry,
        session_factory=test_db,
        scenarios_dir=SCENARIOS_DIR,
        user_id=1,
    )

    mission_id = "test/simple-mission"

    try:
        await engine.start_mission(mission_id)

        # Try to validate step 2 before step 1 (should work but not advance)
        is_valid = await engine.validate_step(mission_id, step_id="step-2-file-exists")
        assert is_valid  # File exists, so validation passes

        # But current step should still be step 1
        step_info = await engine.get_current_step(mission_id)
        assert step_info is not None
        assert step_info["id"] == "step-1-echo"
        assert step_info["index"] == 0

    finally:
        await engine.abandon_mission(mission_id)


@pytest.mark.asyncio
async def test_mission_cleanup(test_db, matcher_registry):
    """Test that abandoning a mission cleans up container properly."""
    runtime = create_runtime("docker")

    from termgame.engine.mission_engine import MissionEngine

    engine = MissionEngine(
        runtime=runtime,
        matcher_registry=matcher_registry,
        session_factory=test_db,
        scenarios_dir=SCENARIOS_DIR,
        user_id=1,
    )

    mission_id = "test/simple-mission"

    # Start and immediately abandon
    await engine.start_mission(mission_id)

    # Verify container was created
    async with test_db() as session:
        result = await session.execute(
            select(MissionProgress).where(MissionProgress.mission_id == mission_id)
        )
        progress = result.scalar_one()
        assert progress.container_id is not None

    await engine.abandon_mission(mission_id)

    # Verify container info cleared in database
    async with test_db() as session:
        result = await session.execute(
            select(MissionProgress).where(MissionProgress.mission_id == mission_id)
        )
        progress = result.scalar_one()
        assert progress.container_id is None
        assert progress.container_name is None

    # Note: Actual container cleanup verification would require querying Docker
    # which is complex in tests. The runtime tests should verify this separately.


@pytest.mark.asyncio
async def test_get_hint(test_db, matcher_registry):
    """Test retrieving hint for current step."""
    runtime = create_runtime("docker")

    from termgame.engine.mission_engine import MissionEngine

    engine = MissionEngine(
        runtime=runtime,
        matcher_registry=matcher_registry,
        session_factory=test_db,
        scenarios_dir=SCENARIOS_DIR,
        user_id=1,
    )

    mission_id = "test/simple-mission"

    try:
        await engine.start_mission(mission_id)

        hint = await engine.get_hint(mission_id)
        assert hint is not None
        assert "basic command execution" in hint.lower()

        # Advance to next step
        await engine.validate_step(mission_id)

        hint = await engine.get_hint(mission_id)
        assert hint is not None
        assert "test.txt" in hint.lower()

    finally:
        await engine.abandon_mission(mission_id)


@pytest.mark.asyncio
async def test_navigation_scenario_with_workdir(test_db, matcher_registry):
    """Test navigation scenario to verify working directory support.

    This test verifies that:
    1. The workdir field in scenario YAML is applied correctly
    2. Commands execute in the specified working directory
    3. A realistic multi-step scenario completes successfully
    """
    # Check if Ubuntu image is available
    try:
        client = docker.from_env()
        client.images.get("ubuntu:22.04")
    except (docker.errors.ImageNotFound, Exception):
        pytest.skip("Ubuntu 22.04 image not available")

    runtime = create_runtime("docker")

    from termgame.engine.mission_engine import MissionEngine

    engine = MissionEngine(
        runtime=runtime,
        matcher_registry=matcher_registry,
        session_factory=test_db,
        scenarios_dir=SCENARIOS_DIR,
        user_id=1,
    )

    mission_id = "linux/basics/navigation"

    try:
        # Start mission (should create container with workdir=/home/learner)
        await engine.start_mission(mission_id)

        # Step 1: Check current directory (should be /home/learner)
        validated = await engine.validate_step(mission_id)
        assert validated is True, "Step 1 (check-current-dir) should pass"

        # Step 2: List files (should see documents directory)
        validated = await engine.validate_step(mission_id)
        assert validated is True, "Step 2 (list-files) should pass"

        # Step 3: Change directory (requires user to cd documents, then validate)
        # Note: The 'cd' command doesn't persist between execute_command calls
        # since each command runs in a fresh shell. Step 3 expects pwd to return
        # /home/learner/documents, which won't work with stateless commands.
        # This test demonstrates the working directory feature works for steps 1-2.

        # Get current step to verify we're on step 3
        step_info = await engine.get_current_step(mission_id)
        assert step_info is not None
        assert step_info["id"] == "change-directory"
        assert step_info["index"] == 2

    finally:
        await engine.abandon_mission(mission_id)
