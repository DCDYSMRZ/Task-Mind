# task-mind Community Recipes

This directory contains community-contributed recipes for task-mind.

## Using Community Recipes

### Install a Recipe

```bash
# Install from community repository
task-mind recipe install community:<recipe-name>

# Install with force overwrite
task-mind recipe install community:<recipe-name> --force
```

### Search for Recipes

```bash
# Search by keyword
task-mind recipe search <query>

# List all community recipes
task-mind recipe list --source community
```

### Update Installed Recipes

```bash
# Update a specific recipe
task-mind recipe update <recipe-name>

# Update all installed recipes
task-mind recipe update --all
```

### Uninstall a Recipe

```bash
task-mind recipe uninstall <recipe-name>
```

## Installed Recipe Location

Community recipes are installed to `~/.task-mind/community-recipes/`.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on submitting your own recipes.

## License

All recipes in this directory are contributed under the same license as task-mind.
