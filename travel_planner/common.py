"""Shared helpers for Peter, David and Gita."""

import anthropic

MODEL = "claude-opus-5-5"

# If a request is declined by a safety classifier, the API retries it on a
# suitable fallback model inside the same call.
BETAS = ["server-side-fallback-2026-07-01"]
FALLBACKS = "default"

WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment


def text_of(message) -> str:
    """Join the text blocks of a response."""
    return "\n".join(b.text for b in message.content if b.type == "text").strip()


def run_subagent(name: str, system: str, task: str, effort: str = "medium") -> str:
    """Run one sub-agent (David or Gita) on a task and return its written answer.

    The sub-agent can use web search (run on Anthropic's servers) to check current
    prices, opening hours and so on.
    """
    messages = [{"role": "user", "content": task}]
    while True:
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=64000,
            system=system,
            tools=[WEB_SEARCH_TOOL],
            output_config={"effort": effort},
            betas=BETAS,
            fallbacks=FALLBACKS,
            messages=messages,
        ) as stream:
            response = stream.get_final_message()

        if response.stop_reason == "pause_turn":
            # A long web-search turn paused; send it back so the server continues.
            messages.append({"role": "assistant", "content": response.content})
            continue
        if response.stop_reason == "refusal":
            return f"[{name} could not help with this request.]"
        answer = text_of(response)
        if response.stop_reason == "max_tokens":
            answer += "\n[Answer was cut off at the length limit.]"
        return answer or f"[{name} returned no answer.]"
