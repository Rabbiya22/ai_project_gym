
import heapq
from itertools import count, combinations

from exercise_filter import load_exercises, filter_exercises
from weekly_split import dfs_split, DAY_NAMES, MUSCLE_GROUPS

from plan_checker import (
    check_R0,
    get_age_message,
    check_plan,
    MAX_SESSION_MINUTES,
    ALLOWED_EQUIPMENT
)


# ==================================================
# PROJECT SETTINGS
# ==================================================

SETS = 3
MIN_SESSION_TARGET = 35
MAX_SESSION_TARGET = 45

PROJECT_EQUIPMENT = ALLOWED_EQUIPMENT

SUPPORTED_LEVELS = ("beginner", "intermediate")

LEVEL_RANK = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3
}

RULE_NAMES = [
    "R0_Age_Eligibility",
    "R1_Equipment",
    "R2_Difficulty",
    "R3_Session_Duration",
    "R4_Muscle_Recovery",
    "R5_No_Repeats",
    "R6_Weekly_Sets"
]


# ==================================================
# CUSTOMER PROFILE
# ==================================================

def get_customer_profile():

    while True:
        try:
            age = int(input("Enter your age: "))

            profile = {
                "age": age,
                "equipment": PROJECT_EQUIPMENT,
                "session_minutes": MAX_SESSION_TARGET,
                "min_session_minutes": MIN_SESSION_TARGET
            }

            if not check_R0(profile):
                print(get_age_message(age))
                continue

            break

        except ValueError:
            print("Please enter a valid whole-number age.")

    print("\nChoose your workout difficulty level:")
    print("1 = Beginner")
    print("2 = Intermediate")

    while True:

        level_choice = input("Enter 1 or 2: ").strip()

        if level_choice == "1":
            profile["level"] = "beginner"
            break

        elif level_choice == "2":
            profile["level"] = "intermediate"
            break

        else:
            print(
                "Invalid choice. Please enter 1 for Beginner "
                "or 2 for Intermediate."
            )

    return profile


# ==================================================
# USER AVAILABILITY
# ==================================================

def get_user_availability():

    print("\nChoose your preferred workout days.")
    print("0 = Monday")
    print("1 = Tuesday")
    print("2 = Wednesday")
    print("3 = Thursday")
    print("4 = Friday")
    print("5 = Saturday")
    print("Sunday is closed.")

    while True:

        try:

            entered_days = input(
                "\nEnter day numbers separated by commas: "
            )

            preferred_days = [
                int(day.strip())
                for day in entered_days.split(",")
            ]

            if not 2 <= len(preferred_days) <= 6:
                print("Please select between 2 and 6 days.")
                continue

            if len(set(preferred_days)) != len(preferred_days):
                print("You cannot select the same day twice.")
                continue

            if any(day < 0 or day > 5 for day in preferred_days):
                print("Choose days from 0 to 5 only.")
                continue

            return sorted(preferred_days)

        except ValueError:
            print("Enter valid day numbers separated by commas.")


# ==================================================
# VALIDATE DATASET IDS
# ==================================================

def validate_unique_ids(exercises):

    seen_ids = set()

    for exercise in exercises:

        exercise_id = str(
            exercise.get("id", "")
        ).strip()

        if not exercise_id:
            raise ValueError("An exercise is missing its ID.")

        if exercise_id in seen_ids:
            raise ValueError(
                f"Duplicate exercise ID found: {exercise_id}"
            )

        seen_ids.add(exercise_id)

    return True


# ==================================================
# PREPARE EXERCISE DATA
# ==================================================

def prepare_exercise(exercise):

    primary = str(
        exercise.get("primary_muscle", "")
    ).strip().lower()

    secondary = exercise.get("secondary_muscles", "")

    if isinstance(secondary, str):
        secondary = secondary.replace(",", ";").split(";")

    secondary = [
        muscle.strip().lower()
        for muscle in secondary
        if isinstance(muscle, str) and muscle.strip()
    ]

    try:
        minutes = float(
            exercise.get("minutes_per_set", 0)
        )

    except (ValueError, TypeError):
        minutes = 0

    prepared = exercise.copy()

    prepared["id"] = str(
        exercise.get("id", "")
    ).strip()

    prepared["name"] = str(
        exercise.get("name", "")
    ).strip()

    prepared["primary_muscle"] = primary
    prepared["secondary_muscles"] = secondary

    prepared["equipment"] = str(
        exercise.get("equipment", "")
    ).strip().lower()

    prepared["level"] = str(
        exercise.get("level", "")
    ).strip().lower()

    prepared["minutes_per_set"] = minutes
    prepared["sets"] = SETS

    return prepared


# ==================================================
# CHECK EXERCISE SUITABILITY
# ==================================================

def is_suitable_exercise(exercise, profile):

    equipment = exercise["equipment"]
    level = exercise["level"]
    minutes = exercise["minutes_per_set"]

    if equipment not in PROJECT_EQUIPMENT:
        return False

    if level not in LEVEL_RANK:
        return False

    if LEVEL_RANK[level] > LEVEL_RANK[profile["level"]]:
        return False

    if minutes <= 0:
        return False

    if not exercise["id"] or not exercise["name"]:
        return False

    if exercise["primary_muscle"] not in MUSCLE_GROUPS:
        return False

    return True


# ==================================================
# GET PRIMARY AND SECONDARY MUSCLES
# ==================================================

def get_active_muscles(exercise):

    active = set()

    primary = exercise.get(
        "primary_muscle", ""
    )

    if primary:
        active.add(primary.strip().lower())

    secondary = exercise.get(
        "secondary_muscles", []
    )

    if isinstance(secondary, str):
        secondary = secondary.replace(",", ";").split(";")

    for muscle in secondary:

        if isinstance(muscle, str) and muscle.strip():
            active.add(muscle.strip().lower())

    return active


# ==================================================
# CALCULATE EXERCISE TIME
# ==================================================

def exercise_time(exercise):

    return (
        exercise["minutes_per_set"]
        * exercise["sets"]
    )


# ==================================================
# SESSION BUILDER - A* SEARCH
# ==================================================

def build_session(
    target_muscles,
    suitable_exercises,
    blocked_muscles,
    used_exercise_ids=None
):

    if not target_muscles:
        return None

    if used_exercise_ids is None:
        used_exercise_ids = set()

    # 1. Find available exercises for each target muscle.

    candidates = {}

    for muscle in target_muscles:

        candidates[muscle] = [
            exercise
            for exercise in suitable_exercises
            if exercise["primary_muscle"] == muscle
            and muscle not in blocked_muscles
            and exercise["id"] not in used_exercise_ids
        ]

        if not candidates[muscle]:
            print(f"No available exercises for {muscle}")
            return None

    # 2. Create options: one or two exercises per muscle.

    muscle_options = {}

    for muscle in target_muscles:

        available = candidates[muscle]

        options = (
            [(exercise,) for exercise in available]
            + list(combinations(available, 2))
        )

        valid_options = []

        for option in options:

            option_time = sum(
                exercise_time(exercise)
                for exercise in option
            )

            if option_time <= MAX_SESSION_TARGET:
                valid_options.append(option)

        if not valid_options:
            return None

        muscle_options[muscle] = valid_options

    # 3. Calculate minimum and maximum possible time.

    min_time_per_muscle = {}
    max_time_per_muscle = {}

    for muscle in target_muscles:

        option_times = [
            sum(
                exercise_time(exercise)
                for exercise in option
            )
            for option in muscle_options[muscle]
        ]

        min_time_per_muscle[muscle] = min(option_times)
        max_time_per_muscle[muscle] = max(option_times)

    # 4. A* SEARCH
    #
    # State:
    # muscle_index = next muscle to process
    # current_time = accumulated exercise time
    # selected = selected exercises
    #
    # g(n) = accumulated time
    # h(n) = minimum possible time for remaining muscles
    # f(n) = g(n) + h(n)

    open_list = []
    counter = count()

    initial_h = sum(
        min_time_per_muscle[muscle]
        for muscle in target_muscles
    )

    heapq.heappush(
        open_list,
        (
            initial_h,
            next(counter),
            0,
            0,
            []
        )
    )

    while open_list:

        f_score, _, muscle_index, current_time, selected = (
            heapq.heappop(open_list)
        )

        # 5. GOAL TEST

        if muscle_index == len(target_muscles):

            if MIN_SESSION_TARGET <= current_time <= MAX_SESSION_TARGET:
                return selected

            continue

        # 6. Process the next target muscle.

        muscle = target_muscles[muscle_index]

        for option in muscle_options[muscle]:

            option_time = sum(
                exercise_time(exercise)
                for exercise in option
            )

            new_time = current_time + option_time

            if new_time > MAX_SESSION_TARGET:
                continue

            next_index = muscle_index + 1

            # 7. Calculate remaining heuristic.

            remaining_muscles = target_muscles[next_index:]

            remaining_minimum = sum(
                min_time_per_muscle[m]
                for m in remaining_muscles
            )

            remaining_maximum = sum(
                max_time_per_muscle[m]
                for m in remaining_muscles
            )

            # 8. PRUNING

            if new_time + remaining_maximum < MIN_SESSION_TARGET:
                continue

            if new_time + remaining_minimum > MAX_SESSION_TARGET:
                continue

            new_selected = selected + list(option)

            # 9. Calculate A* priority.

            h_score = remaining_minimum
            new_f = new_time + h_score

            heapq.heappush(
                open_list,
                (
                    new_f,
                    next(counter),
                    next_index,
                    new_time,
                    new_selected
                )
            )

    return None


# ==================================================
# DISPLAY WEEKLY SET TOTALS
# ==================================================

def show_weekly_sets(plan):

    weekly_sets = {
        muscle: 0
        for muscle in MUSCLE_GROUPS
    }

    for day in plan:

        for exercise in day["exercises"]:

            muscle = exercise["primary_muscle"]
            sets = exercise["sets"]

            if muscle in weekly_sets:
                weekly_sets[muscle] += sets

    print("\nWEEKLY SET TOTALS")

    for muscle, total in weekly_sets.items():
        print(f"{muscle}: {total} sets")

    return weekly_sets


# ==================================================
# DISPLAY GENERATED PLAN
# ==================================================

def display_plan(plan):

    print("\n" + "=" * 45)
    print("GENERATED WEEKLY WORKOUT PLAN")
    print("=" * 45)

    for day in plan:

        day_name = DAY_NAMES[day["day_index"]]

        print(f"\n{day_name}")

        total_time = 0

        for exercise in day["exercises"]:

            duration = exercise_time(exercise)
            total_time += duration

            print(
                f"- {exercise['name']} "
                f"({exercise['sets']} sets, "
                f"{duration:g} minutes)"
            )

        print(
            f"Total session time: {total_time:g} minutes"
        )


# ==================================================
# FINAL RULE VALIDATION
# ==================================================

def validate_final_plan(generated_plan, profile):

    print("\n" + "=" * 45)
    print("FINAL RULE VALIDATION")
    print("=" * 45)

    result = check_plan(generated_plan, profile)

    all_rules_pass = True

    for rule in RULE_NAMES:

        status = result.get(rule)

        if status is True:
            print(f"{rule}: PASS")

        elif status is False:
            print(f"{rule}: FAIL")
            all_rules_pass = False

        else:
            print(f"{rule}: NOT CHECKED")
            all_rules_pass = False

    print("\n" + "=" * 45)

    if all_rules_pass:
        print("FINAL RESULT: PLAN APPROVED")

    else:
        print("FINAL RESULT: PLAN NOT APPROVED")

    print("=" * 45)

    return all_rules_pass


# ==================================================
# MAIN PROGRAM
# ==================================================

def main():

    print("=" * 45)
    print("AI WORKOUT PLANNER")
    print("=" * 45)

    # 1. Get customer profile.

    profile = get_customer_profile()

    # 2. Get preferred workout days.

    preferred_days = get_user_availability()

    # 3. Load dataset.

    try:

        raw_exercises = load_exercises()

        if not raw_exercises:
            print("The exercise dataset is empty.")
            return

        validate_unique_ids(raw_exercises)

    except (FileNotFoundError, ValueError) as error:

        print("Dataset error:", error)
        return

    print(
        f"\nTotal exercises in dataset: "
        f"{len(raw_exercises)}"
    )

    # 4. Filter exercises by level.

    filtered_exercises = filter_exercises(
        raw_exercises,
        profile
    )

    # 5. Prepare and validate exercises.

    suitable_exercises = []

    for exercise in filtered_exercises:

        prepared = prepare_exercise(exercise)

        if is_suitable_exercise(prepared, profile):
            suitable_exercises.append(prepared)

    print(
        f"Suitable {profile['level']} exercises: "
        f"{len(suitable_exercises)}"
    )

    if not suitable_exercises:
        print("No suitable exercises were found.")
        return

    # 6. Generate weekly muscle split using DFS.

    weekly_split = dfs_split(
        len(preferred_days),
        preferred_days
    )

    if weekly_split is None:
        print("DFS could not create a weekly split.")
        return

    print("\nDFS WEEKLY MUSCLE SPLIT")

    for day, muscles in weekly_split.items():

        print(
            f"{DAY_NAMES[day]}: "
            f"{', '.join(muscles)}"
        )

    # 7. Generate daily sessions.

    generated_plan = []
    active_by_day = {}

    # Track used exercise IDs across the whole week.
    used_exercise_ids = set()

    for day in sorted(weekly_split):

        # Block primary muscles from the immediately
        # preceding calendar day.

        blocked_muscles = active_by_day.get(
            day - 1,
            set()
        )

        target_muscles = weekly_split[day]

        print(
            f"\nBuilding {DAY_NAMES[day]}..."
        )

        selected_exercises = build_session(
            target_muscles,
            suitable_exercises,
            blocked_muscles,
            used_exercise_ids
        )

        if selected_exercises is None:

            print(
                f"\nCould not build a session "
                f"for {DAY_NAMES[day]}."
            )

            print("The weekly plan cannot be approved.")
            return

        # Record selected exercise IDs.
        selected_ids = {
            exercise["id"]
            for exercise in selected_exercises
        }

        if used_exercise_ids.intersection(selected_ids):
            print("Repeated exercise found across the week.")
            print("The weekly plan cannot be approved.")
            return

        used_exercise_ids.update(selected_ids)

        # Track primary muscles trained that day.

        day_primary_muscles = set()

        for exercise in selected_exercises:

            day_primary_muscles.add(
                exercise["primary_muscle"]
            )

        active_by_day[day] = day_primary_muscles

        generated_plan.append({
            "day_index": day,
            "exercises": selected_exercises
        })

    # 8. Display weekly plan.

    display_plan(generated_plan)

    # 9. Display weekly set totals.

    show_weekly_sets(generated_plan)

    # 10. Validate all rules.

    approved = validate_final_plan(
        generated_plan,
        profile
    )

    if not approved:
        print("\nPlease review the failed rules.")


# ==================================================
# RUN PROGRAM
# ==================================================

if __name__ == "__main__":

    try:
        main()

    except (FileNotFoundError, ValueError, KeyError) as error:

        print("\nProgram error:", error)
