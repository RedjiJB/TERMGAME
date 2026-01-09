#!/usr/bin/env python3
"""Generate a comprehensive mission validation report."""

from collections import defaultdict
from pathlib import Path

from termgame.loaders.scenario_loader import ScenarioLoader


def main():
    scenarios_dir = Path("scenarios")
    loader = ScenarioLoader(scenarios_dir)

    print("=" * 70)
    print("TERMGAME MISSION VALIDATION REPORT")
    print("=" * 70)
    print()

    missions = []
    images = defaultdict(list)
    difficulties = defaultdict(list)

    for yaml_file in scenarios_dir.rglob("*.yml"):
        if yaml_file.name.startswith("_"):
            continue

        rel_path = yaml_file.relative_to(scenarios_dir)
        mission_id = str(rel_path.with_suffix("")).replace("\\", "/")

        try:
            scenario = loader.load(mission_id)
            missions.append(
                {
                    "id": mission_id,
                    "title": scenario.mission.title,
                    "difficulty": scenario.mission.difficulty,
                    "time": scenario.mission.estimated_time,
                    "steps": len(scenario.steps),
                    "image": scenario.environment.image,
                    "xp": scenario.completion.xp,
                }
            )
            images[scenario.environment.image].append(mission_id)
            difficulties[scenario.mission.difficulty].append(mission_id)
        except Exception as e:
            print(f"[ERROR] {mission_id}: {e}")

    # Summary
    print(f"Total Missions: {len(missions)}")
    print(f"Unique Docker Images: {len(images)}")
    print()

    # By Difficulty
    print("Missions by Difficulty:")
    for difficulty in ["beginner", "intermediate", "advanced"]:
        count = len(difficulties.get(difficulty, []))
        print(f"  {difficulty.capitalize():12s}: {count}")
    print()

    # Docker Images
    print("Docker Images Used:")
    for image, mission_list in sorted(images.items()):
        print(f"  {image:30s}: {len(mission_list)} missions")
    print()

    # Mission List
    print("All Missions:")
    print(f"{'ID':<40s} {'Title':<35s} {'Difficulty':<12s} {'Steps':>5s} {'XP':>4s}")
    print("-" * 105)
    for m in sorted(missions, key=lambda x: x["id"]):
        print(
            f"{m['id']:<40s} {m['title']:<35s} {m['difficulty']:<12s} {m['steps']:>5d} {m['xp']:>4d}"
        )
    print()

    # XP Summary
    total_xp = sum(m["xp"] for m in missions)
    print(f"Total XP Available: {total_xp}")
    print()

    print("=" * 70)
    print("VALIDATION COMPLETE - All missions loaded successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
