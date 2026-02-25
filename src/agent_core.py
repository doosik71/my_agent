import os
from google import genai
from google.genai import types  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from src.tools.tool_definitions import tools


# Load environment variables from .env file
load_dotenv()


class MyAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        # Configure the Gemini API
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. Please set it in a .env file.")

        self.client = genai.Client(api_key=google_api_key)
        self.model_name = model_name
        self.config = self._create_config()

    @staticmethod
    def _generate_tool_instructions(tools_list: list) -> str:
        """Generates a formatted string of tool descriptions for the SYSTEM_INSTRUCTION."""
        instructions = "\nAVAILABLE TOOLS AND WHEN TO USE THEM:\n"
        for tool_func in tools_list:
            tool_name = tool_func.__name__
            tool_doc = tool_func.__doc__
            if tool_doc:
                doc_lines = [line.strip()
                             for line in tool_doc.splitlines() if line.strip()]
                formatted_doc = doc_lines[0]
                if len(doc_lines) > 1:
                    formatted_doc += "\n  " + "\n  ".join(doc_lines[1:])
            else:
                formatted_doc = "No description available."
            instructions += f"- **{tool_name}**: {formatted_doc}\n"
        return instructions

    def _create_config(self) -> types.GenerateContentConfig:
        tool_instructions = self._generate_tool_instructions(tools)

        system_instruction_template = """
You are 'my_agent', an autonomous AI assistant powered by Google Gemini.
Your primary goal is to help the user by managing knowledge and performing tasks.

CORE RULES:
1. All files are automatically stored in a sandboxed 'docs/' directory. Do NOT include 'docs/' in the filepath when calling tools.
2. Use markdown (.md) for all documents you create.
3. Organize information logically using subdirectories if necessary (e.g., 'research/ai.md' will be saved as 'docs/research/ai.md').
4. ALWAYS consult and maintain 'index.md' to track the contents and structure of your knowledge base.
   - Before reading or writing any file in 'docs/', FIRST read 'index.md' to determine the best location or to find relevant files.
   - Whenever you create, modify, or delete a file in 'docs/', IMMEDIATELY update 'index.md' to reflect these changes. 'index.md' should contain a summary of each file's content or purpose.
5. BEFORE answering ANY question, ALWAYS FIRST check your 'docs/' knowledge base using 'read_doc' to find relevant information. Prioritize information found in your documents.
6. Specifically, if the user asks about their identity or personal preferences, ALWAYS check 'user_info.md' first (after consulting index.md).
{tool_instructions}
7. Always be concise and helpful.
"""
        system_instruction = system_instruction_template.format(
            tool_instructions=tool_instructions)

        return types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False)
        )

    def send_message(self, prompt: str, chat_session=None):
        """
        Sends a prompt to the Gemini agent and handles tool calls automatically.
        Returns the full GenerativeModel Response object.
        """

        if chat_session is None:
            chat_session = self.client.chats.create(
                model=self.model_name, config=self.config)

        try:
            response = chat_session.send_message(prompt)
            return response
        except Exception as e:
            # Returning a dummy object that has a 'text' attribute for compatibility
            class ErrorResponse:
                text = f"Error: {e}"
                parts = []
            return ErrorResponse()


if __name__ == "__main__":

    print("my_agent - Core Module (Sandboxed Document Management)")
    print("-" * 50)

    agent = MyAgent(model_name=os.getenv(
        "GEMINI_MODEL_NAME", "gemini-2.5-flash"))
    chat = agent.client.chats.create(
        model=agent.model_name, config=agent.config)

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        response = agent.send_message(user_input, chat_session=chat)

        if response.text:
            print(f"Agent: {response.text}")

        for model_turn in response.candidates[0].content.parts:
            if model_turn.call:
                call = model_turn.call
                print(f"[Tool Call] {call.name}({call.args})")
