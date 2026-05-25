import json
from utils import ask_llm, evaluate_answer_simulated

def evaluate_answer(question_obj, user_answer):
    """
    Evaluates the candidate's answer to a specific interview question.
    Grades correctness, checks confidence, suggests improvements, and links resources.
    """
    # Clean answer
    answer = user_answer.strip() if user_answer else ""
    
    # Base check for empty/short answers
    if not answer or len(answer) < 5:
        return {
            "score": 1,
            "confidence": "Low",
            "correctness": "No answer provided or answer is too short.",
            "suggestions": "Please write a comprehensive response. Aim for at least 3-4 descriptive sentences explaining your technical experience and architectural rationale.",
            "suggested_answer": question_obj.get("model_answer", "No model answer available."),
            "resources": question_obj.get("resources", [])
        }
        
    # 1. Try LLM evaluation first
    system_instruction = (
        "You are an elite technical interviewer and coding assessor. "
        "Your task is to grade candidate answers fairly, highlighting strengths and concrete improvement areas."
    )
    
    prompt = f"""
    Evaluate the candidate's response to the following interview question:
    
    Question Category: {question_obj.get("type", "General")}
    Question: {question_obj.get("question")}
    Expected Key Terms: {", ".join(question_obj.get("key_terms", []))}
    Model Answer: {question_obj.get("model_answer")}
    
    Candidate's Response:
    \"\"\"
    {answer}
    \"\"\"
    
    Analyze the candidate's answer and return a JSON object with the following keys:
    - "score": An integer from 1 to 10 grading the technical depth and accuracy.
    - "confidence": A string rating ("High", "Medium", "Low") based on the phrasing, detail, and directness of the answer.
    - "correctness": A brief 1-2 sentence technical assessment of what was correct or incorrect.
    - "suggestions": 2-3 specific, actionable recommendations on what technical concepts they should add, how to structure their communication, or what real-world examples to provide next time.
    - "suggested_answer": The provided model answer (or a slightly optimized version matching their specific details).
    - "resources": The resources provided in the question, or any customized study guides.

    JSON format requirements:
    Return your response STRICTLY as a raw JSON object. Do not wrap it in markdown code blocks like ```json ... ```.
    Ensure all fields exist in the JSON.
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
            
            evaluation = json.loads(cleaned_response)
            
            # Basic validation
            if all(k in evaluation for k in ["score", "confidence", "correctness", "suggestions"]):
                # Ensure score is an integer between 1 and 10
                evaluation["score"] = min(max(int(evaluation["score"]), 1), 10)
                # Keep original model answer and resources if missing in LLM response
                if "suggested_answer" not in evaluation:
                    evaluation["suggested_answer"] = question_obj.get("model_answer", "")
                if "resources" not in evaluation:
                    evaluation["resources"] = question_obj.get("resources", [])
                return evaluation
        except Exception as e:
            print(f"Failed to parse LLM evaluation: {e}. Using offline fallback evaluator.")
            
    # 2. Local Fallback Scorer (high-fidelity keyword matching engine)
    return evaluate_answer_simulated(question_obj, answer)
