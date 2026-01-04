#!/bin/bash
# task-mind CDP Command Examples

# === Navigation ===
uv run task-mind navigate "https://x.com/search?q=AI"

# === Scroll to Element ===
# Scroll to element containing specified text
uv run task-mind scroll-to --text "AI will change the way we work"

# === Screenshot ===
uv run task-mind screenshot "screenshots/001.png"

# === Wait ===
uv run task-mind wait 2

# === Get Page Content ===
uv run task-mind get-content

# === Execute JavaScript ===
uv run task-mind exec-js "document.querySelector('[data-testid=\"tweetText\"]').innerText"

# === Recipe Execution ===
# Extract tweet + comments
uv run task-mind recipe run x_extract_tweet_with_comments \
  --params '{"url": "https://x.com/user/status/123456"}'

# Extract Timeline
uv run task-mind recipe run x_extract_timeline_with_scroll \
  --params '{"query": "AI", "max_tweets": 20}'
