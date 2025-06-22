"""
Tool for generating task reports.

This module provides functionality to generate reports about tasks,
including statistics and summaries for different time periods.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from utils.db_utils import get_task_summary, get_tasks_by_status


class GenerateReportInput(BaseModel):
    """Input model for the generate_task_report tool."""
    period: str = Field(
        "daily",
        description="The time period for the report (daily, weekly, monthly, all)",
        pattern=r"^(daily|weekly|monthly|all)$"
    )


def get_date_range(period: str) -> tuple[Optional[str], Optional[str]]:
    """
    Get date range based on the specified period.
    
    Args:
        period: The time period (daily, weekly, monthly, all)
        
    Returns:
        Tuple of (start_date, end_date) as strings in YYYY-MM-DD format
    """
    today = datetime.now().date()
    
    if period == "daily":
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif period == "weekly":
        start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=6-today.weekday())).strftime("%Y-%m-%d")
    elif period == "monthly":
        first_day = today.replace(day=1)
        if first_day.month == 12:
            last_day = first_day.replace(year=first_day.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = first_day.replace(month=first_day.month + 1, day=1) - timedelta(days=1)
        start_date = first_day.strftime("%Y-%m-%d")
        end_date = last_day.strftime("%Y-%m-%d")
    else:  # all
        start_date = None
        end_date = None
        
    return start_date, end_date


def generate_task_report(period: str = "daily") -> Dict[str, Any]:
    """
    Generate a task report for the specified time period.
    
    Args:
        period: The time period for the report (daily, weekly, monthly, all)
        
    Returns:
        Dict containing the task report
        
    Example:
        >>> generate_task_report("weekly")
        {
            'success': True,
            'period': 'weekly',
            'start_date': '2023-11-27',
            'end_date': '2023-12-03',
            'summary': {
                'total_tasks': 10,
                'todo': 5,
                'in_progress': 3,
                'done': 2
            },
            'recently_completed': [...],
            'upcoming_deadlines': [...]
        }
    """
    try:
        # Validate input using Pydantic model
        report_input = GenerateReportInput(period=period)
        
        # Get date range for the report
        start_date, end_date = get_date_range(report_input.period)
        
        # Get task summary
        summary = get_task_summary()
        
        # Get recently completed tasks (last 5)
        completed_tasks = get_tasks_by_status("done")
        recently_completed = sorted(
            [dict(task) for task in completed_tasks],
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )[:5]
        
        # Get upcoming deadlines (next 7 days)
        upcoming_deadlines = []
        if period != "all":
            all_tasks = []
            for status in ["todo", "in progress"]:
                all_tasks.extend(get_tasks_by_status(status))
                
            upcoming_deadlines = sorted(
                [
                    dict(task) for task in all_tasks 
                    if task.get("due_date") and 
                    (start_date is None or task["due_date"] >= start_date) and
                    (end_date is None or task["due_date"] <= end_date)
                ],
                key=lambda x: x.get("due_date", "")
            )[:5]
        
        return {
            "success": True,
            "period": report_input.period,
            "start_date": start_date,
            "end_date": end_date,
            "summary": {
                "total_tasks": sum(summary.values()),
                "todo": summary.get("todo", 0),
                "in_progress": summary.get("in progress", 0),
                "done": summary.get("done", 0)
            },
            "recently_completed": recently_completed,
            "upcoming_deadlines": upcoming_deadlines
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate task report: {str(e)}"
        }


# Tool definition for the LLM
generate_task_report_tool = {
    "name": "generate_task_report",
    "description": "Generate a task report for the specified time period",
    "parameters": {
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "enum": ["daily", "weekly", "monthly", "all"],
                "description": "The time period for the report (default: daily)"
            }
        },
        "required": [],
        "additionalProperties": False
    }
}
