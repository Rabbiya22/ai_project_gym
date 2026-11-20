MUSCLE_GROUPS = [
    "chest",
    "back",
    "shoulders",
    "biceps",
    "triceps",
    "quads",
    "hamstrings_glutes",
    "calves",
    "core"
]

DAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


def dfs_split(available_days, preferred_days):
    """
    Distributes all nine primary muscle groups across the selected days.

    The distribution is kept as balanced as possible.
    Recovery validation is handled separately by the plan checker.
    """

    # Validate number of available days
    if not isinstance(available_days, int) or isinstance(available_days, bool):
        raise ValueError("Number of available days must be an integer.")

    # Validate preferred days input
    if not isinstance(preferred_days, (list, tuple)):
        raise ValueError("Preferred days must be a list or tuple.")

    if available_days < 2 or available_days > 6:
        raise ValueError("Choose between 2 and 6 days. Sunday is closed.")

    if len(preferred_days) != available_days:
        raise ValueError("The number of selected days does not match.")

    if len(set(preferred_days)) != len(preferred_days):
        raise ValueError("You cannot select the same day more than once.")

    # Validate day numbers
    for day in preferred_days:
        if not isinstance(day, int) or isinstance(day, bool):
            raise ValueError("Day numbers must be integers.")

        if day < 0 or day > 5:
            raise ValueError("Choose days from Monday to Saturday only.")

    # Sort selected days
    selected_days = sorted(preferred_days)

    # Create an empty split for each selected day
    split = {day: [] for day in selected_days}

    # Calculate maximum groups allowed per day
    max_groups_per_day = (
        len(MUSCLE_GROUPS) + available_days - 1
    ) // available_days

    # Depth First Search
    def dfs(index):

        # Base case: all muscle groups have been assigned
        if index == len(MUSCLE_GROUPS):
            return all(split[day] for day in selected_days)

        # Select the current muscle group
        muscle = MUSCLE_GROUPS[index]

        # Try days with fewer muscle groups first
        ordered_days = sorted(
            selected_days,
            key=lambda day: len(split[day])
        )

        # Try assigning the muscle group to each day
        for day in ordered_days:

            # Skip if the day has reached its maximum capacity
            if len(split[day]) >= max_groups_per_day:
                continue

            # Make a choice
            split[day].append(muscle)

            # Recursively assign the next muscle group
            if dfs(index + 1):
                return True

            # Backtrack if the choice does not work
            split[day].pop()

        return False

    # Start DFS
    if dfs(0):
        return split

    return None


# Main program
if __name__ == "__main__":

    print("Select your preferred days:")
    print("0 Monday, 1 Tuesday, 2 Wednesday")
    print("3 Thursday, 4 Friday, 5 Saturday")
    print("Sunday is closed.")

    try:
        days = input("Enter day numbers separated by commas: ")

        preferred_days = [
            int(day.strip()) for day in days.split(",")
        ]

        result = dfs_split(
            len(preferred_days),
            preferred_days
        )

        if result is None:
            print("No valid split could be created.")

        else:
            print("\nWeekly Split:")

            for day, muscles in result.items():
                print(
                    f"{DAY_NAMES[day]}: {', '.join(muscles)}"
                )

    except ValueError as error:
        print("Error:", error)