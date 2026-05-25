import os
import re
from pypdf import PdfReader

# ==========================================
# 1. AI API Integration (Gemini & OpenAI)
# ==========================================

def get_llm_client():
    """
    Detects API keys in the environment and returns a client type and configured key/settings.
    Supports GEMINI_API_KEY and OPENAI_API_KEY.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            return "gemini", genai
        except ImportError:
            pass
            
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            return "openai", client
        except ImportError:
            pass
            
    return "fallback", None

def ask_llm(prompt, system_instruction=None):
    """
    Queries the detected LLM (Gemini or OpenAI) with fallback to None if no key is present.
    """
    client_type, client = get_llm_client()
    
    if client_type == "gemini":
        try:
            # Using new Gemini API structure
            model_name = "gemini-1.5-flash"
            generation_config = {
                "temperature": 0.4,
                "top_p": 0.95,
                "response_mime_type": "application/json" if "json" in prompt.lower() else "text/plain"
            }
            
            if system_instruction:
                model = client.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
            else:
                model = client.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config
                )
                
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return None
            
    elif client_type == "openai":
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            response_format = {"type": "json_object"} if "json" in prompt.lower() else None
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.4,
                response_format=response_format
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return None
            
    return None

# ==========================================
# 2. PDF Parsing Helper
# ==========================================

def extract_text_from_pdf(pdf_path):
    """
    Extracts text contents from a PDF file.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

# ==========================================
# 3. Rich Simulation Database & Search
# ==========================================

# Extensive predefined skill set for fallback keyword matching
ALL_KNOWN_SKILLS = [
    "Python", "Flask", "Django", "FastAPI", "React", "Vue", "Angular", "HTML", "CSS", "JavaScript", 
    "TypeScript", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", 
    "Azure", "GCP", "Git", "GitHub", "CI/CD", "Machine Learning", "Data Science", "Pandas", "NumPy",
    "TensorFlow", "PyTorch", "Java", "Spring Boot", "C++", "C#", "Go", "Rust", "Node.js", "Express"
]

FALLBACK_QUESTIONS = {
    "Python Developer": [
        {
            "id": "py_1",
            "type": "Technical",
            "question": "What is the difference between a list and a tuple in Python, and when would you use each?",
            "key_terms": ["mutable", "immutable", "syntax", "memory", "performance", "hashable", "dictionary key"],
            "model_answer": "Lists are mutable, meaning their elements can be modified after creation. They are defined using square brackets `[]`. Tuples are immutable, meaning they cannot be changed after creation, and are defined using parentheses `()`. Because of immutability, tuples are more memory-efficient and faster. Additionally, tuples can be used as dictionary keys because they are hashable, whereas lists cannot.",
            "resources": [
                {"title": "Python Lists vs Tuples (Real Python)", "url": "https://realpython.com/python-lists-tuples/"},
                {"title": "W3Schools Python Tuples", "url": "https://www.w3schools.com/python/python_tuples.asp"}
            ]
        },
        {
            "id": "py_2",
            "type": "Technical",
            "question": "Explain how decorators work in Python and provide a common use case.",
            "key_terms": ["decorator", "wrapper", "function", "higher-order", "modify", "syntactic sugar", "@", "logging", "auth", "timing"],
            "model_answer": "A decorator is a higher-order function that takes another function as an argument, extends its behavior without explicitly modifying it, and returns a new function. They are represented by the `@decorator_name` syntax. Common use cases include logging, enforcing authentication, caching, rate limiting, and measuring execution time.",
            "resources": [
                {"title": "Primer on Python Decorators", "url": "https://realpython.com/primer-on-python-decorators/"},
                {"title": "Python Decorators (GeeksforGeeks)", "url": "https://www.geeksforgeeks.org/decorators-in-python/"}
            ]
        },
        {
            "id": "py_3",
            "type": "Scenario / Project",
            "question": "Describe a scenario where your Python application encountered a memory leak or a performance bottleneck. How did you diagnose and resolve it?",
            "key_terms": ["profiler", "memory", "leak", "gc", "bottleneck", "optimise", "database query", "indexing", "n+1", "caching"],
            "model_answer": "Performance bottlenecks often happen due to redundant database queries (N+1 query problem) or large in-memory data processing. Diagnosis can be done using profilers like `cProfile`, memory analyzers like `memory_profiler`, or APM tools. Solutions include optimizing SQL queries with proper joins/indexes, implementing redis caching, using generators (`yield`) instead of loading huge lists into memory, and avoiding circular imports or global state that prevent garbage collection.",
            "resources": [
                {"title": "Profiling Python Code", "url": "https://realpython.com/python-profiling/"},
                {"title": "Optimizing Python Code", "url": "https://wiki.python.org/moin/PythonSpeed/PerformanceTips"}
            ]
        },
        {
            "id": "py_4",
            "type": "HR / Behavioral",
            "question": "How do you handle disagreements with team members or senior developers regarding technical architectural choices?",
            "key_terms": ["communication", "collaboration", "pros and cons", "constructive", "listen", "compromise", "data-driven", "respectful"],
            "model_answer": "I approach technical disagreements objectively by focusing on data and project requirements rather than personal opinions. I schedule a brief discussion to actively listen to their perspective, list the pros and cons of both architectural approaches (scalability, maintenance, timeline, costs), and suggest a small prototype/benchmark if needed. If a decision is made that differs from my view, I commit fully to its success.",
            "resources": [
                {"title": "How to Handle Technical Disagreements", "url": "https://leaddev.com/agile-delivery/how-disagree-constructively-about-architecture"}
            ]
        }
    ],
    "React Developer": [
        {
            "id": "re_1",
            "type": "Technical",
            "question": "Explain the React Component Lifecycle in Functional Components using Hooks. How do you mimic componentDidMount and componentWillUnmount?",
            "key_terms": ["useEffect", "lifecycle", "dependency", "mount", "unmount", "cleanup", "functional"],
            "model_answer": "In functional components, useEffect handles lifecycle events. An empty dependency array `[]` runs the effect once after the initial render (mimicking `componentDidMount`). Returning a function inside `useEffect` acts as a cleanup mechanism, running right before the component unmounts (mimicking `componentWillUnmount`).",
            "resources": [
                {"title": "Using the Effect Hook", "url": "https://legacy.reactjs.org/docs/hooks-effect.html"}
            ]
        },
        {
            "id": "re_2",
            "type": "Technical",
            "question": "What is the Virtual DOM and how does React's diffing algorithm work?",
            "key_terms": ["virtual dom", "reconciliation", "diffing", "render", "keys", "performance", "batching"],
            "model_answer": "The Virtual DOM is a lightweight in-memory representation of the real DOM. When state changes, React creates a new virtual tree. The reconciliation (diffing) algorithm compares the new tree with the old one, calculates the minimum set of changes needed, and updates only those specific nodes in the real DOM, ensuring high performance.",
            "resources": [
                {"title": "Reconciliation in React", "url": "https://legacy.reactjs.org/docs/reconciliation.html"}
            ]
        },
        {
            "id": "re_3",
            "type": "Scenario / Project",
            "question": "How do you manage complex application state in React? Explain the trade-offs of Context API vs Redux/Zustand.",
            "key_terms": ["state management", "context api", "redux", "zustand", "prop drilling", "re-render", "boilerplate"],
            "model_answer": "For simple prop-drilling prevention, React's built-in Context API is excellent. However, Context trigger re-renders on all consumers when value changes, which is inefficient for high-frequency updates. Redux Toolkit or Zustand are preferred for complex, high-frequency, global states because they offer optimized selectors, structured actions, devtools, and bypass unnecessary re-renders.",
            "resources": [
                {"title": "React State Management Comparison", "url": "https://react.dev/learn/scaling-up-with-reducer-and-context"}
            ]
        },
        {
            "id": "re_4",
            "type": "HR / Behavioral",
            "question": "Tell me about a time you had to deliver a feature under a very tight deadline. How did you prioritize tasks?",
            "key_terms": ["prioritize", "mvp", "communication", "deadline", "agile", "scope", "quality"],
            "model_answer": "When facing a tight deadline, I align with stakeholders on a Minimum Viable Product (MVP) scope. I break the requirements down, identify critical-path technical blockers, and build the core functionality first. I keep code quality high by using tests and reviews, but cut nice-to-have features or complex animations, creating a backlog to tackle immediately after the critical release.",
            "resources": [
                {"title": "Task Prioritization in Tech", "url": "https://asana.com/resources/prioritize-tasks"}
            ]
        }
    ],
    "General Software Engineer": [
        {
            "id": "gen_1",
            "type": "Technical",
            "question": "What are the SOLID principles of Object-Oriented Design? Provide a brief explanation of each.",
            "key_terms": ["solid", "single responsibility", "open closed", "liskov substitution", "interface segregation", "dependency inversion"],
            "model_answer": "SOLID stands for: \n1. **Single Responsibility**: A class should have only one reason to change.\n2. **Open/Closed**: Software entities should be open for extension, but closed for modification.\n3. **Liskov Substitution**: Subtypes must be substitutable for their base types.\n4. **Interface Segregation**: Clients shouldn't be forced to depend on methods they don't use.\n5. **Dependency Inversion**: Depend on abstractions, not concretions.",
            "resources": [
                {"title": "SOLID Principles Explained", "url": "https://www.freecodecamp.org/news/solid-principles-explained-in-plain-english/"}
            ]
        },
        {
            "id": "gen_2",
            "type": "Technical",
            "question": "Explain the difference between SQL and NoSQL databases. When would you choose one over the other?",
            "key_terms": ["sql", "nosql", "relational", "schema", "scaling", "acid", "document", "joins"],
            "model_answer": "SQL databases are relational, schema-based, use SQL language, and scale vertically. They guarantee ACID compliance, making them perfect for financial systems and applications with complex relational queries. NoSQL databases are non-relational, schema-less (e.g., document, key-value, graph), and scale horizontally. They are ideal for unstructured data, high-throughput writes, and rapid development cycles.",
            "resources": [
                {"title": "SQL vs NoSQL Databases", "url": "https://www.mongodb.com/nosql-explained/nosql-vs-sql"}
            ]
        },
        {
            "id": "gen_3",
            "type": "Scenario / Project",
            "question": "How do you design an API to be highly secure and capable of handling high traffic spikes?",
            "key_terms": ["rate limiting", "caching", "load balancer", "auth", "jwt", "https", "horizontal scaling", "cdn"],
            "model_answer": "To secure an API, I implement HTTPS, JWT tokens with short expiry, role-based access control, input validation, and rate limiting (e.g., via API Gateways). To handle spikes, I use load balancers, horizontally scale the servers, cache static or read-heavy endpoints with Redis or a CDN, and implement asynchronous queuing (RabbitMQ/Kafka) for heavy write tasks.",
            "resources": [
                {"title": "Designing High-Traffic APIs", "url": "https://rapidapi.com/blog/api-design-best-practices/"}
            ]
        },
        {
            "id": "gen_4",
            "type": "HR / Behavioral",
            "question": "Describe your process for debugging a complex, production-level issue that is hard to reproduce locally.",
            "key_terms": ["logs", "observability", "metrics", "production", "monitoring", "tracing", "reproduce"],
            "model_answer": "I start by analyzing production telemetry: checking error tracking (e.g., Sentry), log aggregators (e.g., ELK stack), and APM metrics to understand the exact timing and scope. I look for common variables (browser, input shape, tenant ID). Once I isolate the conditions, I write an automated test mimicking those variables to reproduce and fix it.",
            "resources": [
                {"title": "Debugging Production Outages", "url": "https://charity.wtf/2019/02/05/how-to-debug-production-systems/"}
            ]
        }
    ]
}

def get_fallback_questions(role, extracted_skills):
    """
    Returns an appropriate list of questions if no LLM key is configured.
    Leverages extracted skills to customize generic questions.
    """
    selected_role = "General Software Engineer"
    
    # Simple role routing
    if "python" in role.lower() or "flask" in role.lower() or "django" in role.lower() or "backend" in role.lower():
        selected_role = "Python Developer"
    elif "react" in role.lower() or "frontend" in role.lower() or "vue" in role.lower() or "javascript" in role.lower():
        selected_role = "React Developer"
        
    questions = FALLBACK_QUESTIONS[selected_role]
    
    # We can inject details based on the user's resume
    customized_questions = []
    for q in questions:
        q_copy = q.copy()
        # Customizations based on skills
        if q_copy["type"] == "Technical" and extracted_skills:
            # If we find a matching skill, we can mention it
            for skill in extracted_skills:
                if skill.lower() in q_copy["question"].lower():
                    break
        customized_questions.append(q_copy)
        
    return customized_questions

def evaluate_answer_simulated(question, user_answer):
    """
    Simulates grading a response by analyzing keyword matches, length, and structure.
    Returns feedback as a dictionary.
    """
    answer_text = user_answer.strip()
    
    # 1. Base check for ultra-short answers
    if len(answer_text) < 20:
        return {
            "score": 3,
            "confidence": "Low",
            "correctness": "Too brief to evaluate",
            "suggestions": "Your response is extremely short. To perform well in technical interviews, you must explain *how* concepts work, give structural details, and mention concrete real-world use cases or projects where you've used these technologies.",
            "suggested_answer": question.get("model_answer", "Please provide a comprehensive explanation."),
            "resources": question.get("resources", [])
        }
        
    # 2. Check keyword coverage
    key_terms = question.get("key_terms", [])
    matches = []
    for term in key_terms:
        # Simple word boundaries search
        if re.search(r'\b' + re.escape(term.lower()) + r'\b', answer_text.lower()):
            matches.append(term)
            
    coverage_ratio = len(matches) / len(key_terms) if key_terms else 0.5
    
    # Calculate score based on keyword coverage and length
    score = 4
    if len(answer_text) > 100:
        score += 1
    if len(answer_text) > 250:
        score += 1
        
    coverage_score = int(coverage_ratio * 4) # Up to 4 points
    score += coverage_score
    score = min(max(score, 1), 10)  # Clamp between 1 and 10
    
    # Determine confidence and feedback details
    if score >= 8:
        confidence = "High"
        correctness = "Accurate and comprehensive. You addressed all core conceptual elements."
        suggestions = "Excellent work! To take this answer from a 9 to a 10, include a highly specific code snippet or a precise performance benchmark from your personal experience. Your communication style is clear and developer-ready."
    elif score >= 6:
        confidence = "Medium"
        correctness = "Partially accurate but missing some technical specifics."
        missing_terms = [t for t in key_terms if t not in matches][:3]
        suggestions = f"Good foundational understanding. To strengthen this response, you should explicitly discuss the following concepts: {', '.join(missing_terms)}. Adding an example from a previous project where you applied this pattern would make your answer much more compelling."
    else:
        confidence = "Low-Medium"
        correctness = "Conceptually weak or off-topic. You missed crucial technical keywords."
        suggestions = f"You seem to have a general idea, but the answer lacks technical depth. Be sure to study: {', '.join(key_terms[:4])}. Try structuring your answer by defining the terms first, stating the 'why' (trade-offs), and wrapping up with a concrete architectural scenario."
        
    return {
        "score": score,
        "confidence": confidence,
        "correctness": correctness,
        "suggestions": suggestions,
        "suggested_answer": question.get("model_answer", "Please check study guides."),
        "resources": question.get("resources", [])
    }
