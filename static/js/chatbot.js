const chatBox = document.getElementById("chat-box");

// Display bot response
function addMessage(sender, message) {
  const messageDiv = document.createElement("div");
  messageDiv.textContent = `${sender}: ${message}`;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Fetch initial prompt
async function startChat() {
  try {
    const response = await fetch("http://127.0.0.1:5000/start");
    const data = await response.json();
    if (data.reply) {
      addMessage("Bot", data.reply);
    } else {
      addMessage("Bot", "Error starting chat.");
    }
  } catch (error) {
    addMessage("Bot", "Error connecting to the server.");
  }
}

// Send user message
document.getElementById("sendMessage").addEventListener("click", async () => {
  const userMessage = document.getElementById("userInput").value.trim();
  if (!userMessage) return;

  addMessage("User", userMessage);
  document.getElementById("userInput").value = "";

  try {
    const response = await fetch("http://127.0.0.1:5000/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage }),
    });
    const data = await response.json();
    if (data.reply) {
      addMessage("Bot", data.reply);
    } else {
      addMessage("Bot", "Error processing message.");
    }
  } catch (error) {
    addMessage("Bot", "Error connecting to the server.");
  }
});

// Finalize floorplan
document.getElementById("finalize").addEventListener("click", async () => {
  try {
    const response = await fetch("http://127.0.0.1:5000/finalize");
    const data = await response.json();
    if (data.instructions) {
      addMessage("Bot", "Finalized Floorplan:");
      addMessage("Bot", data.instructions);
    } else {
      addMessage("Bot", data.reply);
    }
  } catch (error) {
    addMessage("Bot", "Error connecting to the server.");
  }
});

// Start the chat
startChat();
