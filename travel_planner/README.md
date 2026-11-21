# Peter – Travel Planner Agent

Peter is a chat-based travel planner built on the Claude API. He leads two sub-agents:

| Agent | Role | File |
|---|---|---|
| **Peter** | Lead planner: talks with you, briefs the sub-agents, merges their work into one plan | `peter.py` |
| **David** | Budget agent: cost breakdown, budget fit, money-saving tips | `david.py` |
| **Gita** | Tour guide: day-by-day itinerary, sights, food, local tips, activity prices | `gita.py` |

Peter calls David and Gita as tools (`ask_david`, `ask_gita`). Usually he asks Gita for an
itinerary first, then has David cost it. If he asks both at once, they run in parallel.
David and Gita can use web search to check current prices and opening hours.

## Run

```bash
pip install -r requirements.txt
```

```bash
export ANTHROPIC_API_KEY=your-key-here
```

```bash
python peter.py
```

Example: `Plan 4 days in Kyoto in April for 2 people from London, budget £2500, we love food and temples.`

## Notes
- Model: `claude-opus-5-5` (set in `common.py`). Peter runs at `high` effort, David and Gita at `medium`.
- Server-side refusal fallback is enabled (`fallbacks="default"`). If a request is declined, the API retries it on a fallback model.
- Web search is billed per search, in addition to tokens. Each sub-agent call is capped at 5 searches.
