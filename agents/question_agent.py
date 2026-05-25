import json
from utils import ask_llm, get_fallback_questions

def generate_questions(role, resume_data):
    """
    Generates a set of structured interview questions based on the candidate's target role and resume profile.
    Uses LLM for real-time generation, with a high-fidelity local database as backup.
    """
    # 1. Check if LLM integration is available
    system_instruction = (
        "You are an expert interviewer and technical assessor. "
        "Your task is to generate custom interview questions for a candidate."
    )
    
    prompt = f"""
    You are interviewing a candidate for the role of '{role}'.
    Here is the analyzed resume data of the candidate:
    {json.dumps(resume_data, indent=2)}

    Generate exactly 4 customized, high-quality interview questions tailored to their profile:
    - 2 Technical Questions: Deep dive into the candidate's key skills (e.g. {", ".join(resume_data.get("skills", []))}) as they relate to '{role}'.
    - 1 Scenario / Project Question: Focus on one of the projects they listed in their resume (e.g. {", ".join([p.get("title", "") for p in resume_data.get("projects", [])])}), asking them how they built it or how they would solve a technical bottleneck in it.
    - 1 HR / Behavioral Question: Focus on their professional career, soft skills, or how they handle common team dilemmas, utilizing their strengths (e.g. {", ".join(resume_data.get("strengths", []))}).

    For each question, provide:
    1. "type": The question category ("Technical", "Scenario / Project", "HR / Behavioral").
    2. "question": The actual question text.
    3. "key_terms": A list of 5-8 crucial technical concepts/keywords that should ideally appear in a perfect response.
    4. "model_answer": A detailed, high-quality paragraph showing how a Senior Developer would answer this question.
    5. "resources": A list of 1-2 learning resources/links (must contain a "title" and a valid "url" starting with https://).

    Format requirements:
    Return your response STRICTLY as a raw JSON array of objects. Do not wrap it in markdown code blocks like ```json ... ```.
    Each object in the array must contain: "id", "type", "question", "key_terms", "model_answer", "resources".
    Use sequential IDs: "q_1", "q_2", "q_3", "q_4".
    """
    
    ai_response = ask_llm(prompt, system_instruction=system_instruction)
    
    if ai_response:
        try:
            cleaned_response = ai_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            questions = json.loads(cleaned_response)
            
            # Ensure it is a valid list of questions
            if isinstance(questions, list) and len(questions) > 0:
                # Add validation for keys
                for i, q in enumerate(questions):
                    if not q.get("id"):
                        q["id"] = f"ai_q_{i+1}"
                    if not all(k in q for k in ["type", "question", "key_terms", "model_answer", "resources"]):
                        raise ValueError("Missing essential keys in question object")
                return questions
        except Exception as e:
            print(f"Failed to generate/parse AI questions: {e}. Falling back to pre-coded library.")
            
    # 2. Offline Fallback Routing
    # Uses the advanced simulation engine built into utils
    skills = resume_data.get("skills", [])
    return get_fallback_questions(role, skills)
