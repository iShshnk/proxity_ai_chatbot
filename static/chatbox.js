// Get elements
const startButton = document.getElementById("start-btn");
const sendButton = document.getElementById("send-button");
const userMsg = document.getElementById("user_msg");
const vidButton = document.getElementById("hidden-button")

document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('chat-form');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // prevent the form from reloading the page

        var formData = new FormData(this);
        
        // Disable form and button
        form.disabled = true;
        sendButton.disabled = true;

        // send a POST request to the server
        fetch('/chat', {  // update with your Flask route
            method: 'POST',
            body: formData
        })
        .then(function() {
            // refresh the chat container
            var chatContainer = document.getElementById('chat-container');
            
            fetch(location.href)
            .then(response => response.text())
            .then(html => {
                var parser = new DOMParser();
                var doc = parser.parseFromString(html, 'text/html');
                chatContainer.innerHTML = doc.getElementById('chat-container').innerHTML;
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                // Enable form and button after receiving the response
                form.disabled = false;
                sendButton.disabled = false;
            });

            // clear the textarea
            document.getElementById('user_msg').value = '';
            vidButton.click();
            
        })
        .catch(function(error) {
            console.error('Error:', error);

            // Enable form and button in case of error
            form.disabled = false;
            sendButton.disabled = false;
        });
    });
    
    var newConversationButton = document.getElementById('new-conversation-button');
    
    newConversationButton.addEventListener('click', function(event) {
        // send a POST request to the server
        fetch('/chat', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({new_conversation: true}),
        })
        .then(response => response.json())
        .then(data => {
            window.location.href = "/"; // reload the page
        })
        .catch((error) => {
            console.error('Error:', error);
        });
        window.location.href = "/login";
    });
});

// Wait for the entire HTML document to load
window.onload = function() {
    var objDiv = document.querySelector(".chat-card-body");
    objDiv.scrollTop = objDiv.scrollHeight;
}


window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.interimResults = true;

let silenceTimer;
let finalTranscript = '';
let isRecording = false;

const startTimer = () => {
    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => {
        if (userMsg.value !== '') {
            sendButton.click();
            finalTranscript = '';
        }
    }, 5000); 
};

recognition.addEventListener('result', e => {
    let interimTranscript = ' ';
    
    for (let i = e.resultIndex; i < e.results.length; i++) {
        const transcript = e.results[i][0].transcript;
    
        if (e.results[i].isFinal) {
            finalTranscript += transcript;
        } else {
            interimTranscript += transcript;
        }
    }
    
    userMsg.value = finalTranscript + interimTranscript;
    startTimer();
});

recognition.addEventListener('end', () => {
    if (isRecording) {
        recognition.start();
    }
});

userMsg.addEventListener('input', startTimer);

startButton.addEventListener('click', () => {
    if (isRecording) {
        recognition.stop();
        startButton.innerHTML = '<i class="fas fa-microphone"></i>'; // change button icon when stopped
    } else {
        recognition.start();
        finalTranscript = ''; // reset the finalTranscript when the startButton is clicked
        userMsg.value = '';
        startButton.innerHTML = '<i class="fas fa-microphone-slash"></i>'; // change button icon when recording
    }
    isRecording = !isRecording; // toggle recording state
});