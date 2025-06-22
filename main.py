"""
AI Task Manager - Main Application

This module contains the main application class that ties together the LLM,
tools, and user interface for the AI Task Manager.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import groq
from groq import GroqError
from constant import MAX_ITERATIONS, TEMPERATURE, MAX_TOKENS, FALLBACK_MODEL

from tools.add_task import add_task, add_task_tool
from tools.update_task_status import update_task_status, update_task_status_tool
from tools.get_tasks_by_status import (
    get_tasks_by_status,
    get_all_tasks,
    get_tasks_by_status_tool,
    get_all_tasks_tool,
)
from tools.generate_task_report import generate_task_report, generate_task_report_tool
from logging_config import setup_logger

logger = setup_logger(__name__)
load_dotenv()

TOOLS = [
    add_task_tool,
    update_task_status_tool,
    get_tasks_by_status_tool,
    get_all_tasks_tool,
    generate_task_report_tool,
]


class TaskManagerAgent:
    """Main application class for the AI Task Manager."""

    def __init__(self):
        """Initialize the TaskManagerAgent with Groq client and tools."""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set")

            self.client = groq.Client(api_key=api_key)
            self.messages = []
            self.tool_calls = []
            self.load_system_prompt()
            logger.info("TaskManagerAgent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize TaskManagerAgent: {str(e)}")
            raise

    def load_system_prompt(self):
        """Load the system prompt from file."""
        try:
            prompt_path = Path(__file__).parent / "prompts" / "system_prompt.txt"
            if not prompt_path.exists():
                raise FileNotFoundError(
                    f"System prompt file not found at {prompt_path}"
                )

            with open(prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read().strip()

            if not self.system_prompt:
                raise ValueError("System prompt is empty")

            self.messages = [{"role": "system", "content": self.system_prompt}]
            logger.debug("System prompt loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load system prompt: {str(e)}")

            self.system_prompt = """You are an AI Task Manager assistant. Help users manage their tasks efficiently.
            Be concise, helpful, and action-oriented in your responses."""
            self.messages = [{"role": "system", "content": self.system_prompt}]
            logger.warning("Using fallback system prompt")

    def handle_tool_call(self, tool_call):
        """
        Handle a single tool call with tracking for UI.

        Args:
            tool_call: The tool call to handle

        Returns:
            Dict containing the tool response

        Raises:
            ValueError: If the tool call is invalid or missing required fields
            Exception: For any unexpected errors during tool execution
        """
        if (
            not tool_call
            or not hasattr(tool_call, "function")
            or not tool_call.function
        ):
            error_msg = "Invalid tool call: missing function information"
            logger.error(error_msg)
            return {"error": error_msg, "success": False}

        function_name = getattr(tool_call.function, "name", "")
        function_args_str = getattr(tool_call.function, "arguments", "{}")

        if not function_name:
            error_msg = "Invalid tool call: missing function name"
            logger.error(error_msg)
            return {"error": error_msg, "success": False}

        try:
            function_args = json.loads(function_args_str)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in function arguments: {str(e)}"
            logger.error(f"{error_msg}. Raw arguments: {function_args_str}")
            return {"error": error_msg, "success": False}

        tool_call_id = f"toolcall_{len(self.tool_calls) + 1}"
        tool_call_info = {
            "id": tool_call_id,
            "name": function_name,
            "args": function_args,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "result": None,
            "error": None,
        }
        self.tool_calls.append(tool_call_info)
        logger.info(f"Calling function: {function_name} with args: {function_args}")

        try:
            valid_functions = {
                "add_task": add_task,
                "update_task_status": update_task_status,
                "get_tasks_by_status": get_tasks_by_status,
                "get_all_tasks": get_all_tasks,
                "generate_task_report": generate_task_report,
            }

            if function_name not in valid_functions:
                error_msg = f"Unknown function: {function_name}"
                logger.error(error_msg)
                return {"error": error_msg, "success": False}

            tool_call_info = next(
                (t for t in self.tool_calls if t["id"] == tool_call_id), None
            )

            try:
                if function_name in ["get_all_tasks"]:
                    result = valid_functions[function_name]()
                else:
                    result = valid_functions[function_name](**function_args)

                if not isinstance(result, dict):
                    result = {"result": result, "success": True}

                if "success" not in result:
                    result["success"] = True

                if tool_call_info:
                    tool_call_info.update(
                        {
                            "status": "completed",
                            "end_time": datetime.now().isoformat(),
                            "result": result,
                            "success": True,
                        }
                    )

                logger.info(f"Function {function_name} completed successfully")
                logger.debug(f"Function {function_name} result: {result}")

                return result

            except Exception as e:
                error_msg = str(e)
                if tool_call_info:
                    tool_call_info.update(
                        {
                            "status": "error",
                            "end_time": datetime.now().isoformat(),
                            "error": error_msg,
                            "success": False,
                        }
                    )
                logger.error(f"Error in function {function_name}: {error_msg}")
                raise

        except TypeError as e:
            error_msg = f"Invalid arguments for {function_name}: {str(e)}"
            logger.error(f"{error_msg}. Args: {function_args}")
            return {"error": error_msg, "success": False}

        except Exception as e:
            error_msg = f"Error in {function_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "error": f"An error occurred while processing your request: {str(e)}",
                "success": False,
            }

    def process_message(self, user_message: str) -> str:
        """
        Process a user message and return the assistant's response.

        Args:
            user_message: The user's message

        Returns:
            The assistant's response as a string

        Raises:
            groq.GroqError: If there's an error communicating with the Groq API
            Exception: For any other unexpected errors
        """
        if not user_message or not isinstance(user_message, str):
            error_msg = "Invalid message: message must be a non-empty string"
            logger.error(error_msg)
            return "I'm sorry, I didn't receive a valid message. Please try again."

        try:
            self.messages.append({"role": "user", "content": user_message.strip()})
            logger.info(f"Processing user message: {user_message[:100]}...")

            current_iteration = 0

            while current_iteration < MAX_ITERATIONS:
                current_iteration += 1

                try:
                    response = self.client.chat.completions.create(
                        model=os.getenv("MODEL", FALLBACK_MODEL),
                        messages=self.messages,
                        tools=TOOLS,
                        tool_choice="auto",
                        temperature=TEMPERATURE,
                        max_tokens=MAX_TOKENS,
                    )

                    if not response.choices or not response.choices[0].message:
                        error_msg = "Empty or invalid response from the model"
                        logger.error(error_msg)
                        return "I'm sorry, I encountered an issue processing your request. Please try again."

                    assistant_message = response.choices[0].message
                    self.messages.append(assistant_message)

                    if not assistant_message.tool_calls:
                        logger.info(
                            "No tool calls needed, returning assistant response"
                        )
                        return (
                            assistant_message.content
                            or "I don't have a response for that."
                        )

                    tool_responses = []
                    for tool_call in assistant_message.tool_calls:
                        if not tool_call or not tool_call.function:
                            logger.warning("Skipping invalid tool call")
                            continue

                        tool_result = self.handle_tool_call(tool_call)

                        try:
                            tool_result_str = json.dumps(tool_result)
                            tool_responses.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": tool_call.function.name,
                                    "content": tool_result_str,
                                }
                            )
                        except (TypeError, ValueError) as e:
                            error_msg = f"Failed to serialize tool result: {str(e)}"
                            logger.error(f"{error_msg}. Result: {tool_result}")
                            tool_responses.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": tool_call.function.name,
                                    "content": json.dumps(
                                        {
                                            "error": "Failed to process tool result",
                                            "success": False,
                                        }
                                    ),
                                }
                            )

                    if tool_responses:
                        self.messages.extend(tool_responses)
                    else:
                        logger.warning("No valid tool responses to add to conversation")
                        return "I encountered an issue processing your request. Please try again."

                except GroqError as e:
                    error_msg = f"Groq API error: {str(e)}"
                    logger.error(error_msg)
                    return "I'm having trouble connecting to the AI service. Please try again later."

                except json.JSONDecodeError as e:
                    error_msg = f"JSON decode error: {str(e)}"
                    logger.error(error_msg)
                    return "I encountered an error processing the response. Please try again."

                except Exception as e:
                    error_msg = (
                        f"Unexpected error in process_message iteration: {str(e)}"
                    )
                    logger.error(error_msg, exc_info=True)
                    return "I encountered an unexpected error. Please try again."

            return (
                assistant_message.content
                or "I'm having trouble processing your request. Please try again with more specific details."
            )

        except GroqError as e:
            error_msg = f"Groq API error: {str(e)}"
            logger.error(error_msg)
            return "I'm having trouble connecting to the AI service. Please try again later."

        except Exception as e:
            error_msg = f"Unexpected error in process_message: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return "I encountered an unexpected error. Please try again."


def main():
    """Main entry point for the AI Task Manager."""
    print("AI Task Manager - Type 'exit' to quit\n")

    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment variables.")
        return

    agent = TaskManagerAgent()

    try:
        while True:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            if not user_input:
                continue

            try:
                response = agent.process_message(user_input)
                print(f"\nAssistant: {response}")

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                print("\nSorry, I encountered an error. Please try again.")

    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print("\nAn unexpected error occurred. Please check the logs.")


if __name__ == "__main__":
    main()
