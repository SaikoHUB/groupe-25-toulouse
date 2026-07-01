const messagesEl = document.querySelector("#messages");
const chatForm = document.querySelector("#chatForm");
const messageInput = document.querySelector("#messageInput");
const sendButton = document.querySelector("#sendButton");
const serverUrlInput = document.querySelector("#serverUrl");
const modelNameInput = document.querySelector("#modelName");
const connectionBadge = document.querySelector("#connectionBadge");
const checkConnectionButton = document.querySelector("#checkConnection");
const clearChatButton = document.querySelector("#clearChat");
const temperatureInput = document.querySelector("#temperature");
const temperatureValue = document.querySelector("#temperatureValue");
const maxTokensInput = document.querySelector("#maxTokens");
const serverHint = document.querySelector("#serverHint");
const newChatButton = document.querySelector("#newChat");
const deleteHistoryButton = document.querySelector("#deleteHistory");
const conversationList = document.querySelector("#conversationList");

const STORAGE_KEY = "techcorp-chat-conversations";
const welcomeMessage = "Bonjour. Posez une question finance, investissement, budget ou economie.";
const history = [];
let conversations = loadConversations();
let activeConversationId = conversations[0]?.id ?? createConversation().id;

function getServerUrl() {
  return serverUrlInput.value.trim().replace(/\/$/, "");
}

function setConnectionStatus(status, label) {
  connectionBadge.className = `status status-${status}`;
  connectionBadge.textContent = label;
}

function appendMessage(role, text, options = {}) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = role === "user" ? "VO" : "AI";

  const bubble = document.createElement("div");
  bubble.className = options.error ? "bubble error" : "bubble";

  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  bubble.append(paragraph);
  article.append(avatar, bubble);
  messagesEl.append(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  return paragraph;
}

function loadConversations() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(saved) ? saved : [];
  } catch (error) {
    return [];
  }
}

function saveConversations() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
}

function createConversation() {
  const conversation = {
    id: crypto.randomUUID(),
    title: "Nouvelle discussion",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    messages: [],
  };

  conversations.unshift(conversation);
  saveConversations();
  return conversation;
}

function getActiveConversation() {
  let conversation = conversations.find((item) => item.id === activeConversationId);

  if (!conversation) {
    conversation = createConversation();
    activeConversationId = conversation.id;
  }

  return conversation;
}

function getConversationTitle(messages) {
  const firstUserMessage = messages.find((message) => message.role === "user")?.content;
  if (!firstUserMessage) return "Nouvelle discussion";
  return firstUserMessage.length > 42 ? `${firstUserMessage.slice(0, 42)}...` : firstUserMessage;
}

function formatConversationDate(value) {
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function renderConversationList() {
  conversationList.innerHTML = "";

  const conversationsWithMessages = conversations.filter((conversation) => conversation.messages.length > 0);

  if (!conversationsWithMessages.length) {
    const empty = document.createElement("p");
    empty.className = "empty-history";
    empty.textContent = "Aucune discussion sauvegardee pour le moment.";
    conversationList.append(empty);
    return;
  }

  conversationsWithMessages.forEach((conversation) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = conversation.id === activeConversationId ? "conversation-item active" : "conversation-item";
    button.dataset.conversationId = conversation.id;

    const title = document.createElement("span");
    title.className = "conversation-title";
    title.textContent = conversation.title;

    const meta = document.createElement("span");
    meta.className = "conversation-meta";
    meta.textContent = `${conversation.messages.length} messages - ${formatConversationDate(conversation.updatedAt)}`;

    button.append(title, meta);
    conversationList.append(button);
  });
}

function renderActiveConversation() {
  messagesEl.innerHTML = "";
  history.length = 0;

  const conversation = getActiveConversation();
  if (!conversation.messages.length) {
    appendMessage("assistant", welcomeMessage);
  } else {
    conversation.messages.forEach((message) => {
      appendMessage(message.role, message.content);
      history.push({ role: message.role, content: message.content });
    });
  }

  renderConversationList();
}

function persistActiveConversation() {
  const conversation = getActiveConversation();
  conversation.messages = [...history];
  conversation.title = getConversationTitle(history);
  conversation.updatedAt = new Date().toISOString();

  conversations = [
    conversation,
    ...conversations.filter((item) => item.id !== conversation.id),
  ];

  saveConversations();
  renderConversationList();
}

function startNewConversation() {
  const emptyConversation = conversations.find((conversation) => conversation.messages.length === 0);
  const conversation = emptyConversation || createConversation();
  activeConversationId = conversation.id;
  renderActiveConversation();
  messageInput.focus();
}

function resizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 170)}px`;
}

async function checkConnection() {
  const serverUrl = getServerUrl();
  if (!serverUrl) {
    setConnectionStatus("offline", "URL manquante");
    return false;
  }

  setConnectionStatus("checking", "Verification");

  try {
    const response = await fetch(`${serverUrl}/api/tags`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const models = Array.isArray(data.models) ? data.models.map((model) => model.name) : [];
    const selectedModel = modelNameInput.value.trim();
    const modelFound = models.some((model) => model === selectedModel || model.startsWith(`${selectedModel}:`));

    setConnectionStatus("online", "Connecte");
    serverHint.textContent = modelFound
      ? `Serveur disponible avec ${selectedModel}.`
      : "Serveur disponible. Verifiez le nom du modele avec l'equipe INFRA.";
    return true;
  } catch (error) {
    setConnectionStatus("offline", "Deconnecte");
    serverHint.textContent = `Impossible de joindre ${serverUrl}.`;
    return false;
  }
}

async function readOllamaStream(response, targetParagraph) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let fullText = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) continue;
      const payload = JSON.parse(line);
      const chunk = payload.message?.content ?? payload.response ?? "";
      fullText += chunk;
      targetParagraph.textContent = fullText || "Generation en cours...";
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }
  }

  return fullText.trim();
}

async function sendMessage(userText) {
  const serverUrl = getServerUrl();
  const model = modelNameInput.value.trim() || "phi3.5";
  const temperature = Number.parseFloat(temperatureInput.value);
  const maxTokens = Number.parseInt(maxTokensInput.value, 10);

  appendMessage("user", userText);
  history.push({ role: "user", content: userText });
  persistActiveConversation();

  const assistantParagraph = appendMessage("assistant", "Generation en cours...");
  sendButton.disabled = true;
  messageInput.disabled = true;

  try {
    const response = await fetch(`${serverUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model,
        messages: [
          {
            role: "system",
            content:
              "Tu es l'assistant financier de TechCorp. Reponds clairement, structure tes conseils, et precise quand une information doit etre verifiee.",
          },
          ...history,
        ],
        stream: true,
        options: {
          temperature,
          num_predict: maxTokens,
          top_p: 0.9,
        },
      }),
    });

    if (!response.ok || !response.body) {
      throw new Error(`Erreur serveur HTTP ${response.status}`);
    }

    setConnectionStatus("online", "Connecte");
    const answer = await readOllamaStream(response, assistantParagraph);
    const finalAnswer = answer || "Le modele n'a pas renvoye de contenu.";
    assistantParagraph.textContent = finalAnswer;
    history.push({ role: "assistant", content: finalAnswer });
    persistActiveConversation();
  } catch (error) {
    const message = error instanceof Error ? error.message : "Erreur inconnue";
    assistantParagraph.parentElement.classList.add("error");
    assistantParagraph.textContent = `Reponse impossible : ${message}`;
    setConnectionStatus("offline", "Deconnecte");
  } finally {
    sendButton.disabled = false;
    messageInput.disabled = false;
    messageInput.focus();
  }
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const userText = messageInput.value.trim();
  if (!userText) return;

  messageInput.value = "";
  resizeTextarea();
  await sendMessage(userText);
});

messageInput.addEventListener("input", resizeTextarea);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

temperatureInput.addEventListener("input", () => {
  temperatureValue.textContent = temperatureInput.value;
});

checkConnectionButton.addEventListener("click", checkConnection);

clearChatButton.addEventListener("click", () => {
  history.length = 0;
  messagesEl.innerHTML = "";
  appendMessage("assistant", "Conversation effacee. Vous pouvez lancer un nouveau test.");
  const conversation = getActiveConversation();
  conversation.messages = [];
  conversation.title = "Nouvelle discussion";
  conversation.updatedAt = new Date().toISOString();
  saveConversations();
  renderConversationList();
});

newChatButton.addEventListener("click", startNewConversation);

deleteHistoryButton.addEventListener("click", () => {
  conversations = [];
  activeConversationId = createConversation().id;
  renderActiveConversation();
});

conversationList.addEventListener("click", (event) => {
  const item = event.target.closest("[data-conversation-id]");
  if (!item) return;

  activeConversationId = item.dataset.conversationId;
  renderActiveConversation();
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.prompt;
    resizeTextarea();
    messageInput.focus();
  });
});

renderActiveConversation();
checkConnection();
