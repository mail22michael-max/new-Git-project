"""Peter - the travel planner agent.

Peter talks with you, works out what you want, and delegates to two sub-agents:
  * David - the budget agent (costs, budget fit, savings)
  * Gita  - the tour guide (itinerary, sights, food, local tips)
He then merges their answers into one trip plan.

Run:  python peter.py
"""

from concurrent.futures import ThreadPoolExecutor

import anthropic

from common import BETAS, FALLBACKS, MODEL, client, text_of
from david import ask_david
from gita import ask_gita

SYSTEM = """You are Peter, a friendly travel planner who leads a small team:
- David, the budget agent: costs, whether a plan fits a budget, and how to save.
- Gita, the tour guide: day-by-day itineraries, sights, food, and local tips.

How you work:
1. If key details are missing (destination, dates or trip length, number of travellers,
   budget, interests, travel pace, departure city), ask the traveller briefly before
   delegating. Don't ask for things you can sensibly assume; state assumptions instead.
2. Ask Gita for the itinerary first, then send that itinerary to David to cost it.
   When the two requests don't depend on each other (e.g. a quick budget check while
   Gita plans), call both tools in the same turn.
3. Give each sub-agent a complete, self-contained brief: they can't see this
   conversation, only what you send them.
4. Merge their answers into one clear plan: a short overview, the day-by-day itinerary,
   the budget breakdown, and practical tips. Resolve conflicts between them (if the
   itinerary is over budget, adjust it, asking Gita or David again if needed).
5. For small follow-up questions, answer yourself or ask only the sub-agent you need.
Be warm and concise. Credit David and Gita for their parts."""

TOOLS = [
    {
        "name": "ask_david",
        "description": (
            "Ask David, the budget agent, to estimate trip costs, check a plan against a "
            "budget, or find savings. Send a complete brief: destination, dates, travellers, "
            "departure city, accommodation style, budget limit and currency, and the itinerary "
            "to cost if there is one. Returns David's written budget breakdown."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The full, self-contained brief for David."}
            },
            "required": ["task"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "ask_gita",
        "description": (
            "Ask Gita, the tour guide, for a day-by-day itinerary, sights, food, local tips or "
            "changes to an itinerary. Send a complete brief: destination, dates, travellers, "
            "interests, pace, budget level and any constraints. Returns Gita's written plan "
            "with approximate activity prices."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The full, self-contained brief for Gita."}
            },
            "required": ["task"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

SUBAGENTS = {"ask_david": ("David", ask_david), "ask_gita": ("Gita", ask_gita)}


def run_tool(block) -> dict:
    """Run one sub-agent call and wrap its answer as a tool_result."""
    name, fn = SUBAGENTS[block.name]
    task = block.input.get("task") if isinstance(block.input, dict) else None
    if not isinstance(task, str) or not task.strip():
        return {"type": "tool_result", "tool_use_id": block.id,
                "content": "Error: 'task' must be a non-empty string.", "is_error": True}
    try:
        answer = fn(task)
        print(f"  ✓ {name} replied.")
        return {"type": "tool_result", "tool_use_id": block.id, "content": answer}
    except anthropic.APIError as e:
        print(f"  ✗ {name} failed: {e}")
        return {"type": "tool_result", "tool_use_id": block.id,
                "content": f"{name} is unavailable right now ({e.__class__.__name__}).",
                "is_error": True}


def peter_turn(messages: list) -> str:
    """Run Peter until he has a reply for the traveller. Mutates `messages`."""
    while True:
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=64000,
            system=SYSTEM,
            tools=TOOLS,
            output_config={"effort": "high"},
            betas=BETAS,
            fallbacks=FALLBACKS,
            messages=messages,
        ) as stream:
            response = stream.get_final_message()

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "refusal":
            return "Sorry, I can't help plan that one."
        if response.stop_reason != "tool_use":
            return text_of(response)

        calls = [b for b in response.content if b.type == "tool_use"]
        for b in calls:
            who = SUBAGENTS.get(b.name, (b.name,))[0]
            print(f"  → Peter asks {who}...")
        # David and Gita work in parallel when Peter asks both at once.
        with ThreadPoolExecutor(max_workers=len(calls)) as pool:
            results = list(pool.map(run_tool, calls))
        # All results go back in a single user message.
        messages.append({"role": "user", "content": results})


def main() -> None:
    print("Peter: Hi, I'm Peter, your travel planner. David handles budgets and Gita is "
          "our tour guide. Where would you like to go? (type 'quit' to exit)\n")
    messages: list = []
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user.lower() in {"quit", "exit", "bye"}:
            break
        start = len(messages)
        messages.append({"role": "user", "content": user})
        try:
            reply = peter_turn(messages)
        except anthropic.AuthenticationError:
            print("Peter: I can't reach Claude - set ANTHROPIC_API_KEY and try again.")
            break
        except anthropic.APIError as e:
            print(f"Peter: Something went wrong talking to Claude ({e}). Please try again.")
            del messages[start:]  # drop the unanswered turn so the history stays valid
            continue
        print(f"\nPeter: {reply}\n")
    print("Peter: Safe travels!")


if __name__ == "__main__":
    main()
