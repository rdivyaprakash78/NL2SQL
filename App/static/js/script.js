const submit = document.getElementById("submitButton");
const chat = document.getElementById("inputText");

function putUserText(userText) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("chat-answer");

  const messageContent = document.createElement("p");
  messageContent.textContent = userText;

  messageDiv.appendChild(messageContent);

  const historyArea = document.getElementById("chatHistory");
  historyArea.appendChild(messageDiv);
  historyArea.scrollTop = historyArea.scrollHeight;
}

function putBotText(botText) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("bot-answer");
  messageDiv.id = "messageDiv";

  const messageContent = document.createElement("p");
  messageContent.textContent = botText;

  messageDiv.appendChild(messageContent);

  const historyArea = document.getElementById("chatHistory");
  historyArea.appendChild(messageDiv);
  historyArea.scrollTop = historyArea.scrollHeight;
}

function sendData(data) {
  fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: data }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        putBotText(data.error);
      } else {
        putBotText(data.message);
      }
      console.log("Response from backend:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

submit.addEventListener("click", (e) => {
  e.preventDefault();
  userText = chat.value;
  chat.value = "";
  chat.setAttribute("placeholder", "");
  putUserText(userText);
  sendData(userText);
});
