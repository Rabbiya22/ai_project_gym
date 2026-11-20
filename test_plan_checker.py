
import unittest

from plan_checker import check_plan, check_R0


profile = {"age": 25}


# ==========================================
# CREATE A VALID TEST PLAN
# ==========================================

def make_plan():

    muscle_groups = [
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

    days = [0, 2, 4]

    plan = []

    for index, day_index in enumerate(days):

        exercises = []

        daily_muscles = muscle_groups[
            index * 3:(index + 1) * 3
        ]

        for muscle in daily_muscles:

            exercises.append({
                "id": f"exercise_{muscle}",
                "primary_muscle": muscle,
                "secondary_muscles": [],
                "equipment": "bodyweight",
                "level": "beginner",
                "sets": 3,
                "minutes_per_set": 3
            })

        plan.append({
            "day_index": day_index,
            "exercises": exercises
        })

    return plan


# ==========================================
# UNIT TEST CLASS
# ==========================================

class TestPlanChecker(unittest.TestCase):

    # TEST 1: VALID PLAN
    def test_valid_plan(self):

        plan = make_plan()

        result = check_plan(plan, profile)

        self.assertTrue(result["R0_Age_Eligibility"])
        self.assertTrue(result["R1_Equipment"])
        self.assertTrue(result["R2_Difficulty"])
        self.assertTrue(result["R3_Session_Duration"])
        self.assertTrue(result["R4_Muscle_Recovery"])
        self.assertTrue(result["R5_No_Repeats"])
        self.assertTrue(result["R6_Weekly_Sets"])
        self.assertTrue(result["All_Rules_Pass"])


    # TEST 2: R1 - INVALID EQUIPMENT
    def test_R1_equipment(self):

        plan = make_plan()

        plan[0]["exercises"][0]["equipment"] = "unknown"

        result = check_plan(plan, profile)

        self.assertFalse(result["R1_Equipment"])


    # TEST 3: R2 - INVALID DIFFICULTY
    def test_R2_difficulty(self):

        plan = make_plan()

        plan[0]["exercises"][0]["level"] = "expert"

        result = check_plan(plan, profile)

        self.assertFalse(result["R2_Difficulty"])


    # TEST 4: R3 - SESSION TIME EXCEEDED
    def test_R3_time(self):

        plan = make_plan()

        for exercise in plan[0]["exercises"]:
            exercise["minutes_per_set"] = 20

        result = check_plan(plan, profile)

        self.assertFalse(result["R3_Session_Duration"])


    # TEST 5: R4 - CONSECUTIVE-DAY OVERLAP
    def test_R4_recovery(self):

        plan = make_plan()

        # Change Wednesday to Tuesday
        plan[1]["day_index"] = 1

        repeated_exercise = {
            "id": "extra_chest",
            "primary_muscle": "chest",
            "secondary_muscles": [],
            "equipment": "bodyweight",
            "level": "beginner",
            "sets": 3,
            "minutes_per_set": 3
        }

        # Add chest to Tuesday
        plan[1]["exercises"].append(repeated_exercise)

        result = check_plan(plan, profile)

        self.assertFalse(result["R4_Muscle_Recovery"])


    # TEST 6: R5 - REPEATED EXERCISE
    def test_R5_repeated_exercise(self):

        plan = make_plan()

        repeated_exercise = plan[0]["exercises"][0].copy()

        # Add duplicate to the same day
        plan[0]["exercises"].append(repeated_exercise)

        result = check_plan(plan, profile)

        self.assertFalse(result["R5_No_Repeats"])


    # TEST 7: R6 - WEEKLY SET LIMIT EXCEEDED
    def test_R6_weekly_sets(self):

        plan = make_plan()

        # Chest now has 7 sets instead of the maximum 6
        plan[0]["exercises"][0]["sets"] = 7

        result = check_plan(plan, profile)

        self.assertFalse(result["R6_Weekly_Sets"])


    # TEST 8: R0 - AGE ELIGIBILITY
    def test_R0_age(self):

        self.assertFalse(check_R0({"age": 16}))
        self.assertTrue(check_R0({"age": 25}))
        self.assertFalse(check_R0({"age": 65}))


# ==========================================
# RUN ALL TESTS
# ==========================================

if __name__ == "__main__":
    unittest.main()
