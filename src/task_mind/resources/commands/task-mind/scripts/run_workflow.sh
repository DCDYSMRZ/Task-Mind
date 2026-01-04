#!/bin/bash
# Run Command Workflow Example
# Applies to: /task-mind.run (exploration & research, preparation for Recipe creation)

# === 1. Check Existing Projects ===
task-mind run list --format json

# === 2. Create New Project ===
task-mind run init "nano-banana-pro image api research"
# Returns project_id, assume it's nano-banana-pro-image-api-research

# === 3. Set Context ===
task-mind run set-context nano-banana-pro-image-api-research

# === 4. Execute Research Operations ===
# Navigate (auto-logged)
task-mind chrome navigate "https://example.com"

# Extract page links
task-mind chrome exec-js "Array.from(document.querySelectorAll('a')).map(a => ({text: a.textContent.trim(), href: a.href})).filter(a => a.text)" --return-value

# Screenshot verification (auto-logged)
task-mind chrome screenshot /tmp/step1.png

# === 5. Manually Record Analysis Results (with _insights) ===
task-mind run log \
  --step "Analyze API documentation structure" \
  --status "success" \
  --action-type "analysis" \
  --execution-method "analysis" \
  --data '{
    "conclusion": "API uses REST style",
    "endpoints": ["/generate", "/status"],
    "_insights": [
      {"type": "key_factor", "summary": "Requires API Key authentication"}
    ]
  }'

# === 6. Record Failures and Retries (must record _insights) ===
# Assume click failed
task-mind chrome click '.api-key-btn'  # Failed

# Record failure reason
task-mind run log \
  --step "Analyze click failure reason" \
  --status "warning" \
  --action-type "analysis" \
  --execution-method "analysis" \
  --data '{
    "command": "task-mind chrome click .api-key-btn",
    "error": "Element not found",
    "_insights": [
      {"type": "pitfall", "summary": "Dynamic class unreliable, need data-testid"}
    ]
  }'

# === 7. Research Complete: Generate Recipe Draft ===
task-mind run log \
  --step "Summarize research conclusions and generate Recipe draft" \
  --status "success" \
  --action-type "analysis" \
  --execution-method "analysis" \
  --data '{
    "ready_for_recipe": true,
    "recipe_spec": {
      "name": "nano_banana_generate_image",
      "type": "atomic",
      "runtime": "chrome-js",
      "description": "Generate image using Nano Banana Pro",
      "inputs": {
        "prompt": {"type": "string", "required": true}
      },
      "outputs": {
        "image_url": "string"
      },
      "key_steps": [
        "1. Input prompt",
        "2. Click generate button",
        "3. Wait for result",
        "4. Extract image URL"
      ],
      "pitfalls_to_avoid": ["Dynamic class unreliable"],
      "key_factors": ["Requires API Key authentication"]
    }
  }'

# === 8. Release Context (Mandatory!) ===
task-mind run release
