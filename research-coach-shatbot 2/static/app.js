const chat = document.getElementById("chat");
const form = document.getElementById("form");
const input = document.getElementById("input");
const statusEl = document.getElementById("status");

const btnHelp = document.getElementById("btnHelp");
const btnExplain = document.getElementById("btnExplain");

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `msg ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  row.appendChild(bubble);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
}

function updateStatus(state) {
  const topic = state.topic ? state.topic : "topic not set";
  const wc = state.word_count ? `, ${state.word_count} words` : "";
  statusEl.textContent = `Session: ${topic}${wc}`;
  btnExplain.textContent = `Explain: ${state.explain ? "On" : "Off"}`;
  btnExplain.setAttribute("aria-pressed", state.explain ? "true" : "false");
}

async function sendToServer(message) {
  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });

  if (!res.ok) throw new Error("Server error");

  return await res.json();
}

async function sendMessage(message) {
  addMessage("user", message);

  const data = await sendToServer(message);
  addMessage("bot", data.reply);
  updateStatus(data.state);
}

btnHelp.addEventListener("click", async () => {
  try {
    const data = await sendToServer("help");
    addMessage("meta", "Showing help");
    addMessage("bot", data.reply);
    updateStatus(data.state);
  } catch {
    addMessage("bot", "Could not reach server. Is Flask running?");
  }
});

btnExplain.addEventListener("click", async () => {
  try {
    const turningOn = btnExplain.getAttribute("aria-pressed") !== "true";
    const cmd = `explain mode: ${turningOn ? "on" : "off"}`;
    const data = await sendToServer(cmd);
    addMessage("meta", cmd);
    addMessage("bot", data.reply);
    updateStatus(data.state);
  } catch {
    addMessage("bot", "Could not reach server. Is Flask running?");
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = input.value.trim();
  if (!msg) return;

  input.value = "";

  try {
    await sendMessage(msg);
  } catch {
    addMessage("bot", "Could not reach server. Is Flask running?");
  }
});

// Starter message
addMessage("bot", "Hi — I’m Research Coach. Start with: set topic: <your topic> (or click Help).");
updateStatus({ topic: null, word_count: null, notes: [], explain: false });
