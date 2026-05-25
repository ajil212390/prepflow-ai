import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

# Import our agents
from agents import analyze_resume, generate_questions, evaluate_answer

app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = "interview-prep-secret-key-19485"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # Limit uploads to 10MB

# Ensure uploads directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ==========================================
# 1. Main Page Route
# ==========================================

@app.route("/")
def home():
    """
    Serves the primary Single Page Application.
    """
    return render_template("index.html")

# ==========================================
# 2. Resume Upload & Analysis Endpoint
# ==========================================

@app.route("/api/analyze-resume", methods=["POST"])
def api_analyze_resume():
    """
    Handles PDF resume uploads, processes them, and returns an extracted profile.
    """
    target_role = request.form.get("role", "Python Developer").strip()
    
    if "resume" not in request.files:
        return jsonify({"error": "No resume file was uploaded"}), 400
        
    file = request.files["resume"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
        
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported at this time"}), 400
        
    try:
        # Secure filename and save temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        # Analyze using Resume Agent
        profile = analyze_resume(filepath, target_role)
        
        # Clean up the file after analysis to save space
        try:
            os.remove(filepath)
        except Exception as err:
            print(f"Failed to remove temporary file {filepath}: {err}")
            
        return jsonify({
            "success": True,
            "role": target_role,
            "profile": profile
        })
        
    except Exception as e:
        print(f"Error in /api/analyze-resume: {e}")
        return jsonify({"error": f"An error occurred while parsing the resume: {str(e)}"}), 500

# ==========================================
# 3. Question Generation Endpoint
# ==========================================

@app.route("/api/generate-questions", methods=["POST"])
def api_generate_questions():
    """
    Generates a list of interview questions tailored to the candidate profile and role.
    """
    data = request.json or {}
    role = data.get("role", "Python Developer")
    profile = data.get("profile")
    
    if not profile:
        return jsonify({"error": "Profile data is required to generate tailored questions"}), 400
        
    try:
        questions = generate_questions(role, profile)
        return jsonify({
            "success": True,
            "questions": questions
        })
    except Exception as e:
        print(f"Error in /api/generate-questions: {e}")
        return jsonify({"error": f"An error occurred while generating questions: {str(e)}"}), 500

# ==========================================
# 4. Answer Submission & Feedback Endpoint
# ==========================================

@app.route("/api/submit-answer", methods=["POST"])
def api_submit_answer():
    """
    Grades a single question response and returns feedback, score, and recommendations.
    """
    data = request.json or {}
    question_obj = data.get("question")
    user_answer = data.get("answer")
    
    if not question_obj:
        return jsonify({"error": "Question context is required for evaluation"}), 400
        
    try:
        evaluation = evaluate_answer(question_obj, user_answer)
        return jsonify({
            "success": True,
            "evaluation": evaluation
        })
    except Exception as e:
        print(f"Error in /api/submit-answer: {e}")
        return jsonify({"error": f"An error occurred while evaluating the answer: {str(e)}"}), 500

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
