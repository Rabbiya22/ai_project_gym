
import csv
from pathlib import Path


# --------------------------------------------------
# EXERCISE DIFFICULTY LEVELS
# --------------------------------------------------

LEVELS = {
    "beginner": 1,
    "intermediate": 2
}


# --------------------------------------------------
# 1. FILTER EXERCISES BY EXPERIENCE LEVEL
# --------------------------------------------------

def filter_exercises(exercises, profile):

    if not isinstance(profile, dict):
        return []

    user_level = LEVELS.get(
        str(profile.get("level", "")).strip().lower(),
        0
    )

    if user_level == 0:
        return []

    filtered = []

    for exercise in exercises:

        difficulty = LEVELS.get(
            str(exercise.get("level", "")).strip().lower(),
            0
        )

        # Reject invalid or higher difficulty levels
        if difficulty == 0 or difficulty > user_level:
            continue

        filtered.append(exercise)

    return filtered


# --------------------------------------------------
# 2. LOAD EXERCISES FROM CSV
# --------------------------------------------------

def load_exercises():

    file_path = Path(__file__).parent / "exercises_v1.csv"

    # Check whether the CSV file exists
    if not file_path.exists():
        raise FileNotFoundError(
            f"Exercise dataset not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        # Required CSV columns
        required_columns = {
            "id",
            "name",
            "primary_muscle",
            "secondary_muscles",
            "equipment",
            "level",
            "minutes_per_set"
        }

        actual_columns = set(reader.fieldnames or [])

        missing_columns = required_columns - actual_columns

        if missing_columns:
            raise ValueError(
                "Missing CSV columns: "
                + ", ".join(sorted(missing_columns))
            )

        exercises = list(reader)

    if not exercises:
        raise ValueError("The exercise dataset is empty.")

    return exercises


# --------------------------------------------------
# 3. TEST EXERCISE FILTER
# --------------------------------------------------

if __name__ == "__main__":

    try:

        exercises = load_exercises()

        print("\n========== EXERCISE FILTER TEST ==========")

        print("Total exercises:", len(exercises))

        # Test Beginner
        beginner_profile = {
            "level": "beginner"
        }

        beginner_exercises = filter_exercises(
            exercises,
            beginner_profile
        )

        print(
            "\nSuitable Beginner exercises:",
            len(beginner_exercises)
        )

        # Test Intermediate
        intermediate_profile = {
            "level": "intermediate"
        }

        intermediate_exercises = filter_exercises(
            exercises,
            intermediate_profile
        )

        print(
            "Suitable Intermediate exercises:",
            len(intermediate_exercises)
        )

        # Display Intermediate results
        print("\nIntermediate Filtered Exercises:\n")

        for exercise in intermediate_exercises:

            print(
                exercise["name"],
                "| Level:", exercise["level"],
                "| Muscle:", exercise["primary_muscle"]
            )

    except (FileNotFoundError, ValueError) as error:

        print("\nError:", error)
