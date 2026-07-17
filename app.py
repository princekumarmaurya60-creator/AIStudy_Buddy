import os
from datetime import datetime
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# LOAD API KEY
# =========================================================
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error(
        "❌ GEMINI_API_KEY नहीं मिली। "
        "अपनी .env फाइल में API Key सही तरीके से डालें।"
    )
    st.stop()


# =========================================================
# GEMINI CLIENT
# =========================================================
try:
    client = genai.Client(api_key=API_KEY)
except Exception as error:
    st.error(f"❌ Gemini Client शुरू नहीं हुआ:\n\n{error}")
    st.stop()


# आपके account में उपलब्ध नया model
MODEL_NAME = "gemini-3.5-flash"


# =========================================================
# SESSION STATE
# =========================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""

if "history" not in st.session_state:
    st.session_state.history = []


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .feature-card {
        padding: 18px;
        border-radius: 15px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 12px;
    }

    .result-box {
        padding: 20px;
        border-radius: 14px;
        border: 1px solid rgba(128, 128, 128, 0.25);
    }

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
    }

    textarea {
        border-radius: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def generate_ai_response(prompt: str) -> str:
    """
    Gemini से response generate करता है।
    """
    if not prompt.strip():
        return "कृपया पहले कोई Topic या Question लिखें।"

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        if response.text:
            return response.text.strip()

        return "AI से कोई उत्तर प्राप्त नहीं हुआ।"

    except Exception as error:
        error_message = str(error)

        return (
            "❌ AI Response Generate नहीं हो पाया।\n\n"
            f"Error: {error_message}\n\n"
            "अपनी Internet Connection, API Key और Model Access चेक करें।"
        )


def extract_pdf_text(uploaded_file) -> str:
    """
    Uploaded PDF से text निकालता है।
    """
    try:
        pdf_bytes = uploaded_file.read()
        pdf_reader = PdfReader(BytesIO(pdf_bytes))

        all_text = []

        for page_number, page in enumerate(pdf_reader.pages, start=1):
            page_text = page.extract_text()

            if page_text:
                all_text.append(
                    f"\n--- Page {page_number} ---\n{page_text}"
                )

        return "\n".join(all_text).strip()

    except Exception as error:
        st.error(f"PDF पढ़ने में Error आया: {error}")
        return ""


def save_to_history(feature_name: str, user_input: str, output: str) -> None:
    """
    Current session की history save करता है।
    """
    st.session_state.history.insert(
        0,
        {
            "feature": feature_name,
            "input": user_input,
            "output": output,
            "time": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
        },
    )


def download_text_button(content: str, filename: str) -> None:
    """
    Generated content को text file में download करने का button।
    """
    st.download_button(
        label="📥 Download Result",
        data=content,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
    )


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("📚 AI Study Buddy")

    selected_page = st.radio(
        "Menu चुनें",
        [
            "🏠 Home",
            "📝 Notes Generator",
            "📄 PDF Summary",
            "❓ Question Answer",
            "🎯 MCQ Generator",
            "💬 AI Chat",
            "🕘 History",
            "ℹ️ About",
        ],
    )

    st.divider()

    st.info(
        f"Model: {MODEL_NAME}\n\n"
        "Technology: Python, Streamlit, Gemini AI, PyPDF"
    )

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.success("Chat साफ हो गई।")

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.success("History साफ हो गई।")


# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<div class="main-title">📚 AI Study Buddy</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sub-title">'
    'Generative AI आधारित Intelligent Learning Assistant'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# HOME PAGE
# =========================================================
if selected_page == "🏠 Home":
    st.success("✅ Gemini API सफलतापूर्वक Connect हो गई है।")

    st.subheader("इस Project में क्या-क्या है?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📝 Notes Generator</h3>
                <p>किसी भी Topic पर आसान और व्यवस्थित Notes बनाएँ।</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="feature-card">
                <h3>📄 PDF Summary</h3>
                <p>PDF Upload करके उसका Summary और Key Points पाएँ।</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>❓ Question Answer</h3>
                <p>किसी भी Study Question का सरल उत्तर पाएँ।</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="feature-card">
                <h3>🎯 MCQ Generator</h3>
                <p>Topic के आधार पर MCQ और Answers बनाएँ।</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>💬 AI Chat</h3>
                <p>AI Teacher से Chat करके अपने Doubts पूछें।</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="feature-card">
                <h3>🕘 History</h3>
                <p>Generated Notes, MCQ और Answers की History देखें।</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader("Project Objective")

    st.write(
        """
        AI Study Buddy का उद्देश्य छात्रों को Generative AI की सहायता से
        Notes, PDF Summary, MCQ, Question-Answer और Study Support उपलब्ध कराना है।
        इससे छात्र कम समय में विषय को बेहतर तरीके से समझ सकते हैं।
        """
    )


# =========================================================
# NOTES GENERATOR
# =========================================================
elif selected_page == "📝 Notes Generator":
    st.header("📝 AI Notes Generator")

    topic = st.text_input(
        "Topic का नाम लिखें",
        placeholder="उदाहरण: Data Structure, DBMS, Artificial Intelligence",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        language = st.selectbox(
            "Language",
            ["हिंदी", "English", "Hindi + English"],
        )

    with col2:
        notes_length = st.selectbox(
            "Notes Length",
            ["Short", "Medium", "Detailed"],
        )

    with col3:
        student_level = st.selectbox(
            "Student Level",
            ["School", "Diploma", "College", "Beginner"],
        )

    extra_instruction = st.text_area(
        "Extra Instruction",
        placeholder="उदाहरण: Definitions, Examples और Important Questions भी जोड़ें।",
    )

    if st.button("✨ Generate Notes"):
        if not topic.strip():
            st.warning("पहले Topic लिखें।")
        else:
            prompt = f"""
            आप एक अनुभवी शिक्षक हैं।

            Topic: {topic}
            Language: {language}
            Notes Length: {notes_length}
            Student Level: {student_level}

            इस Topic पर स्पष्ट, व्यवस्थित और आसान Study Notes बनाएँ।

            Notes में शामिल करें:
            1. परिचय
            2. महत्वपूर्ण परिभाषाएँ
            3. मुख्य Concepts
            4. आसान Examples
            5. महत्वपूर्ण बिंदु
            6. Exam के लिए Questions
            7. अंत में Short Revision Summary

            Extra Instruction:
            {extra_instruction}

            उत्तर साफ Headings और Bullet Points में दें।
            """

            with st.spinner("AI Notes बना रहा है..."):
                result = generate_ai_response(prompt)

            st.session_state.generated_content = result
            save_to_history("Notes Generator", topic, result)

    if st.session_state.generated_content:
        st.subheader("Generated Notes")
        st.markdown(st.session_state.generated_content)

        download_text_button(
            st.session_state.generated_content,
            "AI_Study_Notes.txt",
        )


# =========================================================
# PDF SUMMARY
# =========================================================
elif selected_page == "📄 PDF Summary":
    st.header("📄 PDF Summary Generator")

    uploaded_pdf = st.file_uploader(
        "PDF Upload करें",
        type=["pdf"],
    )

    summary_language = st.selectbox(
        "Summary Language",
        ["हिंदी", "English", "Hindi + English"],
    )

    summary_type = st.selectbox(
        "Summary Type",
        [
            "Short Summary",
            "Detailed Summary",
            "Key Points",
            "Exam Notes",
            "Important Questions",
        ],
    )

    if uploaded_pdf is not None:
        st.success(f"PDF Selected: {uploaded_pdf.name}")

        if st.button("📖 Generate PDF Summary"):
            with st.spinner("PDF का Text पढ़ा जा रहा है..."):
                pdf_text = extract_pdf_text(uploaded_pdf)

            if not pdf_text:
                st.error(
                    "PDF से Text नहीं निकला। यह Scanned/Image PDF हो सकती है।"
                )
            else:
                # बहुत बड़ी PDF होने पर शुरुआती text उपयोग करें
                maximum_characters = 50000
                shortened_text = pdf_text[:maximum_characters]

                prompt = f"""
                आप एक Expert Study Assistant हैं।

                नीचे दिए गए PDF Text का {summary_type} बनाएँ।

                Language: {summary_language}

                Instructions:
                - आसान भाषा का उपयोग करें।
                - मुख्य Headings बनाएँ।
                - Important Definitions शामिल करें।
                - Important Facts और Key Points दें।
                - गलत जानकारी न जोड़ें।
                - PDF के बाहर की अनावश्यक जानकारी न दें।

                PDF Text:
                {shortened_text}
                """

                with st.spinner("AI Summary बना रहा है..."):
                    result = generate_ai_response(prompt)

                st.session_state.generated_content = result
                save_to_history(
                    "PDF Summary",
                    uploaded_pdf.name,
                    result,
                )

    if st.session_state.generated_content:
        st.subheader("PDF Result")
        st.markdown(st.session_state.generated_content)

        download_text_button(
            st.session_state.generated_content,
            "PDF_Summary.txt",
        )


# =========================================================
# QUESTION ANSWER
# =========================================================
elif selected_page == "❓ Question Answer":
    st.header("❓ AI Question Answer")

    question = st.text_area(
        "अपना Question लिखें",
        placeholder="उदाहरण: Stack और Queue में क्या अंतर है?",
        height=150,
    )

    answer_language = st.selectbox(
        "Answer Language",
        ["हिंदी", "English", "Hindi + English"],
    )

    answer_style = st.selectbox(
        "Answer Style",
        [
            "Very Simple",
            "Exam Answer",
            "Detailed Explanation",
            "Short Answer",
        ],
    )

    if st.button("🤖 Get Answer"):
        if not question.strip():
            st.warning("पहले Question लिखें।")
        else:
            prompt = f"""
            आप एक अनुभवी शिक्षक हैं।

            Student Question:
            {question}

            Language: {answer_language}
            Answer Style: {answer_style}

            Instructions:
            - उत्तर सही और आसान भाषा में दें।
            - जरूरत होने पर Example दें।
            - Exam Answer हो तो Heading और Points में लिखें।
            - शुरुआत से समझाएँ क्योंकि छात्र Beginner है।
            """

            with st.spinner("AI उत्तर तैयार कर रहा है..."):
                result = generate_ai_response(prompt)

            st.session_state.generated_content = result
            save_to_history("Question Answer", question, result)

    if st.session_state.generated_content:
        st.subheader("AI Answer")
        st.markdown(st.session_state.generated_content)

        download_text_button(
            st.session_state.generated_content,
            "AI_Answer.txt",
        )


# =========================================================
# MCQ GENERATOR
# =========================================================
elif selected_page == "🎯 MCQ Generator":
    st.header("🎯 AI MCQ Generator")

    mcq_topic = st.text_input(
        "MCQ Topic",
        placeholder="उदाहरण: Python, DBMS, Computer Network",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        mcq_count = st.selectbox(
            "Number of MCQs",
            [5, 10, 15, 20],
        )

    with col2:
        mcq_level = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Mixed"],
        )

    with col3:
        mcq_language = st.selectbox(
            "MCQ Language",
            ["हिंदी", "English", "Hindi + English"],
        )

    if st.button("🎯 Generate MCQs"):
        if not mcq_topic.strip():
            st.warning("पहले MCQ Topic लिखें।")
        else:
            prompt = f"""
            Topic: {mcq_topic}
            Total MCQ: {mcq_count}
            Difficulty: {mcq_level}
            Language: {mcq_language}

            इस Topic पर Multiple Choice Questions बनाएँ।

            प्रत्येक Question का Format:
            Question 1:
            A.
            B.
            C.
            D.
            Correct Answer:
            Explanation:

            सभी Questions अलग और सही होने चाहिए।
            अंत में Answer Key भी दें।
            """

            with st.spinner("MCQ तैयार हो रहे हैं..."):
                result = generate_ai_response(prompt)

            st.session_state.generated_content = result
            save_to_history("MCQ Generator", mcq_topic, result)

    if st.session_state.generated_content:
        st.subheader("Generated MCQs")
        st.markdown(st.session_state.generated_content)

        download_text_button(
            st.session_state.generated_content,
            "Generated_MCQs.txt",
        )


# =========================================================
# AI CHAT
# =========================================================
elif selected_page == "💬 AI Chat":
    st.header("💬 AI Teacher Chat")

    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    user_message = st.chat_input(
        "अपना Study Question लिखें..."
    )

    if user_message:
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        with st.chat_message("user"):
            st.markdown(user_message)

        previous_chat = ""

        for item in st.session_state.chat_history[-8:]:
            previous_chat += (
                f"{item['role'].upper()}: {item['content']}\n"
            )

        prompt = f"""
        आप AI Study Buddy हैं।
        आप एक दोस्ताना और अनुभवी शिक्षक की तरह उत्तर देते हैं।

        Rules:
        - छात्र Beginner है।
        - आसान हिंदी या Hinglish में समझाएँ।
        - जरूरत होने पर Example दें।
        - उत्तर साफ और व्यवस्थित रखें।
        - गलत तथ्य न बनाएँ।

        Conversation:
        {previous_chat}

        Student का नया Question:
        {user_message}
        """

        with st.chat_message("assistant"):
            with st.spinner("AI सोच रहा है..."):
                answer = generate_ai_response(prompt)

            st.markdown(answer)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        save_to_history("AI Chat", user_message, answer)


# =========================================================
# HISTORY
# =========================================================
elif selected_page == "🕘 History":
    st.header("🕘 Study History")

    if not st.session_state.history:
        st.info("अभी कोई History उपलब्ध नहीं है।")

    else:
        for index, item in enumerate(
            st.session_state.history,
            start=1,
        ):
            title = (
                f"{index}. {item['feature']} — {item['time']}"
            )

            with st.expander(title):
                st.write("**Input:**")
                st.write(item["input"])

                st.write("**Output:**")
                st.markdown(item["output"])

                st.download_button(
                    label="Download",
                    data=item["output"],
                    file_name=f"history_{index}.txt",
                    mime="text/plain",
                    key=f"history_download_{index}",
                )


# =========================================================
# ABOUT
# =========================================================
elif selected_page == "ℹ️ About":
    st.header("ℹ️ About Project")

    st.markdown(
        """
        ### Project Name

        **AI Study Buddy – Intelligent Learning Assistant using Generative AI**

        ### Technologies Used

        - Python
        - Streamlit
        - Google Gemini API
        - Google GenAI Python SDK
        - PyPDF
        - Python Dotenv

        ### Main Features

        - AI Notes Generator
        - PDF Summary
        - Question Answer
        - MCQ Generator
        - AI Chat
        - Session History
        - Download Generated Content

        ### Project Objective

        छात्रों को Generative AI की सहायता से पढ़ाई के लिए Notes,
        Summary, Questions, Answers और MCQs उपलब्ध कराना।

        ### Developed For

        College Generative AI Project
        """
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "AI Study Buddy | Python + Streamlit + Gemini AI"
)