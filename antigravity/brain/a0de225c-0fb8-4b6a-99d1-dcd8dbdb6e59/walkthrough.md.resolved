# AI Interview Analyzer - Walkthrough

I have successfully built the AI Interview Performance Analyzer according to your updated requirements (Python, HTML, NLP, Login Page). 

## 🏗️ Architecture & Tech Stack

1. **Backend (Python + Flask)**: 
   - Handles routing, authentication, and the core API (`/api/process_interview`).
   - Uses **TextBlob** (an NLP library) to perform sentiment analysis and assess the tone of the user's answers.
2. **Frontend (HTML + Vanilla CSS + JS)**:
   - Uses a premium, dynamic UI design with glassmorphism, modern gradients, and smooth hover effects.
   - **Login Page**: A secure entry point built with Python sessions.
3. **AI Capabilities**:
   - **Voice (STT / TTS)**: Uses the browser's native Web Speech API to read out questions and transcribe the user's spoken answers in real-time.
   - **Vision (Facial Expressions)**: Integrates `face-api.js` to analyze the video feed from the webcam locally, detecting emotions like happy, nervous, neutral, etc.

## 📂 Project Structure

The project has been created at `C:\Users\Guest User\.gemini\antigravity\scratch\ai-interview-analyzer`.

```text
ai-interview-analyzer/
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/style.css     # Premium UI styling
│   └── js/main.js        # Webcam, Speech, and Face API logic
└── templates/
    ├── login.html        # Login portal
    ├── index.html        # Topic selection dashboard
    ├── interview.html    # The actual interview interface
    └── results.html      # Final NLP feedback and score
```

## 🚀 How to Run the App

1. Open a terminal (PowerShell or Command Prompt).
2. Navigate to the project directory:
   ```powershell
   cd "C:\Users\Guest User\.gemini\antigravity\scratch\ai-interview-analyzer"
   ```
3. Install the required Python packages (including Flask and TextBlob for NLP):
   ```powershell
   pip install -r requirements.txt
   ```
4. Start the application:
   ```powershell
   python app.py
   ```
5. Open your web browser and go to: **http://127.0.0.1:5000**

## 💡 How to Use
- **Login**: Enter any username and password (for testing, any combination works to create an account).
- **Select Topic**: Choose between Python, JavaScript, or General HR.
- **Interview**: Allow camera and microphone permissions. Click "Start Interview". The AI will read the questions aloud, and the browser will transcribe your answers while analyzing your facial expressions.
- **Results**: After 5 questions, click "Finish" to see your NLP-generated feedback, sentiment score, and emotional analysis!
