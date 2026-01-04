#!/bin/bash
# task-mind Common Command Quick Reference
# Applies to: /task-mind.run, /task-mind.do, /task-mind.recipe, /task-mind.test

# === Chrome Management (Execute First) ===
# Check CDP connection status
task-mind chrome status

# Start Chrome (two modes)
task-mind chrome start              # Normal window mode
task-mind chrome start --headless   # Headless mode (no UI)

# Common startup options
task-mind chrome start --port 9333        # Use different port
task-mind chrome start --keep-alive       # Keep running after start, until Ctrl+C
task-mind chrome start --no-kill          # Don't kill existing CDP Chrome process

# Stop Chrome
task-mind chrome stop

# === Discover Resources ===
# List all recipes
task-mind recipe list
task-mind recipe list --format json  # AI format

# View recipe details
task-mind recipe info <recipe_name>

# Search related run records
rg -l "keyword" ~/.task-mind/projects/

# === Browser Operations ===
# Navigate
task-mind chrome navigate <url>
task-mind chrome navigate <url> --wait-for <selector>

# Click
task-mind chrome click <selector>
task-mind chrome click <selector> --wait-timeout 10

# Scroll
task-mind chrome scroll <pixels>  # Positive for down, negative for up
task-mind chrome scroll-to --text "target text"

# Wait
task-mind chrome wait <seconds>

# === Information Extraction ===
# Get title
task-mind chrome get-title

# Get content
task-mind chrome get-content
task-mind chrome get-content <selector>

# Execute JavaScript
task-mind chrome exec-js <expression>
task-mind chrome exec-js <expression> --return-value
task-mind chrome exec-js "window.location.href" --return-value  # Get URL

# Screenshot
task-mind chrome screenshot output.png
task-mind chrome screenshot output.png --full-page

# === Visual Effects ===
task-mind chrome highlight <selector>
task-mind chrome pointer <selector>
task-mind chrome spotlight <selector>
task-mind chrome annotate <selector> --text "description"

# === Run/Project Management ===
# List projects
task-mind run list
task-mind run list --format json

# Initialize project
task-mind run init "task description"

# Set context
task-mind run set-context <project_id>

# Release context
task-mind run release

# Log
task-mind run log \
  --step "step description" \
  --status "success" \
  --action-type "analysis" \
  --execution-method "analysis" \
  --data '{"key": "value"}'

# Screenshot (in context)
task-mind run screenshot "step description"

# === Recipe Execution ===
task-mind recipe run <name>
task-mind recipe run <name> --params '{"key": "value"}'
task-mind recipe run <name> --output-file result.json
