"""
Script to populate the database with sample tasks.

This script can be run to initialize the database with sample tasks for testing.
"""
import sys
from utils.db_utils import populate_sample_tasks, clear_all_tasks

def main():
    """Main function to populate the database with sample tasks."""
    try:
        clear_result = clear_all_tasks()
        print(f"Cleared {clear_result['tasks_removed']} existing tasks.")
        
        result = populate_sample_tasks()
        print(f"Successfully added {result['tasks_added']} sample tasks to the database.")
        return 0
    except Exception as e:
        print(f"Error populating database: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
