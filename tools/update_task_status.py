"""
Tool for updating the status of existing tasks.

This module provides functionality to update the status of tasks
in the task manager (e.g., from 'todo' to 'in progress' or 'done').
"""
from typing import Dict, Any
from pydantic import BaseModel, Field
from utils.db_utils import update_task_status as db_update_task_status


class UpdateTaskStatusInput(BaseModel):
    """Input model for the update_task_status tool."""
    task_id: int = Field(..., description="The ID of the task to update")
    new_status: str = Field(
        ...,
        description="The new status for the task (todo, in progress, done)",
        pattern=r"^(todo|in progress|done)$"
    )


def update_task_status(task_id: int, new_status: str) -> Dict[str, Any]:
    """
    Update the status of an existing task.
    
    Args:
        task_id: The ID of the task to update
        new_status: The new status for the task (todo, in progress, done)
        
    Returns:
        Dict containing the result of the operation
        
    Example:
        >>> update_task_status(1, "in progress")
        {'success': True, 'message': 'Task status updated successfully'}
    """
    try:
        # Validate input using Pydantic model
        task_input = UpdateTaskStatusInput(
            task_id=task_id,
            new_status=new_status
        )
        
        # Update task status in database
        success = db_update_task_status(
            task_id=task_input.task_id,
            new_status=task_input.new_status
        )
        
        if not success:
            return {
                "success": False,
                "message": f"Task with ID {task_input.task_id} not found"
            }
            
        return {
            "success": True,
            "message": "Task status updated successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update task status: {str(e)}"
        }


# Tool definition for the LLM
update_task_status_tool = {
    "name": "update_task_status",
    "description": "Update the status of an existing task",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to update"
            },
            "new_status": {
                "type": "string",
                "enum": ["todo", "in progress", "done"],
                "description": "The new status for the task"
            }
        },
        "required": ["task_id", "new_status"],
        "additionalProperties": False
    }
}
