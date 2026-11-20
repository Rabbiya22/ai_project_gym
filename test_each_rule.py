from plan_checker import check_R0, check_R4, check_R5


# Only age is required in the customer profile
profile = {
    "age": 25
}


# Sample workout plan
def make_plan():
    return [
        {
            "day_index": 0,
            "exercises": [
                {
                    "id": "E1",
                    "name": "Push Up",
                    "primary_muscle": "chest",
                    "secondary_muscles": ["triceps"],
                    "sets": 3,
                    "minutes_per_set": 3
                }
            ]
        },
        {
            "day_index": 2,
            "exercises": [
                {
                    "id": "E2",
                    "name": "Dumbbell Row",
                    "primary_muscle": "back",
                    "secondary_muscles": ["biceps"],
                    "sets": 3,
                    "minutes_per_set": 3
                }
            ]
        }
    ]


# Test age eligibility
def test_age():
    print("R0 Age Eligibility:", check_R0(profile))


# Test recovery rule
def test_recovery():
    plan = make_plan()

    # Add chest workout on the next day
    # This breaks the recovery rule
    plan.insert(1, {
        "day_index": 1,
        "exercises": [
            {
                "id": "E3",
                "name": "Chest Press",
                "primary_muscle": "chest",
                "secondary_muscles": [],
                "sets": 2,
                "minutes_per_set": 3
            }
        ]
    })

    print("R4 Recovery:", check_R4(plan))


# Test no repeats rule
def test_no_repeats():
    plan = make_plan()

    # Add the same exercise again
    plan[0]["exercises"].append(
        plan[0]["exercises"][0].copy()
    )

    print("R5 No Repeats:", check_R5(plan))


# Run all tests
if __name__ == "__main__":
    test_age()
    test_recovery()
    test_no_repeats()