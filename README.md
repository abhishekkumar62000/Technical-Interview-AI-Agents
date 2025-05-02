![AI](https://github.com/user-attachments/assets/0af3b01f-94df-4e62-935e-42df2f059dde)
![page0](https://github.com/user-attachments/assets/367341c2-29e8-4c95-a447-4ec005ee167d)
![page1](https://github.com/user-attachments/assets/418f28c0-9e62-4b26-ac07-79d0e6dd5753)

---

# 🧑‍💻 Technical Interview AI Agents 🤖

> An AI-powered mock interview assistant for job seekers, HR teams, and ed-tech platforms.

🚀 **Live Demo**: [Click here to try the app](https://technical-interview-ai-agents.streamlit.app/)

---

## 📌 Introduction

Welcome to **Technical Interview AI Agents**, a smart and interactive interview preparation assistant powered by LLMs. Built using **Streamlit**, **LangChain**, and the **Groq API**, this app simulates real-world technical interviews across various domains, skills, and difficulty levels.

Whether you're a job seeker preparing for interviews, an HR team conducting evaluations, or an ed-tech platform offering assessments, this tool is **your intelligent companion**.

---

## 🎯 What This App Does

✅ Generates adaptive, domain-specific technical questions
✅ Evaluates answers using rubric-based logic
✅ Provides strengths, feedback, and improvement tips
✅ Gamifies the interview with badges and progress tracking
✅ Downloads full session reports (PDF)

---

## 🛠️ Tech Stack & Tools Used

| Component             | Tool/Library      |
| --------------------- | ----------------- |
| 🖥️ UI Framework      | Streamlit         |
| 🤖 LLM Integration    | Groq API          |
| 🔗 Prompt Engineering | LangChain         |
| 📊 Data Visualization | Plotly            |
| 🔐 Secrets Management | Python-dotenv     |
| 🔊 Sound Alerts       | Pygame, Playsound |

---

## 💡 Key Features – In Detail

### 🔄 1. Dynamic Question Generation

* **Stages**:

  * Aptitude (🧠): Logical & quantitative reasoning
  * Coding (💻): Programming problems with real-world logic
  * Technical (🔍): System design, architecture, trade-offs
  * Behavioral (👥): Soft skills & situational judgment

* **Difficulty Levels**: Easy, Medium, Hard (auto-adjusting based on performance)

* **Prompt Crafting**: Uses LangChain to generate dynamic prompts tailored to:

  * Job Role
  * Selected Skill (e.g., Python, ML, SQL)
  * Question Stage & Difficulty

---

### 🧪 2. Evaluation System

* **Scoring Criteria**:

  * ✅ Correctness: Accuracy & completeness
  * 📚 Depth: Use of examples, edge cases
  * 🎯 Relevance: Alignment with question intent

* **Scoring Model**:

  * Each answer is scored out of 12
  * ≥9 = Pass ✅ | <9 = Fail ❌

* **Detailed Feedback**:

  * 📈 Strengths highlighted
  * 📉 Weaknesses noted
  * 🎯 Improvement suggestions generated

---

### 🏆 3. Gamification Engine

* **Badge Awards**:

  * 🧠 Aptitude Master
  * 💻 Coding Pro
  * 🎯 Technical Guru
  * 💬 Behavioral Expert

* **Progress Trackers**:

  * 📊 Radial chart of stage-wise performance
  * 📉 Progress bars to visualize completion & accuracy

---

### ⏲️ 4. Smart Timers & Alerts

* ⏱️ Countdown timer per question
* 🔔 Alert sound at final 10 seconds
* ⛔ Auto-evaluation post-timeout

---

### ⚙️ 5. Configurable Experience

* 🧑‍💼 Choose from Job Roles:

  * Data Scientist, Web Developer, AI Researcher, etc.
* 🛠️ Pick Your Skills:

  * Python, SQL, JavaScript, Machine Learning, NLP...
* 🔢 Select Number of Questions: 1 to 15
* 🗃️ Choose Difficulty Level or let AI decide dynamically

---

### 📥 6. Exportable Interview Report

* 📝 Generates a session summary

  * All questions & answers
  * Scores, feedback & status
* 📎 Downloadable PDF format (ideal for:

  * Job applications
  * Mentorship tracking
  * Internal HR documentation)

---

## 🌐 Real-World Applications

| Use Case               | Benefits                                          |
| ---------------------- | ------------------------------------------------- |
| 👨‍💼 HR & Recruitment | Automate interviews, reduce bias, scale processes |
| 👨‍🎓 Candidate Prep   | Practice mock interviews, get AI feedback         |
| 🏫 Ed-Tech Platforms   | Use as assignment/evaluation tool                 |
| 🏢 Corporates          | Employee assessments & upskilling                 |
| 💼 Freelance Portals   | Pre-screen freelancer tech skills                 |
| 🎮 Hackathons          | Automated coding & aptitude evaluations           |

---

## ✅ Strengths

* 📈 **Scalable** for multiple roles, stages, and candidates
* 🧩 **Modular & Configurable** for different use cases
* 🧠 **Smart Feedback** with real-time analysis
* 🕹️ **Engaging UI** with gamification & sounds
* 📥 **Exportable Reports** for detailed review

---

## 🛠️ Suggestions for Future Enhancements

🔍 **Candidate Feedback Generator** – Personalized improvement report
📡 **HR Tool Integration** – ATS/CRM system connectivity
🧠 **LLM-Enhanced Evaluation** – Reduce hallucination & scoring errors
📱 **Mobile Support** – Responsive app experience
🧑‍💼 **Expand Role & Skill Library** – Add DevOps, Blockchain, UI/UX, etc.

---

## 🚀 Try It Now!

🔗 **[Launch the App](https://technical-interview-ai-agents.streamlit.app/)**
💻 Works best in desktop view
🧪 Try different combinations of roles, skills, and stages!

---
---

## 🧑‍💻 Localhost Setup Guide for Technical Interview AI Agents 🤖

### 🛠️ **Prerequisites**

Make sure the following tools are installed:

* ✅ Python 3.8+
* ✅ pip (Python package manager)
* ✅ Git (optional but useful)
* ✅ A code editor (like VS Code)

---

### 📁 **1. Clone or Download the Project**

If your code is hosted on GitHub:

```bash
git clone https://github.com/abhishekkumar62000/Technical-Interview-AI-Agents.git
cd technical-interview-ai-agents
```

Or just download the ZIP and extract it, then `cd` into the folder.

---

### 📦 **2. Create & Activate a Virtual Environment (Optional but Recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

### 📄 **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` file yet, create one with all used libraries:

```txt
streamlit
langchain
python-dotenv
groq
plotly
pygame
playsound
```

Then run:

```bash
pip install streamlit langchain python-dotenv groq plotly pygame playsound
```

---

### 🔐 **4. Set Environment Variables**

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

(Replace with your actual Groq API key)

---

### ▶️ **5. Run the App Locally**

```bash
streamlit run app.py
```

Change `app.py` to whatever your main file is named.

Your app will now open in your default browser at:

```
http://localhost:8501
```

---
## 🤝 Connect with Me

👨‍💻 Developed by: **Abhishek Kumar**
📫 Reach me on [LinkedIn](https://www.linkedin.com/in/abhishek-yadav-70a69829a/) | 🌐 [Portfolio](https://www.datascienceportfol.io/abhiydv23096)

Feel free to fork, star ⭐ this repo, and contribute with ideas, bug reports, or feature requests!
Let’s make technical interview preparation smarter, together. 🙌

---
