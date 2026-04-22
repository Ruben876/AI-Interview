import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from textblob import TextBlob
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'super_secret_interview_key_fallback')

# Setup Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interview.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Setup OAuth
oauth = OAuth(app)
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

if google_client_id and google_client_id != 'your_google_client_id_here':
    oauth.register(
        name='google',
        client_id=google_client_id,
        client_secret=google_client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

# Setup Gemini AI
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key and gemini_api_key != 'your_gemini_api_key_here':
    genai.configure(api_key=gemini_api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
    except Exception:
        model = None
else:
    model = None

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    picture = db.Column(db.String(300))

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(50))
    score = db.Column(db.Integer)
    feedback_json = db.Column(db.Text)

with app.app_context():
    db.create_all()

# Fallback Question DB
QUESTIONS_DB = {
    'python': [
        "What are the built-in data types in Python?",
        "Explain the difference between a list and a tuple.",
        "What is a decorator in Python?",
        "How does Python handle memory management?",
        "What are generators and when would you use them?"
    ],
    'javascript': [
        "Explain the concept of closures in JavaScript.",
        "What is the event loop?",
        "How does prototypal inheritance work?",
        "What are the differences between var, let, and const?",
        "Explain promises and async/await."
    ],
    'general': [
        "Tell me about a time you faced a difficult challenge.",
        "Where do you see yourself in 5 years?",
        "Why do you want to work for our company?",
        "What are your greatest strengths and weaknesses?",
        "Describe a project you are particularly proud of."
    ]
}

@app.route('/')
def landing():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Local fallback login
        username = request.form.get('username')
        session['user'] = {'name': username, 'email': f"{username}@local.com", 'picture': None}
        return redirect(url_for('dashboard'))
    return render_template('login.html', google_enabled=bool(google_client_id and google_client_id != 'your_google_client_id_here'))

@app.route('/login/google')
def login_google():
    if not oauth.google:
        flash("Google Sign-In is not configured. Please set GOOGLE_CLIENT_ID in .env")
        return redirect(url_for('login'))
    redirect_uri = url_for('auth_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    
    if user_info:
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            user = User(email=user_info['email'], name=user_info['name'], picture=user_info.get('picture'))
            db.session.add(user)
            db.session.commit()
            
        session['user'] = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'picture': user.picture
        }
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/interview', methods=['GET'])
def interview():
    if 'user' not in session:
        return redirect(url_for('login'))
    topic = request.args.get('topic', 'general').lower()
    return render_template('interview.html', topic=topic)

@app.route('/api/get_questions', methods=['GET'])
def get_questions():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    topic = request.args.get('topic', 'general').lower()
    
    if model:
        try:
            prompt = f"Generate 5 professional interview questions for a {topic} role. Output ONLY a valid JSON array of strings."
            response = model.generate_content(prompt)
            # Cleanup potential markdown around json
            text = response.text.replace('```json', '').replace('```', '').strip()
            questions = json.loads(text)
            return jsonify({'questions': questions[:5]})
        except Exception as e:
            print(f"Gemini Error generating questions: {e}")
            # Fallback below
            
    if topic not in QUESTIONS_DB:
        topic = 'general'
    return jsonify({'questions': QUESTIONS_DB[topic][:5]})

@app.route('/api/process_interview', methods=['POST'])
def process_interview():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    answers = data.get('answers', [])
    emotions = data.get('emotions', [])
    
    dominant_emotion = "neutral"
    if emotions:
        emotion_counts = {}
        for e in emotions:
            emotion_counts[e] = emotion_counts.get(e, 0) + 1
        if emotion_counts:
            dominant_emotion = max(emotion_counts, key=emotion_counts.get)

    if model:
        try:
            prompt = "Act as an expert technical recruiter. Review these interview answers and the candidate's dominant facial expression. Provide a score out of 100, detailed feedback for each question, and an overall improvement tip.\n\n"
            prompt += f"Dominant Expression: {dominant_emotion}\n\n"
            for i, a in enumerate(answers):
                prompt += f"Q{i+1}: {a.get('question')}\nA{i+1}: {a.get('answer')}\n\n"
            prompt += """
            Respond EXACTLY with this JSON structure:
            {
                "score": integer,
                "improvement_tips": "string",
                "detailed_feedback": [
                    {"question": "string", "user_answer": "string", "feedback": "string"}
                ]
            }
            """
            response = model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            result = json.loads(text)
            result['dominant_emotion'] = dominant_emotion
            
            # Save to DB if real user
            if 'id' in session['user']:
                record = Interview(user_id=session['user']['id'], topic='Auto', score=result['score'], feedback_json=json.dumps(result))
                db.session.add(record)
                db.session.commit()
                
            return jsonify(result)
        except Exception as e:
            print(f"Gemini Error processing interview: {e}")
            # Fallback below
    
    # NLP Processing (Fallback Implementation)
    total_sentiment = 0
    feedback = []
    
    for i, answer_data in enumerate(answers):
        q = answer_data.get('question', '')
        a = answer_data.get('answer', '')
        
        blob = TextBlob(a)
        sentiment = blob.sentiment.polarity
        total_sentiment += sentiment
        
        if len(a.split()) < 5:
            q_feedback = "Your answer was very brief. Try to elaborate more next time."
        elif sentiment > 0.3:
            q_feedback = "Great positive tone and detail!"
        elif sentiment < -0.1:
            q_feedback = "Your tone seemed a bit negative or hesitant. Try to frame challenges more positively."
        else:
            q_feedback = "Good straightforward answer, but you could add more passion or specific examples."
            
        feedback.append({
            'question': q,
            'user_answer': a,
            'feedback': q_feedback
        })
        
    avg_sentiment = total_sentiment / len(answers) if answers else 0
    score = 60 + (avg_sentiment * 20)
    if dominant_emotion in ['happy', 'neutral']: score += 10
    elif dominant_emotion in ['nervous', 'fear', 'sad']: score -= 10
    score = max(0, min(100, score))
    
    overall_improvement = "Work on maintaining a confident posture and giving detailed, structured answers."
    if dominant_emotion in ['nervous', 'fear']:
        overall_improvement = "You appeared a bit nervous. Take deep breaths before answering."
        
    result = {
        'score': int(score),
        'dominant_emotion': dominant_emotion,
        'detailed_feedback': feedback,
        'improvement_tips': overall_improvement
    }
    
    # Save to DB if real user
    if 'id' in session['user']:
        record = Interview(user_id=session['user']['id'], topic='Fallback', score=result['score'], feedback_json=json.dumps(result))
        db.session.add(record)
        db.session.commit()
        
    return jsonify(result)

@app.route('/results', methods=['GET'])
def results():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('results.html')

if __name__ == '__main__':
    # When using OAuth callback locally over HTTP, we need to bypass HTTPS requirements:
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
