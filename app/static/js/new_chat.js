/**
 * @param {string} conversationId - The ID of the conversation to connect to.
 * @param {function} onMessageCallback - Callback function to handle incoming messages from the backend.
 * @param {function} onErrorCallback - Callback function to handle WebSocket errors.
 * @param {function} onCloseCallback - Callback function to handle WebSocket closure.
 * @returns {object} An object with a `sendMessage` function to send messages to the backend and a `close` function to close the connection.
 */

class WebSocketChatClient {
    constructor(conversationId, onMessageCallback, onErrorCallback, onCloseCallback) {
        this.conversationId = conversationId;
        this.onMessageCallback = onMessageCallback;
        this.onErrorCallback = onErrorCallback;
        this.onCloseCallback = onCloseCallback;
        this.socket = null;
        this.connect();
    }

    connect() {
        const socketUrl = `ws://127.0.0.1:8000/chat/socket?conversation_id=${this.conversationId}`;
        this.socket = new WebSocket(socketUrl);

        this.socket.onopen = () => {
        };

        this.socket.onmessage = (event) => {
            let receivedData = event.data;
            try {
                const data = JSON.parse(receivedData);
                
                if (data.type === 'stream_end'){
                    receivedData = ''
                    this.stream_end()
                    
                } else{
                    this.onMessageCallback(data);
                }
            } catch (error) {
                this.onMessageCallback(receivedData);
            }

        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            if (this.onErrorCallback) {
                this.onErrorCallback(error);
            }
        };

        this.socket.onclose = (event) => {
            if (this.onCloseCallback) {
                this.onCloseCallback(event);
            }
        };
    }

    stream_end(){
        const markdownElements = document.querySelectorAll('#markdownContent');

        if (markdownElements.length > 0) {
            const lastMarkdownElement = markdownElements[markdownElements.length - 1];

            const markdown = lastMarkdownElement.textContent;
            const html = marked.parse(markdown);

            lastMarkdownElement.innerHTML = html;

        } else {
            console.log("No element with ID 'markdownContent' found.");
        }
    }

    /**
     * Sends a message to the WebSocket server.
     * @param {object|string} message - The message to send. If it's an object, it will be stringified to JSON.
     */
    sendMessage(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            try {
                if (typeof message === 'object') {
                    this.socket.send(JSON.stringify(message));
                } else {
                    this.socket.send(message);
                }
            } catch (error) {
                console.error("Error sending message:", error);
                if (this.onErrorCallback) {
                    this.onErrorCallback(new Error("Failed to send message via WebSocket."));
                }
            }
        } else {
            console.warn("WebSocket is not open. Message not sent:", message);
            if (this.onErrorCallback) {
                this.onErrorCallback(new Error("WebSocket not open. Message could not be sent."));
            }
        }
    }

    /**
     * Closes the WebSocket connection.
     */
    close() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

/**
 * Manages the chat user interface and interaction.
 */
class ChatUI {
    constructor(chatContainerId, textareaId) {
        this.chatContainer = document.getElementById(chatContainerId);
        this.textarea = document.getElementById(textareaId);

        if (!this.chatContainer) {
            console.error(`Error: Chat container element with ID '${chatContainerId}' not found.`);
            throw new Error(`Chat container element with ID '${chatContainerId}' not found.`);
        }
        if (!this.textarea) {
            console.error(`Error: Textarea element with ID '${textareaId}' not found.`);
            throw new Error(`Textarea element with ID '${textareaId}' not found.`);
        }
    }

    /**
     * Displays a response message in the chat container.
     * @param {string} data - The text content of the message.
     */
    displayResponse(data) {
        let lastChatBox = this.chatContainer.lastElementChild;
        let currentSystemChatBoxContent = null;

        if (lastChatBox && lastChatBox.classList.contains("system")) {
            currentSystemChatBoxContent = lastChatBox.querySelector(".content");
        }

        if (currentSystemChatBoxContent) {
            currentSystemChatBoxContent.textContent += data;
        } else {
            this.appendChatMessage({ author: 'system', content: data });
        }
        this.scrollToBottom();
    }

    /**
     * Appends a chat message to the display.
     * @param {object} message - The message object with `author` and `content`.
     */
    appendChatMessage(message) {
        const chatBox = document.createElement('div');
        const isUser = message.author === 'user';

        chatBox.className = `chat-box ${isUser ? 'user' : 'system'}`;

        const content = document.createElement('p');
        content.className = 'content';
        content.id = 'markdownContent'

        content.innerHTML = message.content.replace(/\n/g, '<br>');

        const time = document.createElement('span');
        time.textContent = this.formatTime(new Date());

        chatBox.appendChild(content);
        chatBox.appendChild(time);
        this.chatContainer.appendChild(chatBox);

        this.scrollToBottom();
    }

    /**
     * Clears all messages from the chat container.
     */
    clearChatContainer() {
        this.chatContainer.innerHTML = '';
    }

    /**
     * Scrolls the chat container to the bottom.
     */
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    /**
     * Gets the current value from the textarea and clears it.
     * @returns {string} The user's input text.
     */
    getUserMessage() {
        const message = this.textarea.value.trim();
        this.textarea.value = '';
        return message;
    }

    /**
     * Formats a Date object into a readable time string (e.g., "10:30 AM").
     * @param {Date} date - The date object to format.
     * @returns {string} The formatted time string.
     */
    formatTime(date) {
        let hours = date.getHours();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes} ${ampm}`;
    }
}

let chatClient;
let chatUI;

document.addEventListener("DOMContentLoaded", function() {
    try {
        chatUI = new ChatUI("chat-container", "textarea");
    } catch (error) {
        console.error("Failed to initialize Chat UI:", error.message);
        document.body.innerHTML = "<p>Error loading chat application. Please try again later.</p>";
        return;
    }
    new_chat()
});

function new_chat(){
    conversationId = generateID()

    chatClient = new WebSocketChatClient(
        conversationId,
        handleIncomingMessage,
        handleWebSocketError,
        handleWebSocketClose
    );

    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessageFromUI);
    }

    if (chatUI.textarea) {
        chatUI.textarea.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessageFromUI();
            }
        });
    }
}

function stream_end(){
    const markdown = document.getElementById('markdownContent').value;
    const html = marked.parse(markdown);
    console.log(html)
    document.getElementById('markdownContent').innerHTML = html;
}

function generateID(){
    const now = new Date();

  const year = now.getFullYear();
  const month = (now.getMonth() + 1).toString().padStart(2, '0');
  const day = now.getDate().toString().padStart(2, '0');
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = now.getSeconds().toString().padStart(2, '0');

  const dateTimeString = `${year}${month}${day}${hours}${minutes}${seconds}`;
  return parseInt(dateTimeString, 10);
}

/**
 * Handles incoming messages from the WebSocket.
 * @param {object|string} data - The received message data.
 */
function handleIncomingMessage(data) {
    if (typeof data === 'object') {
        if (data.type === "history") {
            chatUI.clearChatContainer();
            data.messages.forEach(message => {
                chatUI.appendChatMessage(message);
            });
        } else if (data.type === "new_session") {
            chatUI.clearChatContainer();
        } else {
            chatUI.displayResponse(JSON.stringify(data));
        }
    } else {
        chatUI.displayResponse(data);
    }
}

/**
 * Handles WebSocket errors.
 * @param {Event} error - The WebSocket error event.
 */
function handleWebSocketError(error) {
    chatUI.appendChatMessage({ author: 'system', content: "Connection error. Please try refreshing." });
}

/**
 * Handles WebSocket closure.
 * @param {CloseEvent} event - The WebSocket close event.
 */
function handleWebSocketClose(event) {
    let closeReason = "Connection lost.";
    if (event.wasClean) {
        closeReason = `Connection closed cleanly, code: ${event.code}, reason: ${event.reason}`;
    } else {
        closeReason = `Connection died unexpectedly, code: ${event.code}`;
    }
    chatUI.appendChatMessage({ author: 'system', content: `Chat session ended: ${closeReason}` });
}

/**
 * Sends a message from the UI (e.g., user input).
 */
function sendMessageFromUI() {
    const userText = chatUI.getUserMessage();
    if (userText) {
        chatUI.appendChatMessage({ author: 'user', content: userText });
        chatClient.sendMessage(userText);
    }
}