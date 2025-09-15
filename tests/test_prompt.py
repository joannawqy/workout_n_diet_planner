# tests/test_prompt.py
# Run as a script:  python tests/test_prompt.py
# Or with pytest:   pytest -q tests/test_prompt.py

import os
from crewai import Agent, Task, Crew, LLM

# --- Config ---
MODEL = os.getenv("TEST_LLM", "openai/gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEST_TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("TEST_MAX_TOKENS", "300"))

DEX_PROMPT = (
    "Introduce yourself as Dex, my Personal Data Engineering Twin. In 3 sentences max, "
    "name the sources you'll ingest (workouts, baking logs, recipes, pantry, nutrition), "
    "the curated tables you'll publish (workouts_daily, workouts_sessions, bakes, recipes, "
    "pantry, metrics_weekly), and one reliability check you always run."
)

SAGE_PROMPT = (
    "Introduce yourself as Sage, my Personal Data Science Twin. In 3 sentences max, give a "
    "mini Weekly Twin Report with plausible placeholder numbers: one training takeaway "
    "(volume/intensity), one baking takeaway (macro profile), and one micro-experiment for next week."
)

def make_llm():
    return LLM(model=MODEL, temperature=TEMPERATURE, max_tokens=MAX_TOKENS)

def make_agents():
    llm = make_llm()
    dex = Agent(
        role="Personal Data Engineering Twin",
        goal="Explain how you'll build/refresh the personal datamart clearly and briefly.",
        backstory="Pragmatic DE who loves tidy schemas and reliability checks.",
        llm=llm,
        verbose=True,
    )
    sage = Agent(
        role="Personal Data Science Twin",
        goal="Summarize weekly insights and propose a tiny experiment, briefly.",
        backstory="Curious DS who turns data into decisions (workouts + baking).",
        llm=llm,
        verbose=True,
    )
    return dex, sage

def run_single(agent: Agent, user_prompt: str) -> str:
    task = Task(
        description=f"Respond to this prompt exactly and stay under 3 sentences:\n{user_prompt}",
        expected_output="A short paragraph (≤3 sentences).",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task]).kickoff()

def main():
    dex, sage = make_agents()
    print("\n--- Running Dex test ---")
    out1 = run_single(dex, DEX_PROMPT)
    print(out1)

    print("\n--- Running Sage test ---")
    out2 = run_single(sage, SAGE_PROMPT)
    print(out2)

# --- Pytest smoke tests (optional) ---
def test_dex_prompt_smoke():
    # Skip if no API key to avoid failing CI
    if not os.getenv("OPENAI_API_KEY"):
        import pytest
        pytest.skip("OPENAI_API_KEY not set; skipping live LLM test.")
    dex, _ = make_agents()
    out = run_single(dex, DEX_PROMPT)
    assert isinstance(out, str) and len(out.strip()) > 0

def test_sage_prompt_smoke():
    if not os.getenv("OPENAI_API_KEY"):
        import pytest
        pytest.skip("OPENAI_API_KEY not set; skipping live LLM test.")
    _, sage = make_agents()
    out = run_single(sage, SAGE_PROMPT)
    assert isinstance(out, str) and len(out.strip()) > 0

if __name__ == "__main__":
    main()
