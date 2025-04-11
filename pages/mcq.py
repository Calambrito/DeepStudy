import streamlit as st
from google import genai
import io
import json
import PyPDF2
from docx import Document
from pages.key import get_api_key

# page conf
if 'username' not in st.session_state:
    st.error("Not logged in.")
    st.stop()

st.set_page_config(page_title="DeepStudy Quiz", page_icon="📚", layout="centered")

key = get_api_key
client = genai.Client(api_key=key)

# helper functions
def parse_file(uploaded_file):
    text = ""
    file_type = uploaded_file.type

    try:
        if file_type == "text/plain":
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            text = stringio.read()
        elif file_type == "application/pdf":
            # Use PyPDF2 to read PDF
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            num_pages = len(pdf_reader.pages)
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Use python-docx to read DOCX
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        return None

    return text

def generate_mcqs(text_content, num_questions=10):
    # check if there is enough content for the no. of questions
    if not text_content or len(text_content) < num_questions * 10:
        st.warning("Text content is too short.")
        return None

    prompt = f"""
    Based on the following text, generate exactly {num_questions} multiple-choice questions (MCQs).
    Each question should have 4 options (labeled A, B, C, D).
    Indicate the correct answer clearly for each question.
    Format the output as a JSON list, where each item is an object with keys: "question", "options" (a list of 4 strings), and "correct_answer" (the string label, e.g., "A", "B", "C", or "D").

    Example Format:
    [
      {{
        "question": "What is the capital of France?",
        "options": ["A) Berlin", "B) Madrid", "C) Paris", "D) Rome"],
        "correct_answer": "C"
      }},
      {{
        "question": "...",
        "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
        "correct_answer": "..."
      }}
    ]

    Text Content:
    ---
    {text_content[:4000]}
    ---

    Generate the JSON list now:
    """

    try:
        with st.spinner(f"Generating {num_questions} MCQs..."):
            response = client.models.generate_content(model = "gemini-2.0-flash", contents = prompt)
            # Debug: Print raw response text
            # st.text_area("Raw Gemini Response:", response.text, height=150)

            # clean and parse the JSON response
            # Gemini might sometimes include backticks or 'json' prefix
            cleaned_response_text = response.text.strip().strip('`').strip()
            if cleaned_response_text.startswith('json'):
                cleaned_response_text = cleaned_response_text[4:].strip()

            mcqs = json.loads(cleaned_response_text)

            # validation of parsed structure
            if isinstance(mcqs, list) and len(mcqs) > 0 and all(
                isinstance(q, dict) and
                'question' in q and
                'options' in q and isinstance(q['options'], list) and len(q['options']) == 4 and
                'correct_answer' in q
                for q in mcqs
            ):
                for mcq in mcqs:
                    print(mcq)
                return mcqs[:num_questions]
            else:
                st.error("Format is incorrect.")
                return None

    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        st.text_area("Problematic Response Text:", cleaned_response_text, height=200)
        return None
    except Exception as e:
        st.error(f"An error occurred during MCQ generation: {e}")
        return None

def display_test(mcqs):
    user_answers = {}
    for i, mcq in enumerate(mcqs):
        st.subheader(f"Question {i+1}:")
        st.write(mcq['question'])

        # Generate unique keys for radio buttons using index and a timestamp/run count
        # This helps prevent state issues if questions change slightly
        unique_key = f"q_{i}"

        # Use st.radio for selection. Store the selected option's *text*
        options_with_labels = [f"{opt}" for opt in mcq['options']] # Use full option text
        selected_option_text = st.radio(
            "Choose your answer:",
            options_with_labels,
            key=unique_key,
            index=None # Default to no selection
        )
        user_answers[i] = selected_option_text # Store the chosen text (e.g., "A) Berlin")

    return user_answers

def calculate_score(mcqs, user_answers):
    score = 0
    results = []
    for i, mcq in enumerate(mcqs):
        user_ans_text = user_answers.get(i)
        correct_option_label = mcq['correct_answer'] # e.g., "C"
        correct_option_text = ""
        for option in mcq['options']:
            # Assuming options start with "A)", "B)", etc.
            if option.strip().startswith(f"{correct_option_label})"):
                correct_option_text = option
                break

        is_correct = (user_ans_text == correct_option_text)
        if (user_ans_text == correct_option_text):
            score += 1

        results.append({
            "question": mcq['question'],
            "user_answer": user_ans_text if user_ans_text else "No Answer",
            "correct_answer_text": correct_option_text,
            "is_correct": is_correct
        })

    return score, results


# the main page
col_header_left, col_header_center, col_header_right = st.columns([3, 1, 1])
with col_header_left:
    st.title("DeepStudy Quiz")
st.write("Upload your study material (TXT, PDF, or DOCX) and generate multiple-choice questions to test your knowledge!")
with col_header_right:
    if st.button("Start Planning!"):
        st.switch_page("pages/app.py")

# initialize session state variables
if 'text_content' not in st.session_state:
    st.session_state.text_content = None
if 'mcqs' not in st.session_state:
    st.session_state.mcqs = None
if 'test_submitted' not in st.session_state:
    st.session_state.test_submitted = False
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = None
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'results' not in st.session_state:
    st.session_state.results = []


# upload files
uploaded_file = st.file_uploader("Choose a file (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"])

if uploaded_file is not None:
    # process one file or new files only
    file_identifier = f"{uploaded_file.name}"
    if 'last_file_id' not in st.session_state or st.session_state.last_file_id != file_identifier:
        st.session_state.last_file_id = file_identifier
        st.session_state.text_content = None # Reset state for new file
        st.session_state.mcqs = None
        st.session_state.test_submitted = False
        st.session_state.user_answers = None
        st.session_state.score = 0
        st.session_state.results = []

        with st.spinner("Parsing file..."):
            st.session_state.text_content = parse_file(uploaded_file)

        if st.session_state.text_content:
            st.success(f"Successfully parsed '{uploaded_file.name}'!")
        else:
            st.error("Could not parse text from the file.")

# generate mcqs
if st.session_state.text_content and not st.session_state.mcqs:
    if st.button("Generate MCQs"):
        st.session_state.mcqs = generate_mcqs(st.session_state.text_content, num_questions=10)
        if st.session_state.mcqs:
            st.success("MCQs generated successfully!")
            st.session_state.test_submitted = False # Reset submission status
            st.rerun() # Rerun to display the test form immediately
        else:
            st.error("Failed to generate MCQs. Please check the text content or try again.")


# display test
if st.session_state.mcqs and not st.session_state.test_submitted:
    st.markdown("---")
    st.header("Take the Test")

    with st.form("mcq_form"):
        user_answers = display_test(st.session_state.mcqs)
        submitted = st.form_submit_button("Submit Answers")

        if submitted:
            st.session_state.user_answers = user_answers
            st.session_state.test_submitted = True
            # Calculate score immediately after submission
            st.session_state.score, st.session_state.results = calculate_score(
                st.session_state.mcqs,
                st.session_state.user_answers
            )
            st.rerun() # Rerun to show results

# display results
if st.session_state.test_submitted:
    st.markdown("---")
    st.header("Test Results")

    score = st.session_state.score
    total_questions = len(st.session_state.mcqs)

    # display score
    st.metric(label="Your Score", value=f"{score}/{total_questions}")

    if score == total_questions:
        st.balloons()
        st.success("Perfect score! Well done!")
    elif score >= total_questions * 0.7: # Threshold for good score
         st.success(f"Great job! You scored {score} out of {total_questions}.")
    else:
        st.warning(f"You scored {score} out of {total_questions}. Keep reviewing!")

    # show detailed results
    st.subheader("Review Your Answers:")
    for i, result in enumerate(st.session_state.results):
        st.markdown(f"**Question {i+1}:** {result['question']}")
        if result['is_correct']:
            st.success(f"✔️ Your answer: {result['user_answer']} (Correct)")
        else:
            st.error(f"❌ Your answer: {result['user_answer']}")
            st.info(f"💡 Correct answer: {result['correct_answer_text']}")
        st.markdown("---")

    # restart or upload new file
    if st.button("Start Over with Same File"):
        st.session_state.test_submitted = False
        st.session_state.user_answers = None
        st.session_state.score = 0
        st.session_state.results = []
        st.rerun()

    if st.button("Upload New File"):
        # clear session state for a completely new start
        keys_to_clear = ['text_content', 'mcqs', 'test_submitted', 'user_answers', 'score', 'results', 'last_file_id']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()