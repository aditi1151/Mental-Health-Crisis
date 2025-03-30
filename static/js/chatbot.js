
let chatHistory = [];
let chatSessionId = null;

document.addEventListener('DOMContentLoaded', function() {
 
  const chatForm = document.getElementById('chat-form');
  if (chatForm) {
    chatForm.addEventListener('submit', sendMessage);
  }
  
  const endSessionBtn = document.getElementById('end-session-btn');
  if (endSessionBtn) {
    endSessionBtn.addEventListener('click', endChatSession);
  }
  
  const chatContainer = document.getElementById('chat-container');
  if (chatContainer) {
    chatSessionId = chatContainer.dataset.sessionId;
  }
  
  scrollChatToBottom();
});

/**
 * Send user message to chatbot
 * @param {Event} event - Form submission event
 */
function sendMessage(event) {
  event.preventDefault();
  
  const messageInput = document.getElementById('message-input');
  const userMessage = messageInput.value.trim();
  
  if (!userMessage) {
    return;
  }
  appendMessage(userMessage, true);
  
 
  messageInput.value = '';
  

  showTypingIndicator();
  

  const formData = new FormData();
  formData.append('message', userMessage);
  
  fetch('/chatbot/message', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    hideTypingIndicator();
    
    if (data.status === 'success') {
   
      appendMessage(data.response, false);
    } else {
    
      appendErrorMessage('Sorry, I encountered an error. Please try again.');
    }
  })
  .catch(error => {
    console.error('Error sending message:', error);
    hideTypingIndicator();
    appendErrorMessage('Sorry, I encountered an error connecting to the server. Please try again.');
  });
}


/**
 * Append a message to the chat
 * @param {string} message - The message text
 * @param {boolean} isUser - True if the message is from the user, false if from the bot
 */
function appendMessage(message, isUser) {
  const chatMessages = document.getElementById('chat-messages');
  
  const messageDiv = document.createElement('div');
  messageDiv.className = isUser ? 'chat-message user-message' : 'chat-message bot-message';
  
  const messageContent = document.createElement('div');
  messageContent.className = 'message-content';
  
  if (isUser) {
    messageDiv.classList.add('justify-content-end');
    messageContent.classList.add('bg-primary', 'text-white');
  } else {
    messageDiv.classList.add('justify-content-start');
    messageContent.classList.add('bg-light');
  }
  const formattedMessage = message.replace(/\n/g, '<br>');
  messageContent.innerHTML = formattedMessage;
  
  messageDiv.appendChild(messageContent);
  chatMessages.appendChild(messageDiv);
  
  chatHistory.push({
    message: message,
    isUser: isUser,
    timestamp: new Date()
  });
  
  scrollChatToBottom();
}


function showTypingIndicator() {
  const chatMessages = document.getElementById('chat-messages');
  
  let typingIndicator = document.getElementById('typing-indicator');
  
  if (!typingIndicator) {
    typingIndicator = document.createElement('div');
    typingIndicator.id = 'typing-indicator';
    typingIndicator.className = 'chat-message bot-message';
    
    const indicatorContent = document.createElement('div');
    indicatorContent.className = 'message-content bg-light typing-indicator';
    indicatorContent.innerHTML = '<span></span><span></span><span></span>';
    
    typingIndicator.appendChild(indicatorContent);
    chatMessages.appendChild(typingIndicator);
    
    scrollChatToBottom();
  }
}


function hideTypingIndicator() {
  const typingIndicator = document.getElementById('typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

/**
 * Append an error message to the chat
 * @param {string} errorText - The error message
 */
function appendErrorMessage(errorText) {
  const chatMessages = document.getElementById('chat-messages');
  
  const messageDiv = document.createElement('div');
  messageDiv.className = 'chat-message system-message';
  
  const messageContent = document.createElement('div');
  messageContent.className = 'message-content bg-danger text-white';
  messageContent.textContent = errorText;
  
  messageDiv.appendChild(messageContent);
  chatMessages.appendChild(messageDiv);
  
  scrollChatToBottom();
}

function scrollChatToBottom() {
  const chatMessages = document.getElementById('chat-messages');
  if (chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}


function endChatSession() {
  const endSessionBtn = document.getElementById('end-session-btn');
  
  if (endSessionBtn) {
    endSessionBtn.disabled = true;
    endSessionBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Ending...';
  }
  
  const formData = new FormData();
  if (chatSessionId) {
    formData.append('session_id', chatSessionId);
  }
  
  fetch('/chatbot/end-session', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {
   
      appendSystemMessage('Chat session ended. Your recommendations have been updated.');
      
      const messageInput = document.getElementById('message-input');
      const sendButton = document.getElementById('send-button');
      
      if (messageInput && sendButton) {
        messageInput.disabled = true;
        sendButton.disabled = true;
      }
      
      if (endSessionBtn) {
        endSessionBtn.disabled = false;
        endSessionBtn.textContent = 'Start New Chat';
        endSessionBtn.onclick = function() {
          window.location.reload();
        };
      }
    } else {
      if (endSessionBtn) {
        endSessionBtn.disabled = false;
        endSessionBtn.textContent = 'End Chat';
      }
      
      
      appendErrorMessage('Failed to end chat session. Please try again.');
    }
  })
  .catch(error => {
    console.error('Error ending chat session:', error);
    

    if (endSessionBtn) {
      endSessionBtn.disabled = false;
      endSessionBtn.textContent = 'End Chat';
    }
    
    appendErrorMessage('Error connecting to server. Please try again.');
  });
}

/**
 * Append a system message to the chat
 * @param {string} message - The system message text
 */
function appendSystemMessage(message) {
  const chatMessages = document.getElementById('chat-messages');
  
  const messageDiv = document.createElement('div');
  messageDiv.className = 'chat-message system-message';
  
  const messageContent = document.createElement('div');
  messageContent.className = 'message-content bg-info text-white text-center';
  messageContent.textContent = message;
  
  messageDiv.appendChild(messageContent);
  chatMessages.appendChild(messageDiv);
  
  scrollChatToBottom();
}
