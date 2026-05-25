#!/usr/bin/env python3
"""J3P Leadership Advisory Assistant — Flask web service for Railway."""
import os
from flask import Flask, request, jsonify, session, render_template_string
import anthropic
from system_prompt import SYSTEM_PROMPT

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

client = anthropic.Anthropic()

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
  <title>J3P Health — Leadership Advisory Assistant</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --ink: #0B2545;
      --ink-soft: #13315C;
      --accent: #1B998B;
      --accent-soft: #E8F4F2;
      --paper: #FAF8F5;
      --paper-2: #FFFFFF;
      --line: #E6E2DA;
      --muted: #6B7280;
      --text: #1A1A1A;
      --shadow: 0 1px 2px rgba(11, 37, 69, 0.04), 0 8px 24px rgba(11, 37, 69, 0.06);
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--paper);
      color: var(--text);
      display: flex;
      flex-direction: column;
      font-size: 15px;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }
    header {
      background: var(--ink);
      color: var(--paper-2);
      padding: 1rem 1.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 3px solid var(--accent);
    }
    .brand { display: flex; align-items: center; gap: 0.85rem; }
    .brand-mark {
      width: 36px; height: 36px;
      border-radius: 50%;
      background: var(--accent);
      display: grid; place-items: center;
      font-family: 'Fraunces', serif;
      font-weight: 600;
      color: var(--paper-2);
      font-size: 1.05rem;
      letter-spacing: -0.02em;
    }
    .brand-text { display: flex; flex-direction: column; line-height: 1.1; }
    .brand-name {
      font-family: 'Fraunces', serif;
      font-weight: 500;
      font-size: 1.15rem;
      letter-spacing: 0.01em;
    }
    .brand-tag {
      font-size: 0.7rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: rgba(255,255,255,0.65);
      margin-top: 2px;
    }
    header button {
      background: transparent;
      color: var(--paper-2);
      border: 1px solid rgba(255,255,255,0.2);
      padding: 0.45rem 0.9rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.82rem;
      font-family: inherit;
      letter-spacing: 0.02em;
      transition: all 0.2s ease;
    }
    header button:hover {
      background: rgba(255,255,255,0.08);
      border-color: rgba(255,255,255,0.4);
    }
    #chat-wrap { flex: 1; overflow-y: auto; width: 100%; }
    #chat { max-width: 760px; margin: 0 auto; padding: 2rem 1.5rem 1rem; }
    .msg {
      margin-bottom: 1.25rem;
      padding: 1rem 1.15rem;
      border-radius: 10px;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-size: 0.95rem;
      animation: fadeIn 0.25s ease-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .user {
      background: var(--ink);
      color: var(--paper-2);
      margin-left: 18%;
      box-shadow: var(--shadow);
    }
    .assistant {
      background: var(--paper-2);
      border: 1px solid var(--line);
      margin-right: 12%;
      box-shadow: var(--shadow);
      position: relative;
    }
    .assistant::before {
      content: "";
      position: absolute;
      left: 0; top: 0; bottom: 0;
      width: 3px;
      background: var(--accent);
      border-radius: 10px 0 0 10px;
    }
    .typing { color: var(--muted); font-style: italic; }
    .composer-wrap { background: var(--paper-2); border-top: 1px solid var(--line); }
    form {
      display: flex;
      gap: 0.6rem;
      padding: 1rem 1.5rem;
      max-width: 760px;
      margin: 0 auto;
      width: 100%;
    }
    input[type="text"] {
      flex: 1;
      padding: 0.85rem 1.1rem;
      border: 1px solid var(--line);
      border-radius: 8px;
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
      background: var(--paper);
      color: var(--text);
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    input[type="text"]:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-soft);
    }
    button[type="submit"] {
      padding: 0.85rem 1.5rem;
      background: var(--ink);
      color: var(--paper-2);
      border: none;
      border-radius: 8px;
      font-size: 0.9rem;
      font-family: inherit;
      font-weight: 500;
      letter-spacing: 0.02em;
      cursor: pointer;
      transition: background 0.15s ease;
    }
    button[type="submit"]:hover:not(:disabled) { background: var(--ink-soft); }
    button[type="submit"]:disabled { background: var(--muted); cursor: not-allowed; }
    .footer-note {
      text-align: center;
      font-size: 0.72rem;
      color: var(--muted);
      padding: 0 1rem 0.85rem;
      letter-spacing: 0.04em;
    }
    @media (max-width: 640px) {
      .user { margin-left: 8%; }
      .assistant { margin-right: 6%; }
      header { padding: 0.85rem 1rem; }
      .brand-name { font-size: 1rem; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="brand-mark">J3P</div>
      <div class="brand-text">
        <span class="brand-name">J3P Health</span>
        <span class="brand-tag">Leadership Advisory</span>
      </div>
    </div>
    <button id="reset-btn">New conversation</button>
  </header>

  <div id="chat-wrap">
    <div id="chat">
      <div class="msg assistant">{{ opening }}</div>
    </div>
  </div>

  <div class="composer-wrap">
    <form id="chat-form">
      <input type="text" id="message" placeholder="Describe your leadership challenge..." autocomplete="off" autofocus required />
      <button type="submit" id="send-btn">Send</button>
    </form>
    <div class="footer-note">J3P Health · Confidential advisory conversation</div>
  </div>

  <script>
    const chat = document.getElementById("chat");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("message");
    const sendBtn = document.getElementById("send-btn");
    const resetBtn = document.getElementById("reset-btn");
    const chatWrap = document.getElementById("chat-wrap");
    const OPENING = {{ opening|tojson }};

    function addMessage(text, role) {
      const div = document.createElement("div");
      div.className = "msg " + role;
      div.textContent = text;
      chat.appendChild(div);
      chatWrap.scrollTop = chatWrap.scrollHeight;
      return div;
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      addMessage(text, "user");
      input.value = "";
      sendBtn.disabled = true;

      const thinking = addMessage("Thinking…", "assistant typing");

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
