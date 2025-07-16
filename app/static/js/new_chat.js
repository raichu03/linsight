/**
 * @param {string} conversationId - The ID of the conversation to connect to.
 * @param {function} onMessage - Callback function to handle incoming messages from the backend.
 * It will receive a parsed JSON object for 'history' and 'new_session' types, and a string for text messages.
 * @param {function} onError - Callback function to handle WebSocket errors.
 * @param {function} onClose - Callback function to handle WebSocket closure.
 * @returns {object} An object with a `sendMessage` function to send messages to the backend and a `close` function to close the connection.
*/

let web_socket;

document.addEventListener("DOMContentLoaded", function(){
    web_socket = webSocketCommunication(1247)
});

function webSocketCommunication(conversationID){
    const socketUrl = `ws://127.0.0.1:8000/chat/socket?conversation_id=${conversationID}`
    const ws = new WebSocket(socketUrl);

    ws.onopen = () => {
        console.log("WebSocket connected.");
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === "history" || data.type === "new_session"){
                console.log(data);
                onMessage(data)
            } else {
                console.log(event.data)
            }
        } catch (e) {
            console.log(e)
        }
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        if (onError) {
            onError(error);
        }
    };

    ws.onclose = (event) => {
        console.log("WebSocket closed:", event);
        if (onClose) {
            onClose(event);
        }
    };

    return ws

}

function sendMessage(ws = web_socket, message){
    if (ws && ws.readyState === WebSocket.OPEN ){
        if (typeof message === 'object'){
            ws.send(JSON.stringify(message));
        } else{
            ws.send(message);
        }
        console.log("message sent:", message);
    }else {
        console.warn("WebSocket is not open. Message not sent:", message);
    }
}

// function getMessage()

function formatTime(date) {
    let hours = date.getHours();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes} ${ampm}`;
}

function createChatMessage(message) {
    const chatBox = document.createElement('div');
    const isUser = message.author === 'user';
    
    chatBox.className = `chat-box ${isUser ? 'user' : 'system'}`;
    
    const content = document.createElement('p');
    content.className = 'content';
    // Replace newlines with <br> tags for proper HTML rendering
    content.innerHTML = message.content.replace(/\n/g, '<br>');
    
    const time = document.createElement('span');
    time.textContent = formatTime(new Date());
    
    chatBox.appendChild(content);
    chatBox.appendChild(time);
    
    return chatBox;
}

function clearChatContainer(){
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer){
        chatContainer.innerHTML = ''
    } else{
        console.warn("Element with ID 'chat-container' not found" )
    }
}

function onMessage(data){
    const chatContainer = document.getElementById('chat-container');
    
    if (data.type === "history"){
        data.messages.forEach(message =>{
            chatContainer.appendChild(createChatMessage(message));
        });
    }
    else if (data.type === "new_session"){
        clearChatContainer()
    }
}