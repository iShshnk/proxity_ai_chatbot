// Wait for the entire HTML document to load
window.onload = function() {
    var objDiv = document.querySelector(".chat-card-body");
    objDiv.scrollTop = objDiv.scrollHeight;
}

// Get elements
const startButton = document.getElementById("start-btn");
const sendButton = document.getElementById("send-button");
const userMsg = document.getElementById("user_msg");


// Create a new SpeechRecognition object
window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.interimResults = true;

let silenceTimer;

const startTimer = () => {
    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => {
    if (userMsg.value !== '') {
        sendButton.click();
    }
    }, 2500); 
};

let finalTranscript = '';

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

recognition.addEventListener('end', recognition.start);

userMsg.addEventListener('input', startTimer);

startButton.addEventListener('click', () => {
    recognition.start();
    userMsg.value = '';
    startButton.disabled = true;
});