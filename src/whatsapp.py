import os
import sys
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Add the project root to sys.path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_script_dir, os.pardir)
sys.path.insert(0, os.path.abspath(project_root))

from src.agent_core import MyAgent

load_dotenv()

app = Flask(__name__)

# Initialize MyAgent globally for the Flask app
# In a real-world scenario, you might want to manage agent state per user/chat session.
agent = MyAgent(model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash"))
# TODO: Implement chat session management per WhatsApp user

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages from Twilio."""
    # Verify the webhook request if a token is set (optional, but good practice)
    # For Twilio, direct verification might be more complex, often relying on Twilio's own security features.
    # This example focuses on content.

    incoming_msg = request.values.get("Body", "").strip()
    sender_id = request.values.get("From", "")

    print(f"Received message from {sender_id}: {incoming_msg}")

    # Initialize a new chat session for each message for simplicity,
    # or retrieve/create a persistent session based on sender_id.
    # For now, we'll let agent.send_message create a new one if chat_session is None.
    # TODO: Manage chat sessions per sender_id for context retention.
    
    # Get response from MyAgent
    agent_response_obj = agent.send_message(incoming_msg, chat_session=None) # No persistent chat_session for now

    response_text = ""
    if hasattr(agent_response_obj, 'text') and agent_response_obj.text:
        response_text = agent_response_obj.text
    elif hasattr(agent_response_obj, 'candidates') and agent_response_obj.candidates:
        for part in agent_response_obj.candidates[0].content.parts:
            if part.text:
                response_text += part.text
            if part.function_call:
                # Optionally, log or inform the user about tool calls
                response_text += f"\n🛠️ Tool Call: {part.function_call.name}({part.function_call.args})"
    else:
        response_text = "Sorry, I couldn't process that. An unknown error occurred."

    # Send response back to WhatsApp via Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    # Ensure FLASK_APP and FLASK_ENV are set, or run with gunicorn/waitress in production
    # Example for development:
    # FLASK_APP=src/whatsapp.py FLASK_ENV=development flask run
    # Or for simple run:
    app.run(host="0.0.0.0", port=5000, debug=True)
