const messages = document.querySelector("#messages");
const form = document.querySelector("#chatForm");
const input = document.querySelector("#messageInput");
const sendButton = document.querySelector("#sendButton");
const newChatButton = document.querySelector("#newChatButton");
const storageLabel = document.querySelector("#storageLabel");
const overlay = document.querySelector("#settingsOverlay");
const apiKeyInput = document.querySelector("#apiKeyInput");
const apiBase = "";

let sessionId = null;
let apiKey = apiKeyInput.value;

function escapeHtml(value) {
  const node = document.createElement("div");
  node.textContent = value;
  return node.innerHTML;
}

function messageMarkup(role, content, loading = false) {
  const isUser = role === "user";
  const body = loading
    ? '<span class="typing"><i></i><i></i><i></i></span>'
    : escapeHtml(content);
  return `
    <div class="message-row ${isUser ? "user" : "assistant"}">
      ${isUser ? "" : '<div class="message-avatar">N</div>'}
      <div class="message-content">
        <div class="message-name">${isUser ? "You" : "Noir AI"}</div>
        <div class="message-bubble">${body}</div>
      </div>
    </div>`;
}

function addMessage(role, content, loading = false) {
  const currentWelcome = document.querySelector("#welcomeState");
  if (currentWelcome) currentWelcome.remove();
  const wrapper = document.createElement("div");
  wrapper.innerHTML = messageMarkup(role, content, loading);
  const row = wrapper.firstElementChild;
  messages.appendChild(row);
  messages.scrollTo({ top: messages.scrollHeight, behavior: "smooth" });
  return row;
}

async function sendMessage(question) {
  const trimmed = question.trim();
  if (!trimmed || sendButton.disabled) return;

  addMessage("user", trimmed);
  input.value = "";
  resizeInput();
  sendButton.disabled = true;
  const pending = addMessage("assistant", "", true);

  try {
    const response = await fetch(`${apiBase}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
      body: JSON.stringify({ question: trimmed, session_id: sessionId }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "The request could not be completed.");
    sessionId = data.session_id;
    pending.querySelector(".message-bubble").textContent = data.answer;
  } catch (error) {
    pending.querySelector(".message-bubble").textContent = error.message;
    pending.querySelector(".message-bubble").style.color = "#e9a6b0";
    if (/key/i.test(error.message)) openSettings();
  } finally {
    sendButton.disabled = false;
    input.focus();
    messages.scrollTo({ top: messages.scrollHeight, behavior: "smooth" });
  }
}

function resizeInput() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 140)}px`;
}

function openSettings() {
  overlay.classList.add("open");
  overlay.setAttribute("aria-hidden", "false");
  setTimeout(() => apiKeyInput.focus(), 250);
}

function closeSettings() {
  overlay.classList.remove("open");
  overlay.setAttribute("aria-hidden", "true");
}

form.addEventListener("submit", event => { event.preventDefault(); sendMessage(input.value); });
input.addEventListener("input", resizeInput);
input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll("[data-prompt]").forEach(button => {
  button.addEventListener("click", () => sendMessage(button.dataset.prompt));
});

newChatButton.addEventListener("click", () => {
  sessionId = null;
  messages.innerHTML = `
    <div class="welcome-state" id="welcomeState">
      <div class="orb"><div class="orb-core"></div></div>
      <span class="eyebrow">Fresh canvas</span>
      <h3>Where should we begin?</h3>
      <p>Your previous conversation remains safely stored in Redis.</p>
    </div>`;
  input.focus();
});

document.querySelector("#settingsButton").addEventListener("click", openSettings);
document.querySelector("#closeSettingsButton").addEventListener("click", closeSettings);
document.querySelector("#closeSettingsArea").addEventListener("click", closeSettings);
document.querySelector("#saveSettingsButton").addEventListener("click", () => {
  apiKey = apiKeyInput.value.trim();
  closeSettings();
});
document.querySelector("#toggleKey").addEventListener("click", event => {
  const hidden = apiKeyInput.type === "password";
  apiKeyInput.type = hidden ? "text" : "password";
  event.currentTarget.textContent = hidden ? "Hide" : "Show";
});

document.querySelector("#docsLink").href = `${apiBase}/docs`;

fetch(`${apiBase}/ready`)
  .then(response => response.json())
  .then(data => { storageLabel.textContent = data.storage === "redis" ? "Redis secured" : "Local memory"; })
  .catch(() => { storageLabel.textContent = "Unavailable"; });
