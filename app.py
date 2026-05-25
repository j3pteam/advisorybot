#!/usr/bin/env python3
"""J3P Leadership Advisory Assistant — Flask web service for Railway.

HTML is inlined to avoid template-loading issues on deploy.
"""
import os
from flask import Flask, request, jsonify, session, render_template_string
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

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>J3P Leadership Advisory Assistant</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 0;
      background: #f5f5f7;
      color: #1d1d1f;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: #1d1d1f;
      color: white;
      padding: 1rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    header h1 { margin: 0; font-size: 1.1rem; font-weight: 600; }
    header button {
      background: transparent;
      color: white;
      border: 1px solid #555;
      padding: 0.35rem 0.75rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
    }
    header button:hover { background: #333; }
    #chat {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem;
      max-width: 800px;
      margin: 0 auto;
      width: 100%;
    }
    .msg {
      margin-bottom: 1rem;
      padding: 0.85rem 1rem;
      border-radius: 12px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
    .user { background: #007aff; color: white; margin-left: 15%; }
    .assistant { background: white; border: 1px solid #e0e0e0; margin-right: 15%; }
    .typing { color: #888; font-style: italic; }
    form {
      display: flex;
      gap: 0.5rem;
      padding: 1rem;
      background: white;
      border-top: 1px solid #e0e0e0;
      max-width: 800px;
      margin: 0 auto;
      width: 100%;
    }
    input[type="text"] {
      flex: 1;
      padding: 0.75rem 1rem;
      border: 1px solid #d0d0d0;
      border-radius: 8px;
      font-size: 1rem;
      outline: none;
    }
    input[type="text"]:focus { border-color: #007aff; }
    button[type="submit"] {
      padding: 0.75rem 1.5rem;
      background: #007aff;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
      font-weight: 500;
    }
    button[type="submit"]:disabled { background: #999; cursor: not-allowed; }
  </style>
</head>
<body>
  <header>
    <h1>J3P Leadership Advisory Assistant</h1>
    <button id="reset-btn">New conversation</button>
  </header>
  <div id="chat">
    <div class="msg assistant">{{ opening }}</div>
  </div>
  <form id="chat-form">
    <input type="text" id="message" placeholder="Type your message..." autocomplete="off" autofocus required />
    <button type="submit" id="send-btn">Send</button>
  </form>

  <script>
    const chat = document.getElementById("chat");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("message");
    const sendBtn = document.getElementById("send-btn");
    const resetBtn = document.getElementById("reset-btn");
    const OPENING = {{ opening|tojson }};

    function addMessage(text, role) {
      const div = document.createElement("div");
      div.className = "msg " + role;
      div.textContent = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
      return div;
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      addMessage(text, "user");
      input.value = "";
      sendBtn.disabled = true;

      const thinking = addMessage("Thinking...", "assistant typing");

      try {
        const res = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        });
        const data = await res.json();
        thinking.remove();
        if (data.reply) {
          addMessage(data.reply, "assistant");
        } else {
          addMessage("Error: " + (data.error || "Unknown error"), "assistant");
        }
      } catch (err) {
        thinking.remove();
        addMessage("Network error: " + err.message, "assistant");
      } finally {
        sendBtn.disabled = false;
        input.focus();
      }
    });

    resetBtn.addEventListener("click", async () => {
      await fetch("/reset", { method: "POST" });
      chat.innerHTML = "";
      const div = document.createElement("div");
      div.className = "msg assistant";
      div.textContent = OPENING;
      chat.appendChild(div);
      input.focus();
    });
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    session["messages"] = []
    return render_template_string(INDEX_HTML, opening=OPENING_MESSAGE)


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
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

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
