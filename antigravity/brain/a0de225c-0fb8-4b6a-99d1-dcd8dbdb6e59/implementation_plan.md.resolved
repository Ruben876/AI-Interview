# AI Interview Performance Analyzer

Goal: Build a web application that conducts simulated AI interviews. The app will ask questions based on a user-selected topic, record the user's video and audio, analyze their facial expressions and speech, and finally provide detailed feedback on their performance.

## User Review Required
> [!IMPORTANT]
> **API Keys & AI Backend:** Real-time AI question generation and evaluation require an LLM API (like Google Gemini or OpenAI API). Additionally, accurate transcription might require a dedicated Speech-to-Text API if the built-in browser Web Speech API is not sufficient. 
> - **Question 1:** Do you have an API key (e.g., Gemini, OpenAI) you'd like to integrate, or should we start with simulated (mock) AI responses for testing the UI and flow?
> - **Question 2:** We will use client-side libraries (like `face-api.js`) for facial expression tracking to keep things fast and private. Is this acceptable?

## Proposed Changes

### 1. Project Setup
- Initialize a new Vite + React application.
- Setup a modern, dynamic, and premium UI design system using Vanilla CSS (vibrant colors, glassmorphism, animations) as per the guidelines.

### 2. Core Components
#### [NEW] `Home` Component
- Landing page to select the interview topic and start the session.

#### [NEW] `InterviewSession` Component
- Video/Audio capture using `MediaDevices.getUserMedia()`.
- Integration with Text-to-Speech (Web Speech API) for the AI to ask questions.
- Integration with Speech-to-Text to transcribe user answers.
- Integration with `face-api.js` for real-time facial expression tracking.

#### [NEW] `Results` Component
- Display overall score.
- Detailed feedback per question.
- Areas for improvement based on transcript and facial expressions.

### 3. Services
#### [NEW] `aiService.js`
- Handles logic for generating questions, evaluating answers, and summarizing feedback. (Will use mocks or API depending on user choice).

#### [NEW] `expressionAnalyzer.js`
- Wrapper for `face-api.js` to process video frames and extract dominant emotions (happy, nervous, neutral, etc.).

## Verification Plan

### Automated Tests
- Verify successful initialization of the camera and microphone.
- Test client-side routing between Home, Session, and Results pages.

### Manual Verification
- Start the app using `npm run dev`.
- Select a topic and begin an interview.
- Verify that the camera feed appears and permissions are handled gracefully.
- Answer questions and verify that speech is transcribed and face is tracked.
- Complete the interview and verify the results screen displays comprehensive feedback.
