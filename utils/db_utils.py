"""
Database utility functions for the AI Task Manager.

This module provides functions to interact with the SQLite database,
including creating tables and performing CRUD operations on tasks.
"""

import sqlite3
from typing import List, Dict, Any
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "task_db.sqlite"
)


def get_db_connection():
    """Create and return a database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initialize the database with the required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
            status TEXT DEFAULT 'todo' CHECK(status IN ('todo', 'in progress', 'done')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        cursor.execute(
            """
        CREATE TRIGGER IF NOT EXISTS update_task_timestamp
        AFTER UPDATE ON tasks
        BEGIN
            UPDATE tasks SET updated_at = datetime('now') WHERE id = NEW.id;
        END;
        """
        )

        conn.commit()


def add_task(
    title: str,
    description: str = None,
    due_date: str = None,
    priority: str = "medium",
    status: str = "todo",
) -> int:
    """
    Add a new task to the database.

    Note: The database automatically sets created_at and updated_at timestamps
    using SQLite's CURRENT_TIMESTAMP.

    Args:
        title: The title of the task
        description: Optional description of the task
        due_date: Optional due date in YYYY-MM-DD format
        priority: Priority level ('low', 'medium', 'high')
        status: Current status of the task ('todo', 'in progress', 'done')

    Returns:
        int: The ID of the newly created task
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            -- created_at and updated_at are automatically set by the database
            -- using DEFAULT CURRENT_TIMESTAMP in the schema
            INSERT INTO tasks (title, description, due_date, priority, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, description, due_date, priority, status),
        )
        conn.commit()
        return cursor.lastrowid


def update_task_status(task_id: int, new_status: str) -> Dict[str, Any]:
    """
    Update the status of a task and return the updated task details.

    This function updates the task status and automatically sets the updated_at
    timestamp to the current time. The database trigger 'update_task_timestamp'
    ensures updated_at is always current on any update.

    Args:
        task_id: The ID of the task to update
        new_status: The new status ('todo', 'in progress', 'done')

    Returns:
        Dict containing:
        - success: Boolean indicating if the update was successful
        - message: Status message
        - task: Dict containing all task fields including timestamps
               (created_at, updated_at) in ISO 8601 format

    Example:
        {
            "success": True,
            "message": "Task status updated successfully",
            "task": {
                "id": 1,
                "title": "Task title",
                "status": "in progress",
                "created_at": "2025-06-22 15:30:00",
                "updated_at": "2025-06-22 16:45:00",
                ...
            }
        }
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Update task status and set updated_at to current time
        # The RETURNING clause returns the updated row
        cursor.execute(
            """
            UPDATE tasks 
            SET status = ?,
                updated_at = datetime('now')
            WHERE id = ?
            RETURNING *  -- Returns all columns of the updated row
            """,
            (new_status, task_id),
        )

        # Fetch the updated task data
        updated_task = cursor.fetchone()
        conn.commit()

        if not updated_task:
            return {"success": False, "message": f"Task with ID {task_id} not found"}

        # Convert SQLite Row to dict for easier handling
        columns = [column[0] for column in cursor.description]
        task_dict = dict(zip(columns, updated_task))

        # SQLite returns datetime as string in ISO 8601 format
        # No conversion needed as we want to keep it consistent

        return {
            "success": True,
            "message": "Task status updated successfully",
            "task": task_dict,  # Includes all task fields including timestamps
        }


def get_tasks_by_status(status: str) -> List[Dict[str, Any]]:
    """
    Get all tasks with the given status, including all timestamps.

    Args:
        status: The status to filter by ('todo', 'in progress', 'done')

    Returns:
        List[Dict[str, Any]]: A list of task dictionaries with all fields including timestamps

    Example:
        >>> get_tasks_by_status('todo')
        [
            {
                'id': 1,
                'title': 'Task 1',
                'description': 'Description',
                'due_date': '2025-06-22',
                'priority': 'medium',
                'status': 'todo',
                'created_at': '2025-06-22 15:30:00',
                'updated_at': '2025-06-22 15:30:00'
            },
            ...
        ]
    """
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                id, 
                title, 
                description, 
                due_date, 
                priority, 
                status,
                created_at,
                updated_at
            FROM tasks 
            WHERE status = ?
            ORDER BY created_at DESC
            """,
            (status,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_task_summary() -> Dict[str, int]:
    """
    Get a summary of tasks by status.

    Returns:
        Dict[str, int]: A dictionary with task counts by status
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT status, COUNT(*) as count 
        FROM tasks 
        GROUP BY status
        """
        )
        result = {row[0]: row[1] for row in cursor.fetchall()}

        # Ensure all statuses are present in the result
        for status in ["todo", "in progress", "done"]:
            if status not in result:
                result[status] = 0

        return result


def populate_sample_tasks() -> Dict[str, int]:
    """
    Populate the database with sample tasks for testing and development.

    Returns:
        Dict[str, int]: A dictionary with the count of tasks added
    """
    sample_tasks = [
        {
            "title": "Complete AI assignment",
            "description": "Finish the machine learning project for CS101",
            "due_date": "2023-12-15",
            "priority": "high",
            "status": "todo",
        },
        {
            "title": "Grocery shopping",
            "description": "Buy milk, eggs, and bread",
            "due_date": "2023-12-10",
            "priority": "medium",
            "status": "todo",
        },
        {
            "title": "Call mom",
            "description": "Wish her happy birthday",
            "due_date": "2023-12-12",
            "priority": "high",
            "status": "in progress",
        },
        {
            "title": "Read research paper",
            "description": "Read the latest paper on transformers",
            "due_date": "2023-12-20",
            "priority": "low",
            "status": "todo",
        },
        {
            "title": "Submit expense report",
            "description": "Submit monthly expenses to accounting",
            "due_date": "2023-12-05",
            "priority": "medium",
            "status": "done",
        },
    ]

    added_count = 0
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # First, check if we already have any tasks to avoid duplicates
        cursor.execute("SELECT COUNT(*) FROM tasks")
        if cursor.fetchone()[0] == 0:
            for task in sample_tasks:
                cursor.execute(
                    """
                INSERT INTO tasks (title, description, due_date, priority, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        task["title"],
                        task["description"],
                        task["due_date"],
                        task["priority"],
                        task["status"],
                    ),
                )
                added_count += 1
            conn.commit()

    return {"tasks_added": added_count}


def clear_all_tasks() -> Dict[str, int]:
    """
    Remove all tasks from the database.

    Returns:
        Dict[str, int]: A dictionary with the count of tasks removed
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM tasks")
        conn.commit()
    return {"tasks_removed": count}


init_db()

# Uncomment the following line to populate with sample data when the module is imported
# populate_sample_tasks()
