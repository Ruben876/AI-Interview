# How to Deploy Your AI Interview Analyzer to the Internet

If you want to share your application with the world (e.g., `www.your-ai-interviewer.com`), the easiest way to do this for a Python/Flask application is using a platform called **Render**.

### Step 1: Push your code to GitHub
1. Go to [GitHub](https://github.com/) and create a new repository.
2. Open your terminal in the project folder and run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
   git push -u origin main
   ```

### Step 2: Deploy on Render
1. Go to [Render](https://render.com/) and create a free account.
2. Click **New** -> **Web Service**.
3. Connect your GitHub account and select the repository you just created.
4. Fill out the deployment details:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` *(Note: you will need to add `gunicorn==21.2.0` to your `requirements.txt` file before pushing!)*
5. **Environment Variables**: Scroll down to the Advanced section and add all your keys from your local `.env` file:
   - `FLASK_SECRET_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GEMINI_API_KEY`

### Step 3: Important Google Cloud Update
Once Render gives you your public URL (e.g., `https://my-ai-app.onrender.com`), you **must** go back to the Google Cloud Console where you created your OAuth keys and add that new URL to your **Authorized redirect URIs**.
- Old: `http://127.0.0.1:5000/auth/callback`
- New: `https://my-ai-app.onrender.com/auth/callback`

Click "Deploy" on Render, and your app will be live to the world!
