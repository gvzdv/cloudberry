document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const messageText = userInput.value.trim();
    if (messageText === '') return;

    clearChatWindow(); // Clear previous conversation

    appendMessage('user', messageText);
    userInput.value = '';
    scrollToBottom();

    // Display animated thinking indicator
    const typingMessage = appendMessage('bot', 'Thinking');
    let dotCount = 0;
    const typingInterval = setInterval(() => {
        dotCount = (dotCount + 1) % 4;
        typingMessage.innerText = 'Thinking' + '.'.repeat(dotCount);
    }, 500);

    // Send the user's message to the server
    fetch('/get_response', {
        method: 'POST',
        body: JSON.stringify({ message: messageText }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(typingInterval); // Stop the thinking animation
        typingMessage.innerText = data.response; // Replace with the actual response
        scrollToBottom();
    })
    .catch(error => {
        clearInterval(typingInterval);
        typingMessage.innerText = 'Error: Unable to get response.';
        console.error('Error:', error);
    });
}

function appendMessage(sender, message) {
    const chatWindow = document.getElementById('chat-window');
    const messageElem = document.createElement('div');
    messageElem.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
    messageElem.innerText = message;
    chatWindow.appendChild(messageElem);
    return messageElem; // Return the element for further manipulation
}

function clearChatWindow() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.innerHTML = ''; // Clear all previous messages
}

function scrollToBottom() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.scrollTop = chatWindow.scrollHeight;
}