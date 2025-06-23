"""Run the meta-agent to update guidelines."""

from agent.meta_agent import run_meta_agent


if __name__ == "__main__":
    result = run_meta_agent()
    if result:
        print(result)
