#!/usr/bin/env python3
"""J3P Leadership Advisory Assistant — Flask web service for Railway."""
import os
from flask import Flask, request, jsonify, render_template, session
import anthropic
from system_prompt import SYSTEM_PROMPT

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
OPENING_MESSAGE = (
    "Hi, I'm the J3P Leadership Advisory Assistant. "
    "What leadership challenge are you working through?"
)


@app.route("/")
def index():
    # Start a fresh conversation each time the page loads
    session["messages"] = []
    return render_template("index.html", opening=OPENING_MESSAGE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()
    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    messages = session.get("messages", [])
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=messages,
        )
    except anthropic.APIError as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500

    assistant_text = next(
        (block.text for block in response.content if block.type == "text"), ""
    )

    messages.append({"role": "assistant", "content": assistant_text})
    session["messages"] = messages

    return jsonify({"reply": assistant_text})


@app.route("/reset", methods=["POST"])
def reset():
    session["messages"] = []
    return jsonify({"ok": True})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
