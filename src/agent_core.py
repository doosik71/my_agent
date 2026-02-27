import os
import json
import inspect
from abc import ABC, abstractmethod
from google import genai
# pyright: ignore[reportMissingImports]
from google.genai import types as gemini_types
from openai import OpenAI
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from src.tools.tool_definitions import tools

# Load environment variables
load_dotenv()


def function_to_schema(func):
    """Converts a Python function to an OpenAI-style JSON schema."""
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func) or ""

    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for name, param in signature.parameters.items():
        # 기본적인 타입 매핑 (확장 가능)
        param_type = "string"
        if param.annotation == int:
            param_type = "integer"
        elif param.annotation == float:
            param_type = "number"
        elif param.annotation == bool:
            param_type = "boolean"
        elif param.annotation == list:
            param_type = "array"
        elif param.annotation == dict:
            param_type = "object"

        parameters["properties"][name] = {
            "type": param_type,
            "description": f"The {name} parameter."  # 실제 docstring에서 파싱하면 더 좋음
        }

        if param.default is inspect.Parameter.empty:
            parameters["required"].append(name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": docstring.split("\n")[0] if docstring else "No description",
            "parameters": parameters,
        }
    }


class AIResponse:
    """Unified response object to maintain compatibility with existing UI/Bot."""

    def __init__(self, text="", parts=None, candidates=None):
        self.text = text
        self.parts = parts or []
        self.candidates = candidates or []


class AICandidate:
    def __init__(self, content):
        self.content = content


class AIContent:
    def __init__(self, parts):
        self.parts = parts


class AIPart:
    def __init__(self, text=None, function_call=None):
        self.text = text
        self.function_call = function_call
        self.call = function_call  # Gemini compatibility


class AIFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args  # Gemini compatibility
        # OpenAI compatibility alias (though Gemini uses dict, OpenAI uses string)
        self.arguments = args


class BaseProvider(ABC):
    @abstractmethod
    def send_message(self, prompt, session=None):
        pass

    @abstractmethod
    def create_session(self):
        pass


class GeminiProvider(BaseProvider):
    def __init__(self, model_name):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.config = self._create_config()

    def _create_config(self):
        tool_instructions = MyAgent._generate_tool_instructions(tools)
        system_instruction = MyAgent.SYSTEM_INSTRUCTION_TEMPLATE.format(
            tool_instructions=tool_instructions
        )
        return gemini_types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
            automatic_function_calling=gemini_types.AutomaticFunctionCallingConfig(
                disable=False)
        )

    def create_session(self):
        return self.client.chats.create(model=self.model_name, config=self.config)

    def send_message(self, prompt, session=None):
        if session is None:
            session = self.create_session()

        response = session.send_message(prompt)
        # Ensure compatibility
        if hasattr(response, 'candidates') and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'call') and part.call:
                    part.function_call = part.call
        return response


class OllamaProvider(BaseProvider):
    def __init__(self, model_name):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        self.client = OpenAI(base_url=base_url, api_key="ollama")
        self.model_name = model_name
        self.tools_schema = [function_to_schema(t) for t in tools]
        self.tool_map = {t.__name__: t for t in tools}

    def create_session(self):
        tool_instructions = MyAgent._generate_tool_instructions(tools)
        system_msg = MyAgent.SYSTEM_INSTRUCTION_TEMPLATE.format(
            tool_instructions=tool_instructions
        )
        return [{"role": "system", "content": system_msg}]

    def send_message(self, prompt, session=None):
        if session is None:
            session = self.create_session()

        session.append({"role": "user", "content": prompt})

        all_parts = []
        max_iterations = 5
        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=session,
                tools=self.tools_schema,
                tool_choice="auto"
            )

            message = response.choices[0].message
            session.append(message)

            if message.content:
                all_parts.append(AIPart(text=message.content))

            if not message.tool_calls:
                # No more tool calls, return final response
                candidate = AICandidate(AIContent(all_parts))
                return AIResponse(text=message.content or "", parts=all_parts, candidates=[candidate])

            # Execute tool calls
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args_str = tool_call.function.arguments
                func_args = json.loads(func_args_str)

                # Add to parts for UI visibility
                all_parts.append(
                    AIPart(function_call=AIFunctionCall(func_name, func_args)))

                if func_name in self.tool_map:
                    try:
                        result = self.tool_map[func_name](**func_args)
                    except Exception as e:
                        result = f"Error executing {func_name}: {e}"

                    session.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": str(result)
                    })

        return AIResponse(text="Error: Maximum tool call iterations reached.")


class MyAgent:
    SYSTEM_INSTRUCTION_TEMPLATE = """
You are 'my_agent', an autonomous AI assistant.
Your primary goal is to help the user by managing knowledge and performing tasks.

CORE RULES:
1. **Storage:** All files are automatically stored in a sandboxed directory.
2. **Formatting:** Use Markdown (.md) for all documents you create.
3. **Organization:** Organize information logically, utilizing subdirectories when necessary to maintain order.
4. **Index Management:** Always maintain 'index.md' as the master log of your knowledge base.
   - BEFORE reading or writing any file, read 'index.md' to determine the correct path or locate relevant data.
   - IMMEDIATELY update 'index.md' after creating, modifying, or deleting a file. It must include a brief summary of each file's purpose or content.
   - When updating 'index.md', include relevant keywords or tags for each file to facilitate faster retrieval.
5. **Knowledge Retrieval:** BEFORE answering any question, use the 'read_doc' and 'list_docs' tool to search your working directory for relevant information. Prioritize data found in your stored documents over general knowledge.
6. **Personalization & Memory:** If the user asks about their identity or personal preferences, you MUST check '/user_info.md' first. Use this file to store and update long-term memory about the user.
7. **Requirement Priority:** Upon receiving any user request, your first action must be to check for '/rules.md' or 'rules.md'. Follow these instructions as the highest priority for task execution.
8. **Communication:** Always be concise, professional, and helpful in your responses.

{tool_instructions}

9. Always be kind and helpful.
"""

    def __init__(self):
        provider_type = os.getenv("AI_PROVIDER", "gemini").lower()

        if provider_type == "gemini":
            self.model_name = os.getenv(
                "GEMINI_MODEL_NAME", "gemini-2.5-flash")
            self.provider = GeminiProvider(self.model_name)
        elif provider_type == "ollama":
            self.model_name = os.getenv(
                "OLLAMA_MODEL_NAME", "gpt-oss")
            self.provider = OllamaProvider(self.model_name)
        else:
            raise ValueError(f"Unknown AI_PROVIDER: {provider_type}")

        print(f'Runnging {provider_type} with {self.model_name}')

        # Keep client for backward compatibility in web_ui/telegram_bot if they access it directly
        if hasattr(self.provider, 'client'):
            self.client = self.provider.client

        # Config attribute for Gemini compatibility
        if hasattr(self.provider, 'config'):
            self.config = self.provider.config
        else:
            self.config = None

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

    def send_message(self, prompt: str, chat_session=None):
        return self.provider.send_message(prompt, session=chat_session)

    def create_session(self):
        """Creates a new chat session using the current provider."""
        return self.provider.create_session()


if __name__ == "__main__":

    print(
        f"my_agent - Core Module (Provider: {os.getenv('AI_PROVIDER', 'gemini')})")
    print("-" * 50)

    agent = MyAgent()
    chat = agent.provider.create_session()

    try:
        while True:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            response = agent.send_message(user_input, chat_session=chat)

            if hasattr(response, 'text') and response.text:
                print(f"Agent: {response.text}")

            # Gemini-style candidate/part inspection (wrapped in OllamaProvider for compatibility)
            if hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        call = part.function_call
                        print(
                            f"[Tool Call] {call.name}({getattr(call, 'arguments', getattr(call, 'args', ''))})")
    except KeyboardInterrupt:
        print("\nExiting my_agent...")
