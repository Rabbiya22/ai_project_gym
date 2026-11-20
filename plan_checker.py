
"""
Plan Checker for AI-Based Personalized Workout Planner

R0 - Age Eligibility
R1 - Equipment
R2 - Difficulty Level
R3 - Session Time
R4 - Recovery
R5 - No Repeated Exercises
R6 - Weekly Volume
"""

# ==========================================
# FIXED PROJECT SETTINGS
# ==========================================

MIN_AGE = 19
MAX_AGE = 59

MIN_SESSION_MINUTES = 35
MAX_SESSION_MINUTES = 45

ALLOWED_EQUIPMENT = {
    "bodyweight",
    "bands_other",
    "dumbbell",
    "barbell",
    "machine_cable"
}

ALLOWED_LEVELS = {
    "beginner",
    "intermediate"
}

LEVEL_RANK = {
    "beginner": 1,
    "intermediate": 2
}

MUSCLE_GROUPS = {
    "chest",
    "back",
    "shoulders",
    "biceps",
    "triceps",
    "quads",
    "hamstrings_glutes",
    "calves",
    "core"
}

DEFAULT_WEEKLY_SET_LIMITS = {
    muscle: {"min": 1, "max": 6}
    for muscle in MUSCLE_GROUPS
}


# ==========================================
# R0: AGE ELIGIBILITY
# ==========================================

def check_R0(profile):

    if not isinstance(profile, dict):
        return False

    age = profile.get("age")

    try:
        age = float(age)
    except (ValueError, TypeError):
        return False

    if not age.is_integer():
        return False

    return MIN_AGE <= age <= MAX_AGE


def get_age_message(age):

    try:
        age = float(age)
    except (ValueError, TypeError):
        return "Please enter a valid age."

    if age < MIN_AGE:
        return (
            f"Sorry, this planner is designed for users "
            f"aged {MIN_AGE} to {MAX_AGE}. "
            "Your age is below the allowed range."
        )

    elif age > MAX_AGE:
        return (
            f"Sorry, this planner is designed for users "
            f"aged {MIN_AGE} to {MAX_AGE}. "
            "Your age is above the allowed range."
        )

    return "Age is eligible."


# ==========================================
# R1: EQUIPMENT CHECK
# ==========================================

def check_R1(plan, profile=None):

    if not isinstance(plan, list):
        return False

    if profile is None:
        profile = {}

    available_equipment = profile.get(
        "equipment",
        ALLOWED_EQUIPMENT
    )

    if isinstance(available_equipment, str):
        available_equipment = {available_equipment}

    if not isinstance(
        available_equipment,
        (set, list, tuple)
    ):
        return False

    available_equipment = {
        item.strip().lower()
        for item in available_equipment
        if isinstance(item, str)
    }

    for day in plan:

        if not isinstance(day, dict):
            return False

        exercises = day.get("exercises", [])

        if not isinstance(exercises, list):
            return False

        for exercise in exercises:

            if not isinstance(exercise, dict):
                return False

            equipment = exercise.get("equipment")

            if not isinstance(equipment, str):
                return False

            equipment = equipment.strip().lower()

            if equipment not in ALLOWED_EQUIPMENT:
                return False

            if equipment not in available_equipment:
                return False

    return True


# ==========================================
# R2: DIFFICULTY CHECK
# ==========================================

def check_R2(plan, profile=None):

    if not isinstance(plan, list):
        return False

    if profile is None:
        profile = {}

    user_level = profile.get("level", "beginner")

    if not isinstance(user_level, str):
        return False

    user_level = user_level.strip().lower()

    if user_level not in LEVEL_RANK:
        return False

    user_level_rank = LEVEL_RANK[user_level]

    for day in plan:

        if not isinstance(day, dict):
            return False

        exercises = day.get("exercises", [])

        if not isinstance(exercises, list):
            return False

        for exercise in exercises:

            if not isinstance(exercise, dict):
                return False

            level = exercise.get("level")

            if not isinstance(level, str):
                return False

            level = level.strip().lower()

            if level not in ALLOWED_LEVELS:
                return False

            if LEVEL_RANK[level] > user_level_rank:
                return False

    return True


# ==========================================
# R3: SESSION TIME CHECK
# ==========================================

def check_R3(plan, profile=None):

    if not isinstance(plan, list):
        return False

    if profile is None:
        profile = {}

    max_session_time = profile.get(
        "session_minutes",
        MAX_SESSION_MINUTES
    )

    try:
        max_session_time = float(max_session_time)

    except (ValueError, TypeError):
        return False

    if max_session_time <= 0:
        return False

    effective_max = min(
        MAX_SESSION_MINUTES,
        max_session_time
    )

    for day in plan:

        if not isinstance(day, dict):
            return False

        exercises = day.get("exercises", [])

        if not isinstance(exercises, list) or not exercises:
            return False

        total_time = 0

        for exercise in exercises:

            if not isinstance(exercise, dict):
                return False

            try:
                sets = float(exercise["sets"])
                minutes = float(
                    exercise["minutes_per_set"]
                )

                if sets <= 0 or minutes <= 0:
                    return False

                total_time += sets * minutes

            except (KeyError, ValueError, TypeError):
                return False

        if not (
            MIN_SESSION_MINUTES
            <= total_time
            <= effective_max
        ):
            return False

    return True


# ==========================================
# R4: RECOVERY CHECK
# ==========================================

def check_R4(plan, profile=None):

    if not isinstance(plan, list):
        return False

    days = {}

    for day in plan:

        if not isinstance(day, dict):
            return False

        day_index = day.get("day_index")

        if (
            not isinstance(day_index, int)
            or isinstance(day_index, bool)
            or day_index < 0
            or day_index > 6
        ):
            return False

        if day_index in days:
            return False

        exercises = day.get("exercises", [])

        if not isinstance(exercises, list):
            return False

        # Track primary muscles only.
        muscles = set()

        for exercise in exercises:

            if not isinstance(exercise, dict):
                return False

            primary = exercise.get("primary_muscle")

            if (
                not isinstance(primary, str)
                or not primary.strip()
            ):
                return False

            muscles.add(primary.strip().lower())

        days[day_index] = muscles

    # Compare consecutive calendar days.
    # Secondary muscle overlap is not checked.

    for day_index, muscles in days.items():

        next_day = day_index + 1

        if next_day in days:

            if muscles.intersection(days[next_day]):
                return False

    return True


# ==========================================
# R5: NO REPEATED EXERCISES
# ==========================================

def check_R5(plan, profile=None):

    if not isinstance(plan, list):
        return False

    # One set for the entire week.
    used_exercises = set()

    for day in plan:

        if not isinstance(day, dict):
            return False

        exercises = day.get("exercises", [])

        if not isinstance(exercises, list):
            return False

        for exercise in exercises:

            if not isinstance(exercise, dict):
                return False

            exercise_id = exercise.get(
                "id",
                exercise.get("exercise_id")
            )

            if exercise_id is None:
                return False

            exercise_id = str(exercise_id).strip()

            if not exercise_id:
                return False

            if exercise_id in used_exercises:
                return False

            used_exercises.add(exercise_id)

    return True


# ==========================================
# R6: WEEKLY VOLUME CHECK
# ==========================================

def check_R6(
    plan,
    profile=None,
    weekly_set_limits=None
):

    if not isinstance(plan, list):
        return False

    if weekly_set_limits is None:
        weekly_set_limits = DEFAULT_WEEKLY_SET_LIMITS

    if not isinstance(weekly_set_limits, dict):
        return False

    if not MUSCLE_GROUPS.issubset(weekly_set_limits.keys()):
        return False

    weekly_sets = {
        muscle: 0
        for muscle in MUSCLE_GROUPS
    }

    for day in plan:

        if not isinstance(day, dict):
            return False

        exercises = day.get("exercises", [])

        if not isinstance(exercises, list):
            return False

        for exercise in exercises:

            if not isinstance(exercise, dict):
                return False

            muscle = exercise.get("primary_muscle")

            if not isinstance(muscle, str):
                return False

            muscle = muscle.strip().lower()

            if muscle not in MUSCLE_GROUPS:
                return False

            try:
                sets = float(exercise["sets"])
            except (KeyError, ValueError, TypeError):
                return False

            if sets <= 0:
                return False

            weekly_sets[muscle] += sets

    for muscle in MUSCLE_GROUPS:

        limits = weekly_set_limits[muscle]

        if not isinstance(limits, dict):
            return False

        try:
            minimum = float(limits["min"])
            maximum = float(limits["max"])
        except (KeyError, ValueError, TypeError):
            return False

        if minimum < 0 or maximum < minimum:
            return False

        total = weekly_sets[muscle]

        if total < minimum or total > maximum:
            return False

    return True


# ==========================================
# CHECK ALL RULES
# ==========================================

def check_plan(plan, profile, weekly_set_limits=None):

    if not isinstance(profile, dict):
        profile = {}

    # Check age first.
    if not check_R0(profile):

        return {
            "R0_Age_Eligibility": False,
            "Age_Message": get_age_message(
                profile.get("age")
            ),
            "R1_Equipment": None,
            "R2_Difficulty": None,
            "R3_Session_Duration": None,
            "R4_Muscle_Recovery": None,
            "R5_No_Repeats": None,
            "R6_Weekly_Sets": None,
            "All_Checked_Rules_Pass": False,
            "All_Rules_Pass": False
        }

    # Run all seven rules.
    results = {
        "R0_Age_Eligibility": True,
        "R1_Equipment": check_R1(plan, profile),
        "R2_Difficulty": check_R2(plan, profile),
        "R3_Session_Duration": check_R3(plan, profile),
        "R4_Muscle_Recovery": check_R4(plan, profile),
        "R5_No_Repeats": check_R5(plan, profile),
        "R6_Weekly_Sets": check_R6(
            plan, profile, weekly_set_limits
        )
    }

    rule_names = [
        "R0_Age_Eligibility",
        "R1_Equipment",
        "R2_Difficulty",
        "R3_Session_Duration",
        "R4_Muscle_Recovery",
        "R5_No_Repeats",
        "R6_Weekly_Sets"
    ]

    results["All_Checked_Rules_Pass"] = all(
        results[rule] is True
        for rule in rule_names
    )

    results["All_Rules_Pass"] = (
        results["All_Checked_Rules_Pass"]
    )

    return results
