from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import re
from typing import Any, Dict
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Hw1DigitalTwinLiteJoanna():
    """Hw1DigitalTwinLiteJoanna crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def dex(self) -> Agent:
        return Agent(
            config=self.agents_config['dex'], # type: ignore[index]
            verbose=True
        )

    @agent
    def sage(self) -> Agent:
        return Agent(
            config=self.agents_config['sage'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def build_datamart_task(self) -> Task:
        return Task(
            config=self.tasks_config['build_datamart_task'], # type: ignore[index]
        )

    @task
    def weekly_twin_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['weekly_twin_report_task'], # type: ignore[index]
            output_file='week_iso.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Hw1DigitalTwinLiteJoanna crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

def _inputs_from_tasks_config(inst, user_text: str) -> Dict[str, Any]:
    """Scan task configs for {placeholders} and fill them with user_text."""
    base = {
        # common names used in CrewAI templates
        "prompt": user_text,
        "user_text": user_text,
        "user_input": user_text,
        "query": user_text,
        "input": user_text,
        "topic": user_text,
        "question": user_text,
        "goal": user_text,
    }
    try:
        cfg = getattr(inst, "tasks_config", {}) or {}
        placeholders = set()
        for _tname, tcfg in (cfg.items() if isinstance(cfg, dict) else []):
            if isinstance(tcfg, dict):
                for field in ("description", "expected_output", "instructions", "context", "goal"):
                    val = tcfg.get(field)
                    if isinstance(val, str):
                        placeholders.update(re.findall(r"{([^}]+)}", val))
        for k in placeholders:
            base.setdefault(k, user_text)
    except Exception:
        # If anything odd happens, just keep the base keys
        pass
    return base

def run_once(user_text: str) -> str:
    """
    Build your Crew from the class that defines @crew and run a single turn.
    Returns text (never throws), so the voice loop won't misreport failures.
    """
    try:
        inst = Hw1DigitalTwinLiteJoanna()
    except Exception as e:
        return f"(setup error) Could not initialize Hw1DigitalTwinLiteJoanna: {e}"

    try:
        crew = inst.crew()
    except Exception as e:
        return f"(setup error) Could not build Crew: {e}"

    inputs = _inputs_from_tasks_config(inst, user_text)

    try:
        result = crew.kickoff(inputs=inputs)
        txt = str(result).strip() if result is not None else ""
        return txt or "(no output from crew)"
    except Exception as e:
        return f"(runtime error) Crew failed: {e}"