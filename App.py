import streamlit as st
import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import base64
import time
import json
import random
from playsound import playsound  # type: ignore # Add this import
import plotly.express as px  # Add this import
import pygame  # Add this import

# Initialize pygame mixer for sound playback
pygame.mixer.init()

import pygame

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model configurations
MODEL_CONFIG = {
    "deepseek-r1-distill-qwen-32b": {
        "temperature": 0.3,
        "max_retries": 5,
        "question_prefix": "SQL question:"
    },
    "gemma2-9b-it": {
        "temperature": 0.5,
        "max_retries": 4,
        "question_prefix": ""
    },
    "llama-3.3-70b-versatile": {
        "temperature": 0.4,
        "max_retries": 3,
        "question_prefix": ""
    }
}
# Define enhanced prompt templates with specified techniques
APTITUDE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert in generating aptitude and logical reasoning questions. Use this process to create unique and diverse questions:

    **Rules**:
    1. Generate questions only from verified mathematical or logical principles.
    2. Ensure there is a single correct answer for each question.
    3. Avoid subjective interpretations, ambiguous phrasing, or overly complex scenarios.
    4. Include a mix of quantitative and logical reasoning topics.
    5. Do not use a default topic; generate questions from various stages/topics such as:
       - Simple interest/Clocks/Calendars/Blood relations/Time and work/Speed and distance/Percentage/yllogisms/Arrangements (e.g., seating, order)/Logical deductions

    **Instructions**:
    - Focus on the given topic if provided. If no topic is specified, generate questions from different stages/topics listed above.
    - Use clear and concise language for each question.
    - Provide at least one example for clarity.

    **Few-Shot Examples**:

    ** Time and Work**
    Question: "A can complete a task in 10 days, and B can complete the same task in 15 days. How long will it take for both A and B to complete the task together?"
    Answer: 6 days (1 / (1/10 + 1/15) = 6)

    **Output Rules**:
    - Single question per output.
    - No markdown formatting.
    - Avoid using special characters like `**` at the start or end of questions.
    - Include at least one example for clarity.
    """),
])

CODING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert coder. Use the following Chain-of-Thought process to generate a coding problem:
    
    **Process:**
    1. **Understand the Skill**: Identify the core concept or skill ({skill}) the problem should focus on.
    2. **Define the Problem Context**: Create a real-world or abstract scenario where the skill is applied.
    3. **Break Down the Problem**:
       - Step 1: Clearly state the input(s) required for the problem.
       - Step 2: Specify the expected output(s) or goal.
       - Step 3: Outline any constraints or edge cases.
    4. **Provide Examples**: Include at least one example with inputs and outputs to clarify the problem.
    
    **Rules**:
    - Use clear and concise language.
    - Avoid ambiguous terms or overly complex scenarios.
    - Ensure the problem is solvable within a reasonable time frame.
    - Include a mix of basic and advanced concepts to challenge the candidate.
    
    **Example**:
    Skill: Arrays
    Problem Statement: "Given an array of integers, find the two numbers that add up to a specific target value."
    Input: An array of integers and a target value (e.g., [2, 7, 11, 15], target = 9).
    Output: Indices of the two numbers that sum to the target (e.g., [0, 1]).
    Constraints: You may assume there is exactly one solution, and you cannot use the same element twice.
    Example: 
      Input: [2, 7, 11, 15], target = 9
      Output: [0, 1]
    
    **Output Rules**:
    - Single problem per output.
    - No markdown formatting."""),
    ("human", """Generate a coding problem about {skill} with:""")
])

TECHNICAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a technical interviewer for {role} positions. Structure questions using this framework:

For {skill}, analyze through 5 lenses:
1. Core Theory: Fundamental principles, mathematical foundations, domain laws
2. System Dynamics: Interactions between components, failure cascades, feedback loops
3. Implementation Reality: Tradeoffs, debugging nightmares, "it works on my machine" gaps
4. Evolution: Historical solutions → current best practices → emerging alternatives
5. Paradoxes: Situations where standard patterns contradict (e.g., CAP theorem)

**Question Design Protocol**
1. Select 2 knowledge layers → Identify tension/conflict
2. Frame as concrete scenario requiring prioritization
3. Demand explanation of ripple effects

**Examples**

1. Skill: Database Engineering  
   Question: "When would you prioritize ACID compliance over horizontal scalability in a financial system? How does this choice impact disaster recovery strategies?"

**Output Rules**
1. Force candidate to choose between competing priorities
2. Require explanation of second-order consequences
3. Single question (<2 sentences)
4. Ends with '?'
5. No markdown"""),
    
    ("human", """Create a {skill} question using knowledge layers. {question_prefix}""")
])
BEHAVIORAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a behavioral expert. Use the following structured process to generate behavioral questions:
    
    **Process:**
    1. Start with the core skill ({skill}) and identify potential workplace challenges.
    2. Use Chain-of-Thought reasoning to break down the scenario into logical steps:
       - Step 1: Identify the challenge.
       - Step 2: Frame the challenge as a real-world experience.
       - Step 3: Tailor the question to the role ({role}).
    3. Use few-shot learning with diverse examples to guide the generation of questions.
    
    **Few-Shot Examples:**
    Example 1:
    Core Skill: Communication
    Role: Junior Developer
    Question: "Describe a time when you had to explain a technical concept to a non-technical team member. How did you ensure they understood?"
    
    
    **Rules:**
    - Avoid hypothetical scenarios ("Imagine...").
    - Use "Describe a time..." or "Tell me..." format.
    - Adapt the complexity and focus based on the role (e.g., junior vs. senior).
    - Ensure the question is concise (<2 sentences) and ends with '?'.
    
    **Output Rules:**
    - Single question per output.
    - No markdown formatting."""),
    ("human", """Create a behavioral question about {skill} for {role}.
    {question_prefix}""")
])


EVALUATION_PROMPT_TEMPLATE = """
Evaluate the interview answer using these STRICT criteria (1-4 scale):
1. Correctness: 
   - 4: Fully accurate with no technical errors, covers all aspects
   - 3: Mostly correct but missing minor details
   - 2: Partially correct with significant gaps
   - 0: Fundamentally incorrect
2. Depth: 
   - 4: Advanced concepts + examples + trade-offs + edge cases
   - 3: Good detail but missing some aspects
   - 2: Basic explanation only
   - 1: Superficial treatment
3. Relevance: 
   - 4: Directly addresses all parts of question
   - 3: Mostly relevant with minor tangents
   - 2: Partially relevant
   - 1: Off-topic
Checklist for Depth:
- [ ] Includes concrete examples/code snippets
- [ ] Discusses performance implications
- [ ] Mentions trade-offs/limitations
- [ ] Addresses edge cases
Question: {question}
Answer: {answer}
JSON Output Format:
{{
  "rubric": {{
    "correctness": {{"score": 1-4, "reason": "detailed technical evaluation"}},
    "depth": {{"score": 1-4, "reason": "depth analysis with checklist items"}},
    "relevance": {{"score": 1-4, "reason": "relevance check"}}
  }},
  "strengths": ["key strengths"],
  "suggestions": ["specific improvements based on checklist"],
  "total_score": "sum of all scores (3-12)"
}}
"""
EVALUATION_PROMPT = ChatPromptTemplate.from_template(EVALUATION_PROMPT_TEMPLATE)

# Add images and developer information to the sidebar
AI_path = "AI.png"  # Ensure this file is in the same directory as your script
try:
    st.sidebar.image(AI_path)
except FileNotFoundError:
    st.sidebar.warning("AI.png file not found. Please check the file path.")

image_path = "image.png"  # Ensure this file is in the same directory as your script
try:
    st.sidebar.image(image_path)
except FileNotFoundError:
    st.sidebar.warning("image.png file not found. Please check the file path.")

st.sidebar.markdown("👨👨‍💻 **Developer:** Abhishek 💖 Yadav")

developer_path = "pic.jpg"  # Ensure this file is in the same directory as your script
try:
    st.sidebar.image(developer_path)
except FileNotFoundError:
    st.sidebar.warning("pic.jpg file not found. Please check the file path.")

# Add a difficulty selector in the sidebar
difficulty = st.sidebar.selectbox(
    "Difficulty Level:",
    options=["Easy", "Medium", "Hard"],
    index=0
)

# Adjust the timer and question complexity based on the selected difficulty
difficulty_timer_map = {
    "Easy": 90,  # 90 seconds for Easy
    "Medium": 60,  # 60 seconds for Medium
    "Hard": 30  # 30 seconds for Hard
}
st.session_state["timer"] = difficulty_timer_map[difficulty]

# Adjust question generation logic based on difficulty
def generate_question(role, skill, model_name, existing_questions, stage, difficulty):
    config = MODEL_CONFIG.get(model_name, {})
    max_retries = config.get("max_retries", 3)
    prefix = config.get("question_prefix", "")

    # Adjust prompt or complexity based on difficulty
    if difficulty == "Easy":
        prefix += " (Focus on basic concepts)"
    elif difficulty == "Medium":
        prefix += " (Include moderate complexity)"
    elif difficulty == "Hard":
        prefix += " (Include edge cases and advanced scenarios)"

    for attempt in range(max_retries):
        try:
            model = ChatGroq(
                temperature=config.get("temperature", 0.5),
                groq_api_key=GROQ_API_KEY,
                model_name=model_name
            )
            # Define the prompt based on the selected stage
            if stage == "aptitude":
                prompt = APTITUDE_PROMPT
            elif stage == "coding":
                prompt = CODING_PROMPT
            elif stage == "technical":
                prompt = TECHNICAL_PROMPT
            elif stage == "behavioral":
                prompt = BEHAVIORAL_PROMPT
            else:
                raise ValueError("Invalid stage selected")

            chain = prompt | model
            
            existing_list = "\n".join([f"{i+1}. {q}" for i, q in enumerate(existing_questions[-5:])])
            existing_display = f"Existing questions:\n{existing_list}" if existing_questions else "No existing questions"
            
            response = chain.invoke({
                "role": role,
                "skill": skill,
                "existing_questions": existing_display,
                "question_prefix": prefix
            })
            
            raw_question = response.content.strip()
            question = re.sub(r'\<.*?\>', '', raw_question, flags=re.DOTALL)
            question = re.sub(r'\(.*?\)|Note:.*|```.*```', '', question)
            question = re.split(r'\?|```', question)[0].strip() + '?'
            question = question.replace('`', '').strip()
            
            # Prevent duplicates
            question_core = re.sub(r'[^a-zA-Z0-9]', '', question.lower())
            existing_cores = [re.sub(r'[^a-zA-Z0-9]', '', q.lower()) for q in existing_questions]
            if not question.endswith('?'):
                raise ValueError("Missing question mark")
            if question_core in existing_cores:
                raise ValueError("Duplicate question core detected")
            if any(q in question for q in existing_questions):
                raise ValueError("Partial duplicate detected")
                
            return question
        except Exception as e:
            st.toast(f"Retry {attempt+1}/{max_retries}: {str(e)}")
            continue
    return "❌ Failed to generate valid question after multiple attempts"

def evaluate_answer(question, answer, model_name):
    try:
        model = ChatGroq(temperature=0.2, groq_api_key=GROQ_API_KEY, model_name=model_name)
        chain = EVALUATION_PROMPT | model | JsonOutputParser()
        response = chain.invoke({"question": question, "answer": answer})
        
        # Convert scores to integers and calculate totals
        rubric_scores = {
            "correctness": int(response["rubric"]["correctness"]["score"]),
            "depth": int(response["rubric"]["depth"]["score"]),
            "relevance": int(response["rubric"]["relevance"]["score"])
        }
        total_score = sum(rubric_scores.values())
        binary_score = 1 if total_score >= 9 else 0  # Threshold at 9/12
        
        return {
            "rubric_scores": rubric_scores,
            "total_score": total_score,
            "binary_score": binary_score,
            "feedback": "\n".join([
                f"**{k.title()}** ({v}/4): {response['rubric'][k]['reason']}"
                for k, v in rubric_scores.items()
            ]),
            "strengths": response.get("strengths", []),
            "suggestions": response.get("suggestions", [])
        }
    except Exception as e:
        return {
            "error": str(e),
            "rubric_scores": {"correctness": 0, "depth": 0, "relevance": 0},
            "total_score": 0,
            "binary_score": 0,
            "feedback": "Evaluation failed",
            "strengths": [],
            "suggestions": []
        }

def get_text_download_link(content, filename):
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download Results</a>'

# Function to generate options for a question
def generate_options(question, correct_answer):
    # Generate three random incorrect answers based on the question context
    incorrect_answers = []
    while len(incorrect_answers) < 3:
        # Example logic for generating incorrect answers
        random_incorrect = f"Incorrect {random.randint(1, 100)}"
        if random_incorrect != correct_answer and random_incorrect not in incorrect_answers:
            incorrect_answers.append(random_incorrect)
    
    # Combine correct and incorrect answers
    options = incorrect_answers + [correct_answer]
    random.shuffle(options)  # Shuffle the options
    return options

# Add this function to generate hints dynamically or use predefined hints
def get_hint(question):
    # Example: Generate a hint dynamically or return a predefined hint
    predefined_hints = {
        "Aptitude": "Break the problem into smaller parts and solve step by step.",
        "Coding": "Think about edge cases and optimize your solution.",
        "Technical": "Focus on trade-offs and system design principles.",
        "Behavioral": "Reflect on a real-world experience that aligns with the question."
    }
    return predefined_hints.get(st.session_state.stage, "Think carefully about the question.")

# Session State Initialization
if "job_role" not in st.session_state:
    st.session_state.update({
        "job_role": "Select",
        "skill": "Aptitude",
        "questions": [],
        "current_index": 0,
        "answers": [],
        "evaluations": [],
        "rubric_totals": [],
        "binary_scores": [],
        "num_questions": 10,
        "ready_next": False,
        "selected_model": "gemma2-9b-it",
        "prev_config": ("", "", "Aptitude", 10, "aptitude"),
        "stage": "aptitude"
    })

with st.sidebar:
    st.header("🛠 Interview Configuration")
    
    # Question range selector
    st.session_state.num_questions = st.number_input(
        "Number of Questions:",
        min_value=1,
        max_value=15,
        value=10,
        step=1
    )
    
    model_options = list(MODEL_CONFIG.keys())
    st.session_state.selected_model = st.selectbox(
        "🤖 AI Model:",
        options=model_options,
        index=model_options.index(st.session_state.selected_model)
    )
    
    # Enhanced job roles
    job_role = st.selectbox(
        "💼 Job Role:",
        options=[
            "Select", 
            "Data Analyst", 
            "Machine Learning Engineer", 
            "Web Developer", 
            "Power BI Developer", 
            "Data Scientist", 
            "Frontend Developer", 
            "Backend Developer", 
            "Fullstack Developer", 
            "DevOps Engineer", 
            "Cloud Engineer", 
            "Mobile App Developer", 
            "Game Developer", 
            "Cybersecurity Specialist", 
            "AI Researcher"
        ]
    )
    
    stage = st.selectbox(
        "Stage:",
        options=["aptitude", "coding", "technical", "behavioral"]
    )
    
    # Enhanced skill selection logic
    skill = "Aptitude"
    if stage == 'coding':
        coding_skills = ["Python", "SQL", "DSA", "R", "Java", "C++", "JavaScript", "Go", "Kotlin", "Swift"]
        skill = st.selectbox(
            "📚 Coding Skill:",
            options=["Select"] + coding_skills,
            index=0 if st.session_state.skill not in coding_skills 
                   else coding_skills.index(st.session_state.skill) + 1
        )
    elif stage != 'aptitude':
        # Enhanced skills map for job roles
        skills_map = {
            "Data Analyst": ["Python", "SQL", "Excel", "Data Visualization", "Power BI", "Tableau"],
            "Machine Learning Engineer": ["Python", "R", "SQL", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch"],
            "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Angular", "Node.js", "PHP"],
            "Power BI Developer": ["Power BI", "DAX", "SQL", "Data Modeling", "Excel"],
            "Data Scientist": ["Python", "R", "SQL", "Statistics", "Machine Learning", "Data Wrangling"],
            "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Vue.js", "TypeScript"],
            "Backend Developer": ["Python", "Java", "C#", "Node.js", "Ruby", "Go", "SQL"],
            "Fullstack Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Python", "SQL"],
            "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Azure", "CI/CD", "Linux", "Terraform"],
            "Cloud Engineer": ["AWS", "Azure", "Google Cloud", "Kubernetes", "Terraform", "Python"],
            "Mobile App Developer": ["Kotlin", "Swift", "Java", "Flutter", "React Native"],
            "Game Developer": ["C++", "C#", "Unity", "Unreal Engine", "Game Physics"],
            "Cybersecurity Specialist": ["Network Security", "Penetration Testing", "Python", "Cryptography", "SIEM"],
            "AI Researcher": ["Python", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Reinforcement Learning"]
        }
        skills = ["Select"] + skills_map.get(job_role, [])
        skill = st.selectbox(
            "📚 Skill:",
            options=skills,
            index=0 if st.session_state.skill not in skills 
                   else skills.index(st.session_state.skill)
        )

    # Reset session on config change
    current_config = (st.session_state.selected_model, job_role, skill, 
                     st.session_state.num_questions, stage)
    if current_config != st.session_state.prev_config:
        st.session_state.update({
            "questions": [],
            "current_index": 0,
            "answers": [''] * st.session_state.num_questions,
            "evaluations": [{} for _ in range(st.session_state.num_questions)],
            "rubric_totals": [0] * st.session_state.num_questions,
            "binary_scores": [0] * st.session_state.num_questions,
            "ready_next": False,
            "prev_config": current_config,
            "skill": skill,
            "stage": stage
        })

st.title("🧑‍💻 Technical Interview AI Agents🤖")
st.caption("🚀 AI-Powered Interview Trainer: Your Smart Hiring Assistant 🤖")

if st.session_state.skill != "Select" or st.session_state.stage == 'aptitude':
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader(f"Question {st.session_state.current_index + 1} of {st.session_state.num_questions}")
    with col2:
        st.caption(f"Model: {st.session_state.selected_model.split('-')[0]}")

    # Adjust question difficulty based on performance
    if st.session_state["current_index"] > 0:  # Ensure it's not the first question
        last_score = st.session_state.binary_scores[st.session_state["current_index"] - 1]
        if last_score == 1:  # If the last question was passed
            difficulty = "Hard" if difficulty == "Medium" else "Medium"
        else:  # If the last question was failed
            difficulty = "Easy" if difficulty == "Medium" else "Medium"

    # Question generation
    if len(st.session_state.questions) < st.session_state.num_questions:
        while len(st.session_state.questions) <= st.session_state.current_index:
            new_q = generate_question(
                st.session_state.job_role,
                st.session_state.skill if st.session_state.stage != 'aptitude' else "Aptitude",
                st.session_state.selected_model,
                st.session_state.questions,
                st.session_state.stage,
                difficulty  # Pass the updated difficulty here
            )
            st.session_state.questions.append(new_q)

    # Navigation buttons for Previous and Next Questions
    col1, col2, col3 = st.columns([1, 2, 1])  # Adjust column widths for better alignment

    with col1:
        if st.session_state["current_index"] > 0:  # Enable "Previous" only if not on the first question
            if st.button("⬅️ Previous Question"):
                st.session_state["current_index"] -= 1
                st.session_state.ready_next = False
                st.experimental_rerun()

    with col3:
        if st.session_state["current_index"] < st.session_state.num_questions - 1:  # Enable "Next" only if not on the last question
            if st.button("➡️ Next Question"):
                st.session_state["current_index"] += 1
                st.session_state.ready_next = False
                st.experimental_rerun()

    # Display the current question
    current_q = st.session_state.questions[st.session_state["current_index"]]
    st.markdown(f"<h3 style='font-size: 24px;'>{current_q}</h3>", unsafe_allow_html=True)

    # Answer input area
    answer = st.text_area(
        "Your Answer:",
        value=st.session_state.answers[st.session_state["current_index"]],
        height=150,
        key=f"ans_{st.session_state['current_index']}"
    )

    # Submit Answer button
    if not st.session_state.ready_next:
        if st.button("Submit Answer"):
            if answer.strip():
                evaluation = evaluate_answer(current_q, answer.strip(), st.session_state.selected_model)
                st.session_state.answers[st.session_state["current_index"]] = answer.strip()
                st.session_state.evaluations[st.session_state["current_index"]] = evaluation
                st.session_state.rubric_totals[st.session_state["current_index"]] = evaluation["total_score"]
                st.session_state.binary_scores[st.session_state["current_index"]] = evaluation["binary_score"]
                st.session_state.ready_next = True
                st.experimental_rerun()

    # Show Hint button
    if st.button("Show Hint"):
        hint = get_hint(current_q)
        st.info(f"Hint: {hint}")

    if st.session_state.ready_next:
        # Calculate cumulative scores
        total_rubric = sum(st.session_state.rubric_totals)
        total_binary = sum(st.session_state.binary_scores)
        max_rubric = (st.session_state.current_index + 1) * 12
        
        st.progress((st.session_state.current_index + 1) / st.session_state.num_questions)
        st.subheader(f"Rubric Score: {total_rubric}/{max_rubric}")
        st.subheader(f"Passed Questions: {total_binary}/{st.session_state.current_index + 1}")
        
        # Award badges based on scores
        if total_rubric >= 30:
            st.markdown("🏅 **Badge Earned: Coding Pro**")
        elif total_rubric >= 20:
            st.markdown("🎖️ **Badge Earned: Aptitude Master**")
        else:
            st.markdown("🎗️ **Badge Earned: Beginner**")
        
        # Display detailed feedback
        eval_data = st.session_state.evaluations[st.session_state.current_index]
        with st.expander("Detailed Feedback"):
            # Display Pass/Fail status
            if eval_data.get("binary_score", 0) == 1:
                st.success("✅ **Status: Pass**")
            else:
                st.error("❌ **Status: Fail**")

            # Display feedback if available
            if "feedback" in eval_data:
                st.markdown("### Feedback:")
                st.markdown(eval_data["feedback"])
            else:
                st.warning("No feedback available for this question.")

            # Display strengths
            st.markdown("### Strengths:")
            strengths = eval_data.get("strengths", [])
            if strengths:
                for strength in strengths:
                    st.markdown(f"- {strength}")
            else:
                st.info("No strengths identified.")

            # Display suggestions
            st.markdown("### Suggestions:")
            suggestions = eval_data.get("suggestions", [])
            if suggestions:
                for suggestion in suggestions:
                    st.markdown(f"- {suggestion}")
            else:
                st.info("No suggestions provided.")

        if st.session_state.current_index < st.session_state.num_questions - 1:
            if st.button("Next Question ➡️"):
                st.session_state.current_index += 1
                st.session_state.ready_next = False
                st.rerun()
        else:
            st.success("🎉 Interview Complete!")
            report_content = f"Final Scores:\nRubric: {total_rubric}/{(st.session_state.num_questions)*12}"
            report_content += f"\nPassed Questions: {total_binary}/{st.session_state.num_questions}\n\n"
            
            for i, (q, a, e) in enumerate(zip(st.session_state.questions, 
                                            st.session_state.answers,
                                            st.session_state.evaluations)):
                report_content += f"Question {i+1}:\n{q}\n\nAnswer:\n{a}\n\n"
                report_content += f"Correctness: {e['rubric_scores']['correctness']}/4\n"
                report_content += f"Depth: {e['rubric_scores']['depth']}/4\n"

# Initialize session state variables if not already set
if "timer" not in st.session_state:
    st.session_state["timer"] = 60  # Default timer value in seconds
if "timer_running" not in st.session_state:
    st.session_state["timer_running"] = True  # Timer starts in running state
if "last_update_time" not in st.session_state:
    st.session_state["last_update_time"] = time.time()  # Track the last update time

# Timer controls
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("⏸ Pause Timer"):
        st.session_state["timer_running"] = False
with col2:
    if st.button("▶️ Resume Timer"):
        st.session_state["timer_running"] = True
with col3:
    if st.button("🔄 Reset Timer"):
        st.session_state["timer"] = 60  # Reset to default or custom value
        st.session_state["last_update_time"] = time.time()

# Update the timer based on elapsed time
if st.session_state["timer_running"]:
    current_time = time.time()
    elapsed_time = current_time - st.session_state["last_update_time"]
    st.session_state["last_update_time"] = current_time

    if st.session_state["timer"] > 0:
        st.session_state["timer"] -= elapsed_time  # Decrement the timer
        st.session_state["timer"] = max(0, st.session_state["timer"])  # Ensure timer doesn't go below 0
        

# Display the countdown timer with a progress bar
total_time = 60  # Total time for the timer
remaining_time = int(st.session_state["timer"])
progress = min(remaining_time / total_time, 1.0)  # Ensure progress is within [0.0, 1.0]

st.markdown(f"<h3 style='text-align: center;'>⏳ Time Remaining: {remaining_time} seconds</h3>", unsafe_allow_html=True)
st.progress(progress)

# Handle timer expiration
if remaining_time <= 0:
    st.warning("⏰ Time's up! Moving to the next question...")
    if st.session_state["current_index"] < st.session_state["num_questions"] - 1:
        st.session_state["current_index"] += 1  # Move to the next question
        st.session_state["timer"] = 60  # Reset the timer for the next question
        st.experimental_rerun()  # Rerun the app to load the next question
    else:
        st.success("🎉 Interview Complete!")

# Calculate progress
progress_percentage = (st.session_state.current_index + 1) / st.session_state.num_questions * 100

# Create a radial progress chart
fig = px.pie(
    values=[progress_percentage, 100 - progress_percentage],
    names=["Completed", "Remaining"],
    title="Progress",
    hole=0.4,  # Donut chart style
    color_discrete_sequence=["#00cc96", "#636efa"]
)

# Display the progress chart
st.plotly_chart(fig, use_container_width=True)
