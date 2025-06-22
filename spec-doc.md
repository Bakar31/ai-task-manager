## ✅ **Project: Smart Task Agent**

### 📌 Overview:

An AI-powered task manager where users can:

* Add tasks via natural language
* Update task statuses (e.g. "mark task X as done")
* View tasks by status or priority
* Generate a task summary report (daily, weekly, etc.)

---

## 🧰 Tools (4 total — compact and powerful):

1. ### 📝 `add_task`

   * Parameters: `title`, `description` (optional), `due_date` (optional), `priority`, `status` (default = "todo")
   * Saves a task to an SQLite DB (or Postgres if you want to scale)

2. ### 🔄 `update_task_status`

   * Parameters: `task_title`, `new_status` (`todo`, `in progress`, `done`)
   * Finds task by title and updates status

3. ### 👀 `get_tasks_by_status`

   * Parameters: `status` (e.g., `todo`, `in progress`, `done`)
   * Returns a list of tasks in that category

4. ### 📊 `generate_task_report`

   * Parameters: `period` (e.g., `daily`, `weekly`)
   * Generates a summary: number of tasks added, completed, still pending
   * Optionally saves as a PDF or displays markdown

---

## 🧠 System Prompt (Simplified Example):

> You are a task manager assistant. You help users manage personal or work-related tasks.
> You understand natural language requests like “Add a task to write report by Friday” or “Mark grocery shopping as done”.
> You use tools to save tasks, update their status, fetch based on type, and generate progress reports.
> If a task is unclear, ask for more details. Be short, helpful, and action-oriented.

---

## 💬 Example Conversations:

---

**User**: *"Add a task to finish the AI assignment by Sunday, it’s urgent."*
→ Calls `add_task` with:

```json
{
  "title": "Finish the AI assignment",
  "due_date": "YYYY-MM-DD",
  "priority": "high",
  "status": "todo"
}
```

---

**User**: *"I finished the AI assignment."*
→ Calls `update_task_status` with:

```json
{
  "task_title": "Finish the AI assignment",
  "new_status": "done"
}
```

---

**User**: *"Show me what's in progress."*
→ Calls `get_tasks_by_status` with:

```json
{
  "status": "in progress"
}
```

---

**User**: *"Give me a weekly report."*
→ Calls `generate_task_report` with:

```json
{
  "period": "weekly"
}
```

---

## 🗂️ Suggested Folder Structure:

```
smart_task_agent/
├── main.py
├── tools/
│   ├── add_task.py
│   ├── update_task_status.py
│   ├── get_tasks_by_status.py
│   └── generate_task_report.py
├── db/
│   └── task_db.sqlite
├── prompts/
│   └── system_prompt.txt
└── utils/
    └── db_utils.py
```

---

## ⚙️ Tech Stack

* **DB**: SQLite (start simple)
* **Lang model**: OpenAI GPT-4o or GPT-3.5
* **Frontend**: `gradio` or CLI
* **PDF/Reports**: `reportlab`, `pandas`, or just Markdown

