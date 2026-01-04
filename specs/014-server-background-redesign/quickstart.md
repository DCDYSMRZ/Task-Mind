# Quickstart: Server Background Mode & Frontend Redesign

**Feature**: 014-server-background-redesign

## Overview

This feature introduces:
1. `task-mind server` command group for background web service management
2. Redesigned admin panel frontend with collapsible sidebar
3. Fixed port 8093 for simplified configuration
4. New Dashboard page replacing Tips

## Getting Started

### 1. Start the Server

```bash
# Background mode (default)
task-mind server

# Debug mode (foreground with logs)
task-mind server --debug
```

### 2. Access the Web Interface

Open http://127.0.0.1:8093 in your browser.

### 3. Navigate the Interface

The sidebar provides access to five pages:
- **Dashboard**: System overview and quick actions
- **Tasks**: Create and monitor automation tasks (default page)
- **Recipes**: Browse and manage recipes
- **Skills**: View registered skills
- **Settings**: Configure Task-Mind

Click the collapse button (☰) to minimize the sidebar.

### 4. Stop the Server

```bash
task-mind server stop
```

## Development Setup

### Backend Changes

Key files to modify:
```
src/task-mind/cli/server_command.py  # New command group
src/task-mind/server/daemon.py       # Process management
src/task-mind/server/runner.py       # Updated runner
```

### Frontend Changes

Build the frontend:
```bash
cd src/task-mind/gui/frontend
pnpm install
pnpm build
```

Key files:
```
src/components/layout/Sidebar.tsx    # Collapsible sidebar
src/components/layout/MainLayout.tsx # Admin panel layout
src/components/dashboard/DashboardPage.tsx  # New dashboard
src/styles/globals.css               # Style guide colors
```

### Testing

```bash
# Backend tests
pytest tests/

# Manual frontend testing
task-mind server --debug
# Open http://127.0.0.1:8093
```

## Migration from `task-mind serve`

| Old Command | New Command |
|-------------|-------------|
| `task-mind serve` | `task-mind server` (background) |
| `task-mind serve --debug` | `task-mind server --debug` |
| `task-mind serve -p 8080` | N/A (fixed port 8093) |

## Troubleshooting

### Port 8093 in use
```bash
# Check what's using the port
task-mind server status
# or
lsof -i :8093  # Linux/macOS
netstat -ano | findstr :8093  # Windows
```

### Server won't start
```bash
# Check for stale PID file
cat ~/.task-mind/server.pid
# Remove if process doesn't exist
rm ~/.task-mind/server.pid
```

### Frontend not loading
```bash
# Rebuild frontend
cd src/task-mind/gui/frontend
pnpm build
```
