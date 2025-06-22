# AI Task Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered task management application that allows you to manage your tasks using natural language. Built with Streamlit, Groq, and SQLite.

## 🌟 Features

- **Natural Language Processing**: Interact with your task manager using natural language
- **Task Management**: Add, update, and view tasks with ease
- **Smart Organization**: Tasks are automatically categorized and organized
- **Task Reports**: Generate detailed reports of your tasks
- **Responsive UI**: Clean and intuitive web interface
- **Data Persistence**: All tasks are stored in a SQLite database

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key (Get it from [Groq Cloud](https://console.groq.com/))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-task-manager.git
   cd ai-task-manager
   ```

2. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Create a `.env` file and add your Groq API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your Groq API key.

### Running the Application

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

## 🛠️ Project Structure

```
ai-task-manager/
├── db/                    # Database files
├── logs/                  # Application logs
├── prompts/               # System prompts
├── tools/                 # Tool implementations
│   ├── add_task.py
│   ├── generate_task_report.py
│   ├── get_tasks_by_status.py
│   └── update_task_status.py
├── utils/                 # Utility functions
│   └── db_utils.py
├── .env.example           # Example environment variables
├── app.py                 # Streamlit application
├── main.py                # Main application logic
├── populate_db.py         # Script to populate sample data
└── requirements.txt       # Python dependencies
```

## 🤖 How It Works

The AI Task Manager uses Groq's language model to understand natural language commands and perform task management operations. Here's how it works:

1. The user interacts with the application through the Streamlit web interface
2. User input is processed by the Groq language model
3. The system identifies the intent and extracts relevant parameters
4. The appropriate tool is called to perform the requested action
5. The result is formatted and displayed to the user

## 📚 Usage Examples

### Adding a Task
- "Add a new task to complete the project report by Friday"
- "Create a high priority task for the team meeting tomorrow at 2 PM"

### Updating Tasks
- "Mark task 3 as completed"
- "Change the due date of 'Write documentation' to next Monday"

### Viewing Tasks
- "Show me all my tasks"
- "What tasks are due this week?"
- "List all high priority tasks"

### Generating Reports
- "Generate a weekly report"
- "Show me a summary of completed tasks"

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=development
DATABASE_URL=sqlite:///db/tasks.db
DARK_MODE=false
```

### Logging

Logs are stored in the `logs/` directory:
- `task_manager.log`: General application logs
- `task_manager_errors.log`: Error logs

## 🧪 Testing

To run the test suite:

```bash
pytest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Groq](https://groq.com/) for the powerful language model API
- [SQLite](https://www.sqlite.org/) for lightweight database storage