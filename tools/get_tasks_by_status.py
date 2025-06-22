"""
Tool for retrieving tasks filtered by status.

This module provides functionality to get a list of tasks
filtered by their current status (todo, in progress, or done).
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
from utils.db_utils import get_tasks_by_status as db_get_tasks_by_status


class GetTasksByStatusInput(BaseModel):
    """Input model for the get_tasks_by_status tool."""

    status: str = Field(
        ...,
        description="The status to filter tasks by (todo, in progress, done)",
        pattern=r"^(todo|in progress|done)$",
    )


def get_tasks_by_status(status: str) -> Dict[str, Any]:
    """
    Get all tasks with the specified status.

    Args:
        status: The status to filter tasks by (todo, in progress, done)

    Returns:
        Dict containing the list of tasks with the specified status

    Example:
        >>> get_tasks_by_status("todo")
        {
            'success': True,
            'tasks': [
                {'id': 1, 'title': 'Complete project', 'status': 'todo', ...},
                ...
            ]
        }
    """
    try:
        task_input = GetTasksByStatusInput(status=status)
        tasks = db_get_tasks_by_status(task_input.status)
        tasks_list = [dict(task) for task in tasks]

        return {"success": True, "tasks": tasks_list}

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get tasks: {str(e)}",
        }


def get_all_tasks() -> Dict[str, Any]:
    """
    Get all tasks regardless of status.

    Returns:
        Dict containing all tasks grouped by status
    """
    try:
        all_tasks = {}
        for status in ["todo", "in progress", "done"]:
            tasks = db_get_tasks_by_status(status)
            all_tasks[status] = [dict(task) for task in tasks]

        return {"success": True, "tasks": all_tasks}

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get all tasks: {str(e)}",
        }


get_tasks_by_status_tool = {
    "type": "function",
    "function": {
        "name": "get_tasks_by_status",
        "description": "Get tasks filtered by their current status",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["todo", "in progress", "done"],
                    "description": "The status to filter tasks by",
                }
            },
            "required": ["status"],
            "additionalProperties": False,
        },
    },
}

get_all_tasks_tool = {
    "type": "function",
    "function": {
        "name": "get_all_tasks",
        "description": "Get all tasks grouped by their status",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
}
