#!/usr/bin/env python
import sys
import warnings

from datetime import date

from hw1_digital_twin_lite_joanna.crew import Hw1DigitalTwinLiteJoanna

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    today = date.today()
    iso = today.isocalendar()  # .year, .week, .weekday
    week_iso = f"{iso.year}-W{iso.week:02d}"
    inputs = {
        "week_iso": week_iso,
        "current_year": today.year,
        "warehouse_path": "data/warehouse"

    }
    
    try:
        Hw1DigitalTwinLiteJoanna().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Hw1DigitalTwinLiteJoanna().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Hw1DigitalTwinLiteJoanna().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Hw1DigitalTwinLiteJoanna().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
