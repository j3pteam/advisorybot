#!/usr/bin/env python3
"""J3P Leadership Advisory Assistant — Flask web service for Railway."""
import os
from flask import Flask, request, jsonify, session, render_template_string, send_from_directory
import anthropic
from system_prompt import SYSTEM_PROMPT

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
OPENING_MESSAGE = "Hello, welcome to your session with the J3P Advisor."

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>J3P Health — Coach Alan Friedman</title>
  <link rel="icon" type="image/jpeg" href="/monogram.jpg" />
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
      gap: 1rem;
    }
    .brand-logo {
      height: 60px;
      width: auto;
      display: block;
    }
    .brand-divider {
      width: 1px;
      height: 38px;
      background: rgba(210, 188, 141, 0.35);
    }
    .brand-tag {
      font-size: 0.92rem;
      letter-spacing: 0.22em;
      text-transform: uppercase;
      color: var(--gold);
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
    .feedback {
      display: flex;
      gap: 0.4rem;
      margin-top: 0.6rem;
      padding-top: 0.6rem;
      border-top: 1px solid var(--line);
      align-items: center;
    }
    .feedback-label {
      font-size: 0.7rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      margin-right: 0.3rem;
    }
    .feedback-btn {
      background: transparent;
      border: 1px solid var(--line);
      color: var(--muted);
      width: 30px;
      height: 30px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      transition: all 0.18s ease;
    }
    .feedback-btn svg { width: 14px; height: 14px; }
    .feedback-btn:hover {
      border-color: var(--gold);
      color: var(--navy);
      background: var(--paper);
    }
    .feedback-btn.selected-up {
      background: var(--navy);
      border-color: var(--navy);
      color: var(--gold);
    }
    .feedback-btn.selected-down {
      background: var(--rust);
      border-color: var(--rust);
      color: #fff;
    }
    .feedback-btn:disabled { cursor: default; }
    .feedback-thanks {
      font-size: 0.7rem;
      color: var(--muted);
      margin-left: 0.4rem;
      letter-spacing: 0.06em;
      font-style: italic;
    }

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
      padding: 0.85rem 3.2rem 0.85rem 1.1rem;
      border: 1px solid var(--line);
      border-radius: 2px;
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
      background: var(--paper);
      color: var(--text);
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      width: 100%;
    }
    input[type="text"]:focus {
      border-color: var(--gold);
      box-shadow: 0 0 0 3px rgba(210, 188, 141, 0.18);
    }
    input[type="text"]::placeholder { color: rgba(39, 51, 74, 0.45); }
    .input-wrap {
      flex: 1;
      position: relative;
      display: flex;
      align-items: center;
    }
    .mic-btn {
      position: absolute;
      right: 6px;
      top: 50%;
      transform: translateY(-50%);
      width: 38px;
      height: 38px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--navy);
      color: var(--gold);
      border: none;
      border-radius: 50%;
      cursor: pointer;
      padding: 0;
      transition: all 0.2s ease;
    }
    .mic-btn:hover { background: var(--gold); color: var(--navy); }
    .mic-btn svg { width: 18px; height: 18px; }
    .mic-btn.recording {
      background: var(--rust);
      color: #fff;
      animation: pulse 1.2s ease-in-out infinite;
    }
    .mic-btn.unsupported { display: none; }
    @keyframes pulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(157, 67, 44, 0.6); }
      50% { box-shadow: 0 0 0 8px rgba(157, 67, 44, 0); }
    }
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
      .brand-logo { height: 48px; }
      .brand-tag { font-size: 0.74rem; letter-spacing: 0.16em; }
      .brand { gap: 0.7rem; }
      .brand-divider { height: 30px; }
      header button { padding: 0.4rem 0.7rem; font-size: 0.7rem; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <img src="/full_logo.png" alt="J3P Health" class="brand-logo" />
      <span class="brand-divider"></span>
      <span class="brand-tag">J3P Advisor</span>
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
      <div class="input-wrap">
        <input type="text" id="message" placeholder="How can I help you?" autocomplete="off" autofocus required />
        <button type="button" id="mic-btn" class="mic-btn" aria-label="Voice input" title="Click to speak">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8" y1="23" x2="16" y2="23"/>
          </svg>
        </button>
      </div>
      <button type="submit" id="send-btn">Send</button>
    </form>
    <div class="footer-note">
      For informational purposes only. Not medical, legal, or financial advice.<br />
      To schedule time with a J3P Advisor, please <a href="https://j3phealth.as.me/schedule/81cec0b7" target="_blank" rel="noopener">click here</a>.
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

    function addMessage(text, role, withFeedback = false) {
      const div = document.createElement("div");
      div.className = "msg " + role;
      const textNode = document.createElement("div");
      textNode.textContent = text;
      div.appendChild(textNode);
      if (withFeedback) attachFeedback(div, text);
      chat.appendChild(div);
      chatWrap.scrollTop = chatWrap.scrollHeight;
      return div;
    }

    function attachFeedback(msgDiv, replyText) {
      const wrap = document.createElement("div");
      wrap.className = "feedback";
      wrap.innerHTML = `
        <span class="feedback-label">Helpful?</span>
        <button class="feedback-btn" data-rating="up" aria-label="Thumbs up" title="Yes, helpful">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H7v-12L11.69 2.5a2 2 0 0 1 3.31 3.38z"/>
          </svg>
        </button>
        <button class="feedback-btn" data-rating="down" aria-label="Thumbs down" title="No, not helpful">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H17v12l-4.69 7.5a2 2 0 0 1-3.31-3.38z"/>
          </svg>
        </button>
      `;
      const buttons = wrap.querySelectorAll(".feedback-btn");
      buttons.forEach(btn => {
        btn.addEventListener("click", async () => {
          if (btn.disabled) return;
          const rating = btn.dataset.rating;
          buttons.forEach(b => { b.disabled = true; });
          btn.classList.add(rating === "up" ? "selected-up" : "selected-down");
          const thanks = document.createElement("span");
          thanks.className = "feedback-thanks";
          thanks.textContent = "Thanks for the feedback";
          wrap.appendChild(thanks);
          try {
            await fetch("/feedback", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ rating, reply: replyText }),
            });
          } catch (err) {
            console.error("Feedback error:", err);
          }
        });
      });
      msgDiv.appendChild(wrap);
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
          addMessage(data.reply, "assistant", true);
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

    // --- Voice input via Web Speech API ---
    const micBtn = document.getElementById("mic-btn");
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      micBtn.classList.add("unsupported");
    } else {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      let isRecording = false;
      let baseText = "";

      micBtn.addEventListener("click", () => {
        if (isRecording) {
          recognition.stop();
        } else {
          baseText = input.value.trim();
          if (baseText) baseText += " ";
          try { recognition.start(); }
          catch (err) { console.error("Speech recognition error:", err); }
        }
      });

      recognition.addEventListener("start", () => {
        isRecording = true;
        micBtn.classList.add("recording");
        micBtn.setAttribute("title", "Click to stop");
      });

      recognition.addEventListener("end", () => {
        isRecording = false;
        micBtn.classList.remove("recording");
        micBtn.setAttribute("title", "Click to speak");
        input.focus();
      });

      recognition.addEventListener("result", (event) => {
        let transcript = "";
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        input.value = baseText + transcript;
      });

      recognition.addEventListener("error", (event) => {
        console.error("Speech error:", event.error);
        if (event.error === "not-allowed" || event.error === "service-not-allowed") {
          alert("Microphone access is blocked. Please allow microphone access in your browser settings.");
        }
        isRecording = false;
        micBtn.classList.remove("recording");
      });
    }
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


@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json(silent=True) or {}
    rating = data.get("rating")
    reply = (data.get("reply") or "")[:500]  # truncate to keep logs reasonable
    if rating not in ("up", "down"):
        return jsonify({"error": "Invalid rating"}), 400

    messages = session.get("messages", [])
    last_user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_msg = (m.get("content") or "")[:500]
            break

    # Log to stdout — Railway captures these in the deploy logs (searchable)
    app.logger.info(
        "FEEDBACK rating=%s user_msg=%r reply=%r",
        rating, last_user_msg, reply,
    )
    return jsonify({"ok": True})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/full_logo.png")
def serve_logo():
    return send_from_directory(".", "full_logo.png")


@app.route("/monogram.jpg")
def serve_monogram():
    return send_from_directory(".", "monogram.jpg")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
