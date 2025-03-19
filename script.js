const API_URL = "http://127.0.0.1:5000";

// Event Listeners
document.getElementById("startChat").addEventListener("click", function () {
    document.querySelector(".landing-page").style.display = "none";
    document.querySelector(".chatbot-container").style.display = "flex";
});

document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") sendMessage();
});

function sendMessage() {
    let userInput = document.getElementById("user-input").value.trim();
    let chatbox = document.getElementById("chatbox");

    if (userInput === "") return;

    // Display User Message (Right side)
    let userMessage = document.createElement("div");
    userMessage.classList.add("user-message");
    userMessage.textContent = `You: ${userInput}`;
    chatbox.appendChild(userMessage);
    chatbox.scrollTop = chatbox.scrollHeight;

    // Clear input box
    document.getElementById("user-input").value = "";

    // Add Typing Indicator
    let typingIndicator = document.createElement("div");
    typingIndicator.classList.add("bot-message", "typing");
    typingIndicator.textContent = "Bot is typing...";
    chatbox.appendChild(typingIndicator);
    chatbox.scrollTop = chatbox.scrollHeight;

    // Send to Backend
    fetch(`${API_URL}/chatbot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    })
        .then(response => response.json())
        .then(data => {
            chatbox.removeChild(typingIndicator);

            let botMessage = document.createElement("div");
            botMessage.classList.add("bot-message");
            chatbox.appendChild(botMessage);
            chatbox.scrollTop = chatbox.scrollHeight;

            // Apply Typing Effect with Structured Data
            typeStructuredResponse(botMessage, data.response);
        })
        .catch(error => {
            console.error("Error fetching response:", error);
        });
}

// Typing Effect for Bot Response with Structured Formatting
function typeStructuredResponse(element, text) {
    let lines = text.split("\n");
    let i = 0;
    let speed = 20;

    function type() {
        if (i < lines.length) {
            let line = document.createElement("p");

            // Format headings (bold)
            if (lines[i].startsWith("🏫") || lines[i].startsWith("📜") || lines[i].startsWith("🏷") ||
                lines[i].startsWith("📍") || lines[i].startsWith("📧") || lines[i].startsWith("📞") ||
                lines[i].startsWith("🏢")) {
                line.style.fontWeight = "bold";
            }

            line.textContent = lines[i];
            element.appendChild(line);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}