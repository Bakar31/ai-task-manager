"""
Tool for adding new tasks to the task manager.

This module provides functionality to add new tasks with various attributes
like title, description, due date, priority, and status.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from utils.db_utils import add_task as db_add_task


class AddTaskInput(BaseModel):
    """Input model for the add_task tool."""

    title: str = Field(..., description="The title of the task")
    description: Optional[str] = Field(
        None, description="Optional description providing more details about the task"
    )
    due_date: Optional[str] = Field(
        None, description="Optional due date in YYYY-MM-DD format"
    )
    priority: str = Field(
        "medium",
        description="Priority level of the task (low, medium, high)",
        pattern=r"^(low|medium|high)$",
    )
    status: str = Field(
        "todo",
        description="Current status of the task (todo, in progress, done)",
        pattern=r"^(todo|in progress|done)$",
    )

    @field_validator("due_date")
    def validate_due_date(cls, v):
        """Validate the due_date format."""
        if v is None:
            return v
        try:

            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError as exc:
            raise ValueError("due_date must be in YYYY-MM-DD format") from exc


def add_task(
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: str = "medium",
    status: str = "todo",
) -> Dict[str, Any]:
    """
    Add a new task to the task manager with proper datetime handling.

    Args:
        title: The title of the task
        description: Optional description of the task
        due_date: Optional due date in YYYY-MM-DD format
        priority: Priority level (low, medium, high)
        status: Current status (todo, in progress, done)

    Returns:
        Dict containing the result of the operation with task details

    Example:
        >>> add_task("Complete project", "Finish the AI assignment", "2023-12-31", "high")
        {
            'success': True,
            'task_id': 1,
            'message': 'Task added successfully',
            'created_at': '2025-06-22 21:10:00',
            'due_date': '2025-06-22'
        }
    """
    try:
        created_at = datetime.now().isoformat(sep=" ", timespec="seconds")

        task_input = AddTaskInput(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            status=status,
        )

        task_id = db_add_task(
            title=task_input.title,
            description=task_input.description,
            due_date=task_input.due_date,
            priority=task_input.priority,
            status=task_input.status,
        )

        response = {
            "success": True,
            "task_id": task_id,
            "message": "Task added successfully",
            "created_at": created_at,
        }

        if due_date:
            response["due_date"] = due_date

        return response

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to add task: {str(e)}",
        }


add_task_tool = {
    "type": "function",
    "function": {
        "name": "add_task",
        "description": "Add a new task to the task manager",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The title of the task"},
                "description": {
                    "type": "string",
                    "description": "Optional description of the task",
                },
                "due_date": {
                    "type": "string",
                    "description": "Optional due date in YYYY-MM-DD format",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Priority level of the task (default: medium)",
                },
                "status": {
                    "type": "string",
                    "enum": ["todo", "in progress", "done"],
                    "description": "Current status of the task (default: todo)",
                },
            },
            "required": ["title"],
            "additionalProperties": False,
        },
    },
}
