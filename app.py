#!/usr/bin/env python3
"""J3P Leadership Advisory Assistant — Flask web service for Railway."""
import os
from flask import Flask, request, jsonify, session, render_template_string
import anthropic
from system_prompt import SYSTEM_PROMPT

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
OPENING_MESSAGE = "Hello, welcome to your session with Alan Friedman's bot."

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>J3P Health — Coach Alan Friedman</title>
  <link rel="icon" type="image/jpeg" href="/static/monogram.jpg" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    /* J3P Health brand palette */
    :root {
      --navy: #27334A;          /* PANTONE 2380 C — primary */
      --navy-2: #1d2738;         /* deeper navy for hovers */
      --blue: #5F8FB4;          /* PANTONE 7454 C — accent blue */
      --sand: #E7CEB5;          /* PANTONE 2309 C — soft sand */
      --gold: #D2BC8D;          /* PANTONE 467 C — gold accent */
      --rust: #9D432C;          /* PANTONE 7593 C — rare accent */
      --black: #202322;         /* PANTONE 419 C */
      --paper: #FAF6F0;         /* warm off-white derived from sand */
      --paper-2: #FFFFFF;
      --line: rgba(39, 51, 74, 0.12);
      --muted: #6B7280;
      --text: #27334A;
      --shadow: 0 1px 2px rgba(39, 51, 74, 0.05), 0 8px 28px rgba(39, 51, 74, 0.07);
    }

    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0;
      font-family: 'Jost', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--paper);
      color: var(--text);
      display: flex;
      flex-direction: column;
      font-size: 15px;
      line-height: 1.6;
      font-weight: 400;
      -webkit-font-smoothing: antialiased;
    }

    /* Header */
    header {
      background: var(--navy);
      color: var(--paper-2);
      padding: 1rem 1.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid var(--gold);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.9rem;
    }
    .brand-logo {
      width: 42px;
      height: 42px;
      border-radius: 4px;
      object-fit: contain;
      background: var(--navy);
    }
    .brand-text { display: flex; flex-direction: column; line-height: 1.1; }
    .brand-name {
      font-family: 'Jost', sans-serif;
      font-weight: 300;
      font-size: 1.25rem;
      letter-spacing: 0.04em;
      color: var(--gold);
    }
    .brand-tag {
      font-size: 0.68rem;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: rgba(231, 206, 181, 0.7);
      margin-top: 3px;
      font-weight: 400;
    }
    header button {
      background: transparent;
      color: var(--paper-2);
      border: 1px solid rgba(210, 188, 141, 0.35);
      padding: 0.5rem 1rem;
      border-radius: 2px;
      cursor: pointer;
      font-size: 0.75rem;
      font-family: inherit;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      font-weight: 400;
      transition: all 0.2s ease;
    }
    header button:hover {
      background: rgba(210, 188, 141, 0.08);
      border-color: var(--gold);
      color: var(--gold);
    }

    /* Chat area */
    #chat-wrap {
      flex: 1;
      overflow-y: auto;
      width: 100%;
    }
    #chat {
      max-width: 760px;
      margin: 0 auto;
      padding: 2.25rem 1.5rem 1rem;
    }
    .msg {
      margin-bottom: 1.25rem;
      padding: 1rem 1.2rem;
      border-radius: 4px;
      line-height: 1.65;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-size: 0.95rem;
      animation: fadeIn 0.3s ease-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .user {
      background: var(--navy);
      color: var(--paper);
      margin-left: 18%;
      box-shadow: var(--shadow);
    }
    .assistant {
      background: var(--paper-2);
      border: 1px solid var(--line);
      margin-right: 12%;
      box-shadow: var(--shadow);
      position: relative;
      color: var(--text);
    }
    .assistant::before {
      content: "";
      position: absolute;
      left: 0; top: 0; bottom: 0;
      width: 3px;
      background: var(--gold);
    }
    .typing { color: var(--muted); font-style: italic; }

    /* Composer */
    .composer-wrap {
      background: var(--paper-2);
      border-top: 1px solid var(--line);
    }
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
      border-radius: 2px;
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
      background: var(--paper);
      color: var(--text);
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    input[type="text"]:focus {
      border-color: var(--gold);
      box-shadow: 0 0 0 3px rgba(210, 188, 141, 0.18);
    }
    input[type="text"]::placeholder { color: rgba(39, 51, 74, 0.45); }
    button[type="submit"] {
      padding: 0.85rem 1.75rem;
      background: var(--navy);
      color: var(--gold);
      border: 1px solid var(--navy);
      border-radius: 2px;
      font-size: 0.78rem;
      font-family: inherit;
      font-weight: 400;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    button[type="submit"]:hover:not(:disabled) {
      background: var(--gold);
      color: var(--navy);
      border-color: var(--gold);
    }
    button[type="submit"]:disabled { opacity: 0.5; cursor: not-allowed; }

    .footer-note {
      text-align: center;
      font-size: 0.68rem;
      color: var(--muted);
      padding: 0 1rem 0.9rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      line-height: 1.7;
    }
    .footer-note a {
      color: var(--navy);
      text-decoration: none;
      border-bottom: 1px solid var(--gold);
      padding-bottom: 1px;
      transition: color 0.15s ease;
    }
    .footer-note a:hover { color: var(--rust); }

    @media (max-width: 640px) {
      .user { margin-left: 8%; }
      .assistant { margin-right: 6%; }
      header { padding: 0.85rem 1rem; }
      .brand-name { font-size: 1.1rem; }
      .brand-logo { width: 36px; height: 36px; }
      header button { padding: 0.4rem 0.7rem; font-size: 0.7rem; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="brand-text">
        <span class="brand-name">J3P Health</span>
        <span class="brand-tag">Coach Alan Friedman</span>
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
      <input type="text" id="message" placeholder="How can I help you?" autocomplete="off" autofocus required />
      <button type="submit" id="send-btn">Send</button>
    </form>
    <div class="footer-note">
      For informational purposes only. Not medical, legal, or financial advice.<br />
      To schedule time with Alan Friedman directly, please <a href="https://j3phealth.as.me/schedule/81cec0b7" target="_blank" rel="noopener">click here</a>.
    </div>
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
