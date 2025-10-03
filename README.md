# Design Idea

I built two agents—Dex (data engineering twin) and Sage (data science twin)—because that’s basically how I already operate. My school/work experience sits across DE and DS, so I naturally split problems into two lanes: first, get the data right; second, make the data useful. My interests—workout and baking—fit this pattern neatly. Workouts throw off logs (duration, volume, intensity), while baking has recipes, macros, and pantry constraints. Dex is the part of me that loves tidy schemas, unit normalization, and reliability checks. It ingests workouts, recipes, pantry, and nutrition, then publishes stable tables I can trust. Sage mirrors the side of me that uses R to explore, forecast a little, and write short, actionable notes. Its job isn’t to produce a 20-page report; it’s to deliver one training insight, one baking insight, and one micro-experiment I can try next week. In short, these agents are my “digital twin lite”—how my brain prefers to work, just a bit more organized (and less distracted, hopefully).

# What worked 
The DE/DS split made interfaces crisp: Dex publishes documented, tidy tables; Sage consumes without chasing missing columns. Standardizing keys (date, session_id, recipe_id) plus a tiny data dictionary meant Sage could move quickly on a “Weekly Twin Report.” The brief felt focused and actionable—clear takeaways and a pantry-aware bake suggestion. Small scope, big signal.

# What didn’t work
Templating tripped me at first: I used {week_iso} and forgot to pass it into kickoff, so interpolation errors wasted time. There was a couple places where column names drifted (workout_type vs exercise_type) and Sage’s plots broke.

# What I learned
Design the contract before the code: stable table names, a short data dictionary, and 3–5 essential derived fields. Add “Hello World” tests for both agents on day 1 (Dex asserts row counts/freshness; Sage outputs a 3-sentence mini report). Put in guardrails—retry/backoff for API calls, clear error messages for missing template vars, a sane .gitignore. Keep the weekly brief short and opinionated; it nudges behavior change more than long dashboards. And tie recommendations to pantry constraints—those feel personal and make me actually act. I should’ve check naming with a quick R skim before the full run, lesson learned.

# Hw1DigitalTwinLiteJoanna Crew

Welcome to the Hw1DigitalTwinLiteJoanna Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## 🎤 Voice mode (STT+TTS)

This repo supports speech input (Whisper via `faster-whisper`) and spoken replies (Kokoro).


## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

### Install extras
```bash
uv sync --extra voice
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/hw1_digital_twin_lite_joanna/config/agents.yaml` to define your agents
- Modify `src/hw1_digital_twin_lite_joanna/config/tasks.yaml` to define your tasks
- Modify `src/hw1_digital_twin_lite_joanna/crew.py` to add your own logic, tools and specific args
- Modify `src/hw1_digital_twin_lite_joanna/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the hw1-digital-twin-lite-joanna Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The hw1-digital-twin-lite-joanna Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the Hw1DigitalTwinLiteJoanna Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.

