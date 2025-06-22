"""
Streamlit UI for the AI Task Manager.

This module provides a web-based interface for interacting with the AI Task Manager
using Streamlit.
"""

import os
import traceback
import streamlit as st
from dotenv import load_dotenv
from main import TaskManagerAgent
from logging_config import setup_logger

logger = setup_logger("streamlit_ui")

st.set_page_config(
    page_title="AI Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

if "agent" not in st.session_state:
    st.session_state.agent = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_chat" not in st.session_state:
    st.session_state.show_chat = True


def initialize_agent():
    """
    Initialize the TaskManagerAgent if not already initialized.
    """
    if st.session_state.agent is not None:
        return True

    try:
        logger.info("Initializing TaskManagerAgent...")
        st.session_state.agent = TaskManagerAgent()
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your AI Task Assistant. How can I help you manage your tasks today?",
            }
        ]
        logger.info("TaskManagerAgent initialized successfully")
        st.rerun()

    except Exception as e:
        error_msg = f"Failed to initialize AI agent: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        st.error(error_msg)
        st.stop()


def display_chat():
    """
    Display the chat interface and handle user interactions.

    Handles displaying the chat history and processing user input.
    """
    try:
        st.title("AI Task Manager")
        st.caption("Talk to your AI assistant to manage your tasks")

        # Display chat messages with error handling for each message
        for i, message in enumerate(st.session_state.messages):
            try:
                with st.chat_message(message.get("role", "user")):
                    content = message.get("content", "")
                    if not isinstance(content, str):
                        content = str(content)
                    st.markdown(content)
            except Exception as e:
                logger.error(f"Error displaying message {i}: {str(e)}")
                logger.debug(f"Message content: {message}")

        # Chat input with validation
        if prompt := st.chat_input("How can I help you with your tasks?"):
            try:
                if not isinstance(prompt, str) or not prompt.strip():
                    raise ValueError("Empty or invalid input")

                st.session_state.messages.append(
                    {"role": "user", "content": prompt.strip()}
                )
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    try:
                        if (
                            "agent" not in st.session_state
                            or not st.session_state.agent
                        ):
                            raise RuntimeError("AI agent is not initialized")

                        response = st.session_state.agent.process_message(prompt)

                        if not response or not isinstance(response, str):
                            raise ValueError("Invalid response from AI agent")

                        st.session_state.messages.append(
                            {"role": "assistant", "content": response}
                        )
                        st.markdown(response)

                    except Exception as e:
                        error_msg = f"I'm sorry, I encountered an error processing your request: {str(e)}"
                        logger.error(f"Error in process_message: {str(e)}")
                        logger.debug(f"Traceback: {traceback.format_exc()}")

                        st.session_state.messages.append(
                            {"role": "assistant", "content": error_msg}
                        )
                        st.error(error_msg)

            except Exception as e:
                error_msg = f"Error processing your input: {str(e)}"
                logger.error(error_msg)
                logger.debug(f"Traceback: {traceback.format_exc()}")
                st.error(error_msg)

    except Exception as e:
        error_msg = f"An unexpected error occurred in the chat interface: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        st.error("A critical error occurred. Please refresh the page and try again.")
        st.stop()


def display_quick_actions():
    """
    Display quick action buttons and task summary in the sidebar.

    Handles errors gracefully and provides feedback to the user.
    """
    try:
        st.sidebar.title("Quick Actions")
        st.sidebar.markdown(
            """
            <div style='font-size: 0.92rem; color: #555; margin-bottom: 0.5rem;'>
                <b>Example messages:</b>
                <ul style='margin: 0.3em 0 0 1.2em; padding: 0; font-size: 0.89rem;'>
                    <li>Add a new task: <span style='color:#888;'>"Add task: Buy groceries"</span></li>
                    <li>Show all tasks: <span style='color:#888;'>"Show me all my tasks"</span></li>
                    <li>Mark task as done: <span style='color:#888;'>"Mark 'Buy groceries' as done"</span></li>
                    <li>Change due date: <span style='color:#888;'>"Change the due date of 'Write report' to Friday"</span></li>
                    <li>Generate report: <span style='color:#888;'>"Generate a weekly report"</span></li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.sidebar.divider()

        try:
            if hasattr(st.session_state, "agent") and st.session_state.agent:
                tool_call = type(
                    "obj",
                    (),
                    {
                        "function": type(
                            "func",
                            (),
                            {
                                "name": "generate_task_report",
                                "arguments": '{"period": "all"}',
                            },
                        )
                    },
                )

                summary = st.session_state.agent.handle_tool_call(tool_call)
                if summary and isinstance(summary, dict) and "summary" in summary:
                    st.sidebar.subheader("Task Summary")
                    col1, col2, col3 = st.sidebar.columns(3)

                    try:
                        col1.metric("To Do", summary["summary"].get("todo", 0))
                        col2.metric(
                            "In Progress", summary["summary"].get("in_progress", 0)
                        )
                        col3.metric("Done", summary["summary"].get("done", 0))
                    except Exception as e:
                        logger.error(f"Error displaying metrics: {str(e)}")
                        st.sidebar.error("Could not display task metrics.")

        except Exception as e:
            logger.error(f"Error loading task summary: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")

    except Exception as e:
        logger.critical(f"Critical error in quick actions: {str(e)}", exc_info=True)
        st.sidebar.error("An error occurred in the sidebar. Please refresh the page.")


def check_environment() -> bool:
    """
    Check if all required environment variables are set.

    Returns:
        bool: True if all required environment variables are set, False otherwise
    """
    required_vars = ["GROQ_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg = (
            "The following required environment variables are not set:\n\n"
            f"{', '.join(missing_vars)}\n\n"
            "Please set them in your .env file or environment variables."
        )
        st.error(error_msg)
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True


def setup_page():
    """Set up the Streamlit page configuration."""
    st.set_page_config(
        page_title="AI Task Manager",
        page_icon="✅",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.sidebar.markdown(
        """
        <div style="background: rgba(30, 30, 30, 0.9); padding: 0.6rem; border-radius: 0.5rem; margin-bottom: 1rem;">
            <div style="font-size: 0.9rem; font-weight: 600; color: #ffffff; margin-bottom: 0.2rem;">👨‍💻 Author</div>
            <div style="font-size: 0.75rem; color: #b0b0b0; margin-bottom: 0.5rem;">Abu Bakar Siddik - Machine Learning Engineer</div>
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; gap: 0.5rem;">
                <a href="mailto:abubakar1808031@gmail.com" style="color: #90caf9; text-decoration: none;" title="Email">✉️</a>
                <a href="https://github.com/bakar31" target="_blank" style="color: #90caf9; text-decoration: none;" title="GitHub">GitHub</a>
                <a href="https://linkedin.com/in/abu-bakar-siddik31" target="_blank" style="color: #90caf9; text-decoration: none;" title="LinkedIn">LinkedIn</a>
            </div>
        </div>
        <style>
            .stAlert {margin-bottom: 1rem;}
            .stAlert .stAlert-content {padding: 1rem;}
            .stAlert .stAlert-content code {background: rgba(255, 43, 43, 0.1); padding: 0.2rem 0.4rem; border-radius: 0.2rem;}
            a {text-decoration: none; transition: opacity 0.2s;}
            a:hover {opacity: 0.8;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    """
    Main function to run the Streamlit app.

    Handles initialization, error handling, and the main application flow.
    """
    try:
        setup_page()

        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "show_chat" not in st.session_state:
            st.session_state.show_chat = True

        if not check_environment():
            return

        if "agent" not in st.session_state or st.session_state.agent is None:
            if not initialize_agent():
                return

        try:
            display_quick_actions()
            display_chat()

        except Exception as e:
            error_msg = f"An error occurred in the application: {str(e)}"
            logger.critical(error_msg, exc_info=True)
            st.error(
                "A critical error occurred. Please refresh the page and try again."
            )

    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        st.error("A critical error occurred. Please refresh the page and try again.")

    st.sidebar.caption("AI Task Manager v1.0.0")

    if st.sidebar.button("🔄 Refresh Application"):
        st.rerun()


if __name__ == "__main__":
    main()
