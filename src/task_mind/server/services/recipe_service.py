"""Recipe management service.

Provides functionality for listing, viewing, and executing recipes.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from task_mind.server.services.base import get_utf8_env, run_subprocess

logger = logging.getLogger(__name__)


class RecipeService:
    """Service for recipe management operations."""

    # Cache for loaded recipes
    _cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def get_recipes(cls, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Get list of available recipes.

        Args:
            force_reload: If True, bypass cache and reload.

        Returns:
            List of recipe dictionaries.
        """
        if cls._cache is None or force_reload:
            cls._cache = cls._load_recipes()
        return cls._cache

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the recipe cache."""
        cls._cache = None

    @classmethod
    def _load_recipes(cls) -> List[Dict[str, Any]]:
        """Load recipes from task-mind recipe list command.

        Returns:
            List of recipe dictionaries.
        """
        recipes = []
        
        # Try to use RecipeRegistry directly for better performance
        try:
            from task_mind.recipes.registry import RecipeRegistry
            registry = RecipeRegistry()
            registry.scan()
            
            for recipe in registry.list_all():
                recipes.append({
                    "name": recipe.metadata.name,
                    "description": recipe.metadata.description,
                    "category": recipe.metadata.type,
                    "tags": recipe.metadata.tags,
                    "path": str(recipe.script_path),
                    "source": recipe.source.lower(),
                    "runtime": recipe.metadata.runtime,
                })
            
            if recipes:
                return recipes
        except Exception as e:
            logger.warning("Failed to load recipes from RecipeRegistry: %s", e)
        
        # Fallback: try CLI command
        try:
            result = run_subprocess(
                ["task-mind", "recipe", "list", "--format", "json"],
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                for item in data:
                    recipes.append({
                        "name": item.get("name", ""),
                        "description": item.get("description"),
                        "category": item.get("type", "atomic"),
                        "tags": item.get("tags", []),
                        "path": item.get("path"),
                        "source": item.get("source"),
                        "runtime": item.get("runtime"),
                    })
        except Exception as e:
            logger.warning("Failed to load recipes from command: %s", e)

        # Fallback to filesystem if no recipes loaded
        if not recipes:
            recipes = cls._load_recipes_from_filesystem()

        return recipes

    @staticmethod
    def _load_recipes_from_filesystem() -> List[Dict[str, Any]]:
        """Load recipes from filesystem as fallback.

        Returns:
            List of recipe dictionaries.
        """
        recipes = []
        recipe_dirs = [
            Path.home() / ".task-mind" / "recipes",
        ]

        for recipe_dir in recipe_dirs:
            if not recipe_dir.exists():
                continue

            # Find all recipe files (.js, .py, .sh)
            for ext in ["*.js", "*.py", "*.sh"]:
                for path in recipe_dir.rglob(ext):
                    if path.stem == "__init__":
                        continue
                    
                    # Use parent directory name as recipe name
                    recipe_name = path.parent.name if path.name in ["recipe.js", "recipe.py", "recipe.sh", "index.js", "index.py"] else path.stem
                    
                    # Try to read metadata from recipe.md
                    metadata = {}
                    md_path = path.parent / "recipe.md"
                    if md_path.exists():
                        try:
                            content = md_path.read_text(encoding="utf-8")
                            # Simple parsing for description (first paragraph after title)
                            lines = [l.strip() for l in content.split('\n') if l.strip()]
                            for i, line in enumerate(lines):
                                if not line.startswith('#') and len(line) > 10:
                                    metadata['description'] = line
                                    break
                        except Exception:
                            pass
                    
                    recipes.append({
                        "name": recipe_name,
                        "description": metadata.get('description'),
                        "category": "atomic" if "atomic" in str(path) else "workflow",
                        "tags": [],
                        "path": str(path),
                        "source": "user",
                        "runtime": path.suffix[1:] if path.suffix else None,
                    })

        return recipes

    @classmethod
    def get_recipe(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get recipe details by name.

        Args:
            name: Recipe name.

        Returns:
            Recipe dictionary or None if not found.
        """
        # Try to use RecipeRegistry directly for complete metadata
        try:
            from task_mind.recipes.registry import RecipeRegistry
            registry = RecipeRegistry()
            registry.scan()
            
            recipe = registry.find(name)
            
            # Read source code
            source_code = None
            try:
                source_code = recipe.script_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning("Failed to read recipe source code: %s", e)
            
            # Read full markdown content
            markdown_content = None
            try:
                markdown_content = recipe.metadata_path.read_text(encoding="utf-8")
                # Remove YAML frontmatter
                if markdown_content.startswith('---'):
                    parts = markdown_content.split('---', 2)
                    if len(parts) >= 3:
                        markdown_content = parts[2].strip()
            except Exception:
                pass
            
            return {
                "name": recipe.metadata.name,
                "type": recipe.metadata.type,
                "runtime": recipe.metadata.runtime,
                "version": recipe.metadata.version,
                "description": recipe.metadata.description,
                "use_cases": recipe.metadata.use_cases,
                "output_targets": recipe.metadata.output_targets,
                "inputs": recipe.metadata.inputs,
                "outputs": recipe.metadata.outputs,
                "dependencies": recipe.metadata.dependencies,
                "tags": recipe.metadata.tags,
                "env": recipe.metadata.env,
                "source": recipe.source.lower(),
                "script_path": str(recipe.script_path),
                "source_code": source_code,
                "markdown_content": markdown_content,
            }
        except Exception as e:
            logger.warning("Failed to get recipe from RecipeRegistry: %s", e)
        
        # Fallback: try CLI command
        try:
            result = run_subprocess(
                ["task-mind", "recipe", "info", name, "--format", "json"],
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                # Read source code if script_path exists
                script_path = data.get("script_path")
                if script_path:
                    try:
                        data["source_code"] = Path(script_path).read_text(encoding="utf-8")
                    except Exception as e:
                        logger.warning("Failed to read recipe source code: %s", e)
                        data["source_code"] = None
                return data
        except Exception as e:
            logger.warning("Failed to get recipe info from command: %s", e)

        # Last fallback to list lookup
        recipes = cls.get_recipes()
        for recipe in recipes:
            if recipe.get("name") == name:
                return recipe

        return None

    @staticmethod
    def run_recipe(
        name: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """Execute a recipe.

        Args:
            name: Recipe name.
            params: Optional parameters.
            timeout: Timeout in seconds (default 300).

        Returns:
            Result dictionary with status, output, and optionally error.
        """
        import time

        start_time = time.time()

        try:
            cmd = ["task-mind", "recipe", "run", name]
            if params:
                cmd.extend(["--params", json.dumps(params)])

            result = run_subprocess(cmd, timeout=timeout)

            duration_ms = int((time.time() - start_time) * 1000)

            if result.returncode == 0:
                output = result.stdout.strip()
                return {
                    "status": "ok",
                    "output": output,
                    "error": None,
                    "duration_ms": duration_ms,
                }
            else:
                error = result.stderr.strip() or "Recipe execution failed"
                return {
                    "status": "error",
                    "output": None,
                    "error": error,
                    "duration_ms": duration_ms,
                }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            if "TimeoutExpired" in error_msg or "timed out" in error_msg.lower():
                error_msg = "Execution timed out"
            logger.error("Recipe execution failed: %s", e)
            return {
                "status": "error",
                "output": None,
                "error": error_msg,
                "duration_ms": duration_ms,
            }
