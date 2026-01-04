#!/bin/bash
# Do Command Workflow Example
# Applies to: /task-mind.do (one-time task execution)

# === 1. Clarify Output Format (If user hasn't specified, ask first) ===
# Use AskUserQuestion tool to confirm output format:
# - Structured data (JSON/CSV)
# - Document report (Markdown/HTML)
# - Execution logs only

# === 2. Create Project ===
task-mind run init "upwork python job apply"
task-mind run set-context upwork-python-job-apply

# === 3. Execute Task ===
# Navigate (auto-logged)
task-mind chrome navigate "https://upwork.com/jobs"

# Search
task-mind chrome exec-js "document.querySelector('input[type=search]').value = 'Python'" --return-value
task-mind chrome click 'button[type=submit]'
task-mind chrome wait 2

# Extract data
task-mind chrome exec-js "Array.from(document.querySelectorAll('.job-tile')).map(el => ({
  title: el.querySelector('.title')?.textContent,
  url: el.querySelector('a')?.href,
  rate: el.querySelector('.rate')?.textContent
}))" --return-value

# === 4. Use Recipe to Accelerate Repeated Operations ===
task-mind recipe run upwork_extract_job_list --params '{"keyword": "Python"}' --output-file ~/.task-mind/projects/upwork-python-job-apply/outputs/jobs.json

# Log Recipe execution
task-mind run log \
  --step "Extract Python job list" \
  --status "success" \
  --action-type "recipe_execution" \
  --execution-method "recipe" \
  --data '{"recipe_name": "upwork_extract_job_list", "output_file": "outputs/jobs.json"}'

# === 5. Data Processing (Script File) ===
# Create filter script
cat > ~/.task-mind/projects/upwork-python-job-apply/scripts/filter_jobs.py <<'EOF'
import json
jobs = json.load(open('outputs/jobs.json'))
filtered = [j for j in jobs if j.get('rate', 0) > 50]
json.dump(filtered, open('outputs/filtered_jobs.json', 'w'), indent=2)
print(f"Filtered {len(filtered)} high-paying jobs")
EOF

# Execute script (use absolute path, don't cd)
uv run python ~/.task-mind/projects/upwork-python-job-apply/scripts/filter_jobs.py

# Log script execution
task-mind run log \
  --step "Filter high-paying jobs" \
  --status "success" \
  --action-type "data_processing" \
  --execution-method "file" \
  --data '{
    "file": "scripts/filter_jobs.py",
    "language": "python",
    "result_file": "outputs/filtered_jobs.json"
  }'

# === 6. Save Final Results ===
task-mind run screenshot "Application success page"

task-mind run log \
  --step "Task completed: Successfully filtered high-paying jobs" \
  --status "success" \
  --action-type "analysis" \
  --execution-method "analysis" \
  --data '{
    "task_completed": true,
    "summary": "Filtered 8 high-paying Python jobs",
    "result_file": "outputs/filtered_jobs.json"
  }'

# === 7. Release Context (Mandatory!) ===
task-mind run release
