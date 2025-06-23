"""Meta-agent that synthesizes guidelines from reflection logs."""
from __future__ import annotations

import glob
import os
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage


REFLECT_DIR = "data/reflections"
GUIDELINES_FILE = "guidelines.txt"


def run_meta_agent() -> str | None:
    files = glob.glob(os.path.join(REFLECT_DIR, "*.jsonl"))
    if not files:
        return None
    texts = []
    for f in files:
        with open(f) as fh:
            texts.extend([line.strip() for line in fh if line.strip()])
    llm = ChatOllama()
    ai: AIMessage = llm.invoke([HumanMessage(content="\n".join(texts))])
    with open(GUIDELINES_FILE, "w") as fh:
        fh.write(ai.content.strip())
    return ai.content.strip()


if __name__ == "__main__":
    run_meta_agent()
