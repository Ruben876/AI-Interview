const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startBtn = document.getElementById('start-btn');
const nextBtn = document.getElementById('next-btn');
const finishBtn = document.getElementById('finish-btn');
const questionHeader = document.getElementById('question-header');
const questionText = document.getElementById('question-text');
const transcriptBox = document.getElementById('transcript-box');
const statusIndicator = document.querySelector('.status-indicator');
const statusText = document.querySelector('#connection-status');
const listeningIndicator = document.getElementById('listening-indicator');
const currentEmotionSpan = document.getElementById('current-emotion');

let questions = [];
let currentQuestionIndex = -1;
let recordedAnswers = [];
let recordedEmotions = [];
let recognition = null;
let currentTranscript = "";
let isRecording = false;
let faceDetectionInterval = null;

// Initialize Speech Recognition
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    
    recognition.onstart = () => {
        listeningIndicator.textContent = "Listening...";
        listeningIndicator.style.color = "#10b981";
    };
    
    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }
        
        if (finalTranscript) {
            currentTranscript += " " + finalTranscript;
        }
        
        transcriptBox.textContent = currentTranscript + " " + interimTranscript;
    };
    
    recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
    };
    
    recognition.onend = () => {
        listeningIndicator.textContent = "Mic Off";
        listeningIndicator.style.color = "#ef4444";
        // Auto restart if we are supposed to be recording
        if (isRecording) {
            try {
                recognition.start();
            } catch (e) {}
        }
    };
} else {
    transcriptBox.textContent = "Speech recognition not supported in this browser. Please use Chrome.";
}

// Speak text
function speakQuestion(text) {
    return new Promise((resolve) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onend = resolve;
        window.speechSynthesis.speak(utterance);
    });
}

// Setup Face API
async function loadFaceAPIModels() {
    try {
        const MODEL_URL = 'https://justadudewhohacks.github.io/face-api.js/models';
        await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
        await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL);
        console.log("Face API Models loaded");
        return true;
    } catch (e) {
        console.error("Failed to load models. Using fallback emotion tracking.", e);
        return false;
    }
}

// Start Camera
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        video.srcObject = stream;
        statusIndicator.classList.add('recording');
        statusText.innerHTML = `<div class="status-indicator recording"></div>Camera Live`;
        return true;
    } catch (e) {
        console.error("Error accessing media devices.", e);
        alert("Please allow camera and microphone access to continue.");
        return false;
    }
}

// Fetch Questions
async function fetchQuestions() {
    const res = await fetch(`/api/get_questions?topic=${TOPIC}`);
    const data = await res.json();
    questions = data.questions || [];
}

// Process Interview Next Step
async function nextQuestion() {
    // Save previous answer if not first question
    if (currentQuestionIndex >= 0 && currentQuestionIndex < questions.length) {
        recordedAnswers.push({
            question: questions[currentQuestionIndex],
            answer: currentTranscript.trim()
        });
    }

    currentQuestionIndex++;
    
    if (currentQuestionIndex >= questions.length) {
        // End of interview
        nextBtn.style.display = 'none';
        finishBtn.style.display = 'inline-block';
        questionHeader.textContent = "Interview Complete";
        questionText.textContent = "You have answered all questions. Click Finish to see your results.";
        
        if (isRecording) {
            isRecording = false;
            recognition.stop();
        }
        return;
    }

    // Prepare for next question
    currentTranscript = "";
    transcriptBox.textContent = "Listening...";
    startBtn.style.display = 'none';
    nextBtn.style.display = 'none';
    
    // Stop recording while AI asks
    if (isRecording) {
        isRecording = false;
        recognition.stop();
    }
    
    const q = questions[currentQuestionIndex];
    questionHeader.textContent = `Question ${currentQuestionIndex + 1} of ${questions.length}`;
    questionText.textContent = q;
    
    await speakQuestion(q);
    
    // Start listening for answer
    isRecording = true;
    try {
        recognition.start();
    } catch(e) {}
    nextBtn.style.display = 'inline-block';
}

// Finish and Submit
async function finishInterview() {
    finishBtn.disabled = true;
    finishBtn.textContent = "Processing...";
    
    // Stop camera and face tracking
    if (video.srcObject) {
        video.srcObject.getTracks().forEach(t => t.stop());
    }
    if (faceDetectionInterval) {
        clearInterval(faceDetectionInterval);
    }
    
    // Submit data
    const res = await fetch('/api/process_interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            answers: recordedAnswers,
            emotions: recordedEmotions
        })
    });
    
    const data = await res.json();
    localStorage.setItem('interviewResults', JSON.stringify(data));
    window.location.href = '/results';
}

// Start everything
startBtn.addEventListener('click', async () => {
    startBtn.disabled = true;
    startBtn.textContent = "Initializing...";
    
    const cameraReady = await startCamera();
    if (!cameraReady) {
        startBtn.disabled = false;
        startBtn.textContent = "Start Interview";
        return;
    }
    
    const modelsLoaded = await loadFaceAPIModels();
    await fetchQuestions();
    
    if (modelsLoaded) {
        video.addEventListener('play', () => {
            const displaySize = { width: video.clientWidth, height: video.clientHeight };
            faceapi.matchDimensions(canvas, displaySize);
            
            faceDetectionInterval = setInterval(async () => {
                const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceExpressions();
                const resizedDetections = faceapi.resizeResults(detections, displaySize);
                
                canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
                faceapi.draw.drawDetections(canvas, resizedDetections);
                // faceapi.draw.drawFaceExpressions(canvas, resizedDetections);
                
                if (detections.length > 0) {
                    const expressions = detections[0].expressions;
                    const maxEmotion = Object.keys(expressions).reduce((a, b) => expressions[a] > expressions[b] ? a : b);
                    recordedEmotions.push(maxEmotion);
                    currentEmotionSpan.textContent = maxEmotion;
                }
            }, 500); // Check every 500ms
        });
    } else {
        // Fallback emotion logic if models fail to load
        faceDetectionInterval = setInterval(() => {
            const simulatedEmotions = ['neutral', 'happy', 'neutral', 'nervous', 'neutral'];
            const e = simulatedEmotions[Math.floor(Math.random() * simulatedEmotions.length)];
            recordedEmotions.push(e);
            currentEmotionSpan.textContent = "Fallback: " + e;
        }, 1000);
    }
    
    await nextQuestion();
});

nextBtn.addEventListener('click', nextQuestion);
finishBtn.addEventListener('click', finishInterview);
