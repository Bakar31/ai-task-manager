"""
Streamlit UI for the AI Task Manager.

This module provides a web-based interface for interacting with the AI Task Manager
using Streamlit.
"""
import os
import json
import logging
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List
import streamlit as st
from dotenv import load_dotenv

# Import the main application class
from main import TaskManagerAgent, TOOLS
from logging_config import setup_logger

# Set up logging
logger = setup_logger("streamlit_ui")

# Configure page
st.set_page_config(
    page_title="AI Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_chat" not in st.session_state:
    st.session_state.show_chat = True


def initialize_agent() -> bool:
    """
    Initialize the TaskManagerAgent if not already initialized.
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    if st.session_state.agent is not None:
        return True
        
    try:
        logger.info("Initializing TaskManagerAgent...")
        st.session_state.agent = TaskManagerAgent()
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Hello! I'm your AI Task Assistant. How can I help you manage your tasks today?"
            }
        ]
        logger.info("TaskManagerAgent initialized successfully")
        st.rerun()
        return True
        
    except Exception as e:
        error_msg = f"Failed to initialize AI agent: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        st.error(error_msg)
        st.stop()
        return False


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
                    
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": prompt.strip()})
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Get assistant response with error handling
                with st.chat_message("assistant"):
                    try:
                        if "agent" not in st.session_state or not st.session_state.agent:
                            raise RuntimeError("AI agent is not initialized")
                            
                        response = st.session_state.agent.process_message(prompt)
                        
                        # Validate and process the response
                        if not response or not isinstance(response, str):
                            raise ValueError("Invalid response from AI agent")
                            
                        # Add assistant response to chat
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response
                        })
                        st.markdown(response)
                        
                    except Exception as e:
                        error_msg = f"I'm sorry, I encountered an error processing your request: {str(e)}"
                        logger.error(f"Error in process_message: {str(e)}")
                        logger.debug(f"Traceback: {traceback.format_exc()}")
                        
                        # Add error message to chat
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
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
        
        # Create two columns for the action buttons
        col1, col2 = st.sidebar.columns(2)
        
        # Add Task button
        if col1.button("📝 Add Task"):
            try:
                st.session_state.show_chat = True
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "I want to add a new task"
                })
                st.rerun()
            except Exception as e:
                logger.error(f"Error in Add Task button: {str(e)}")
                st.sidebar.error("Failed to add a new task. Please try again.")
        
        # View Tasks button
        if col2.button("📊 View Tasks"):
            try:
                st.session_state.show_chat = True
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Show me all my tasks"
                })
                st.rerun()
            except Exception as e:
                logger.error(f"Error in View Tasks button: {str(e)}")
                st.sidebar.error("Failed to view tasks. Please try again.")
        
        # Generate Report button
        if st.sidebar.button("📋 Generate Report"):
            try:
                st.session_state.show_chat = True
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Generate a task report"
                })
                st.rerun()
            except Exception as e:
                logger.error(f"Error in Generate Report button: {str(e)}")
                st.sidebar.error("Failed to generate report. Please try again.")
        
        st.sidebar.divider()
        
        # Display task summary with error handling
        try:
            if hasattr(st.session_state, 'agent') and st.session_state.agent:
                # Create a tool call object for the task summary
                tool_call = type('obj', (), {
                    'function': type('func', (), {
                        'name': 'generate_task_report',
                        'arguments': '{"period": "all"}'
                    })
                })
                
                # Get the task summary
                summary = st.session_state.agent.handle_tool_call(tool_call)
                
                # Display the summary if available
                if summary and isinstance(summary, dict) and "summary" in summary:
                    st.sidebar.subheader("Task Summary")
                    
                    # Create columns for the metrics
                    col1, col2, col3 = st.sidebar.columns(3)
                    
                    # Display each metric with error handling
                    try:
                        col1.metric("To Do", summary["summary"].get("todo", 0))
                        col2.metric("In Progress", summary["summary"].get("in_progress", 0))
                        col3.metric("Done", summary["summary"].get("done", 0))
                    except Exception as e:
                        logger.error(f"Error displaying metrics: {str(e)}")
                        st.sidebar.error("Could not display task metrics.")
                
        except Exception as e:
            logger.error(f"Error loading task summary: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            # Don't show error to user for summary as it's not critical
            
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
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS for better error message display
    st.markdown("""
    <style>
        .stAlert {margin-bottom: 1rem;}
        .stAlert .stAlert-content {padding: 1rem;}
        .stAlert .stAlert-content code {background: rgba(255, 43, 43, 0.1); padding: 0.2rem 0.4rem; border-radius: 0.2rem;}
    </style>
    """, unsafe_allow_html=True)


def main():
    """
    Main function to run the Streamlit app.
    
    Handles initialization, error handling, and the main application flow.
    """
    try:
        # Set up the page
        setup_page()
        
        # Initialize session state if needed
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "show_chat" not in st.session_state:
            st.session_state.show_chat = True
        
        # Check environment variables
        if not check_environment():
            return
        
        # Initialize the agent if not already done
        if "agent" not in st.session_state or st.session_state.agent is None:
            if not initialize_agent():
                return
        
        try:
            # Display quick actions in sidebar
            display_quick_actions()
            
            # Display the main chat interface
            display_chat()
            
        except Exception as e:
            error_msg = f"An error occurred in the application: {str(e)}"
            logger.critical(error_msg, exc_info=True)
            st.error("A critical error occurred. Please refresh the page and try again.")
    
    except Exception as e:
        # Catch any unhandled exceptions
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        st.error("A critical error occurred. Please refresh the page and try again.")
    
    # Add a small footer with version info
    st.sidebar.markdown("---")
    st.sidebar.caption("AI Task Manager v1.0.0")
    
    # Add a refresh button in case of issues
    if st.sidebar.button("🔄 Refresh Application"):
        st.rerun()


if __name__ == "__main__":
    main()
