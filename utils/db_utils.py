"""
Database utility functions for the AI Task Manager.

This module provides functions to interact with the SQLite database,
including creating tables and performing CRUD operations on tasks.
"""
import sqlite3
from typing import List, Dict, Any
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "task_db.sqlite")

def get_db_connection():
    """Create and return a database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize the database with the required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
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
        ''')
        
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_task_timestamp
        AFTER UPDATE ON tasks
        BEGIN
            UPDATE tasks SET updated_at = datetime('now') WHERE id = NEW.id;
        END;
        ''')
        
        conn.commit()

def add_task(title: str, description: str = None, due_date: str = None, 
            priority: str = 'medium', status: str = 'todo') -> int:
    """
    Add a new task to the database.
    
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
        cursor.execute('''
        INSERT INTO tasks (title, description, due_date, priority, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (title, description, due_date, priority, status))
        conn.commit()
        return cursor.lastrowid

def update_task_status(task_id: int, new_status: str) -> bool:
    """
    Update the status of a task.
    
    Args:
        task_id: The ID of the task to update
        new_status: The new status ('todo', 'in progress', 'done')
        
    Returns:
        bool: True if the update was successful, False otherwise
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE tasks 
        SET status = ? 
        WHERE id = ?
        ''', (new_status, task_id))
        conn.commit()
        return cursor.rowcount > 0

def get_tasks_by_status(status: str) -> List[Dict[str, Any]]:
    """
    Get all tasks with the given status.
    
    Args:
        status: The status to filter by ('todo', 'in progress', 'done')
        
    Returns:
        List[Dict[str, Any]]: A list of task dictionaries
    """
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM tasks 
        WHERE status = ? 
        ORDER BY 
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
                ELSE 4
            END,
            due_date ASC
        ''', (status,))
        return [dict(row) for row in cursor.fetchall()]

def get_task_summary() -> Dict[str, int]:
    """
    Get a summary of tasks by status.
    
    Returns:
        Dict[str, int]: A dictionary with task counts by status
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM tasks 
        GROUP BY status
        ''')
        result = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Ensure all statuses are present in the result
        for status in ['todo', 'in progress', 'done']:
            if status not in result:
                result[status] = 0
                
        return result

# Initialize the database when this module is imported
init_db()
