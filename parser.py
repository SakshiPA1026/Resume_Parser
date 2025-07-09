import os
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import fitz
import docx  

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

prompt = PromptTemplate.from_template("""
You are a resume parser. Extract the following fields in JSON format:
- name
- email
- phone
- skills
- education (list with degree, institution, passing_year,marks_percentage_cgpa)
- work_experience (list with title, company, dates, description)

Resume Text:
-------------------
{text}
-------------------
Return JSON only.
""")


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs]).strip()

def parse_resume_text(text):
    chain = prompt | llm | JsonOutputParser()
    return chain.invoke({"text": text})
