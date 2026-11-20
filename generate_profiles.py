import itertools
import json

# 3 goals x 2 levels x 3 equipment types x 2 schedules = 36 users
GOALS = ["strength", "muscle_gain", "general_fitness"]
LEVELS = ["beginner", "intermediate"]
EQUIPMENT_TYPES = ["bodyweight", "bands_other", "dumbbell"]
SCHEDULES = ["3_days_per_week", "5_days_per_week"]

profiles = []

for number, (goal, level, equipment, schedule) in enumerate(
    itertools.product(GOALS, LEVELS, EQUIPMENT_TYPES, SCHEDULES),
    start=1
):
    profiles.append({
        "profile_id": f"U{number:02d}",
        "goal": goal,
        "level": level,
        "equipment": equipment,
        "schedule": schedule
    })

with open("profiles.json", "w", encoding="utf-8") as file:
    json.dump(profiles, file, indent=2)

print(f"Created profiles.json with {len(profiles)} test users.")
