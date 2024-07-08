import streamlit as st
import openai
import chardet
from PyPDF2 import PdfReader
from docx import Document
import json

# GPT3Responder Class
class GPT3Responder:
    def __init__(self, api_key):
        self.client = openai
        self.client.api_key = api_key

    def get_response(self, messages):
        chat_completion = self.client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return chat_completion.choices[0].message.content

    def set_prompt(self):
        prompt_template = '''SYSTEM: You are a resume formatting assistant and you must read a resume and fill a universal informational format that is given below based on the document provided,
        make sure the each section has relevant information, and if there is no information for a section, then leave it empty. It should be grammatically correct.

        FORMAT: Write in dictionary format so that it can be directly saved into a JSON
        "Name": (Full name),
        "Contact": (mobile, email)
        "Skills": (all the skills listed in the resume from anywhere)
        "Educational Qualifications": (degrees and scores achieved)
        "Projects": (projects done other than work experience, just write in 3 points highlighting the methods used)
        "Work Experience": (Just Write the company name, position and describe the work in 2 points in small sentences)
        '''

        return prompt_template

    def get_prompt(self, resume):
        doc = resume
        return doc

    def generate_dict(self, res):
        user_prompt = self.get_prompt(res)
        messages = [
            {"role": "system", "content": self.set_prompt()},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": ""},
        ]

        response = self.get_response(messages)
        return response

# Function to read content of the uploaded file
def read_uploaded_file_content(uploaded_file):
    try:
        raw_data = uploaded_file.read()
        result = chardet.detect(raw_data)
        encoding = result.get('encoding', 'utf-8')
        resume_content = raw_data.decode(encoding)
        return resume_content
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Function to read content of a DOCX file
def read_docx_content(file):
    try:
        doc = Document(file)
        raw_data = ""
        for para in doc.paragraphs:
            raw_data += para.text + "\n"
    except:
        print("Error reading docx file")
    return raw_data

# Streamlit UI
def main():
    st.title("Resume Converter to JSON")

    # Input for OpenAI API Key
    api_key = st.text_input("Enter your OpenAI API Key", type="password")

    if not api_key:
        st.warning("Please enter your OpenAI API key.")
        return

    # Document Upload
    uploaded_files = st.file_uploader("Upload Resumes (PDF, DOCX, or Text)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    # GPT-3 Chatbot
    gpt3_responder = GPT3Responder(api_key)

    # Generate Resumes Button
    if uploaded_files is not None and st.button("Generate Resumes"):
        for uploaded_file in uploaded_files:
            try:
                # Read the content of the uploaded file
                with uploaded_file as f:
                    if uploaded_file.type == "application/pdf":
                        # Extract text from PDF using PyPDF2
                        pdf_reader = PdfReader(f)
                        raw_data = b""
                        for page_num in range(len(pdf_reader.pages)):
                            raw_data += pdf_reader.pages[page_num].extract_text().encode('utf-8')
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        # Extract text from DOCX
                        raw_data = read_docx_content(f)
                    else:
                        # Read text file
                        raw_data = f.read()

                # Decode the file content with the detected encoding
                if uploaded_file.type == "application/pdf":
                    result = chardet.detect(raw_data)
                    encoding = result.get('encoding', 'utf-8')
                    resume_content = raw_data.decode(encoding)
                else:
                    resume_content = raw_data

                # Generate Resume
                formatted_resume = gpt3_responder.generate_dict(resume_content)

                # Save as JSON
                json_filename = f"{uploaded_file.name.replace(' ', '_').replace('.', '_')}.json"
                with open(json_filename, 'w', encoding='utf-8') as json_file:
                    json.dump(formatted_resume, json_file, ensure_ascii=False)

                st.success(f"JSON file saved: {json_filename}")

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")

if __name__ == "__main__":
    main()
