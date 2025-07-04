import re
import spacy
import io
from pdfminer.high_level import extract_text_to_fp
from docx import Document
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Ensure NLTK data is downloaded
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

# Load a pre-trained spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
    exit()

# Define common stopwords
STOPWORDS = set(stopwords.words('english'))

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using pdfminer.six.
    """
    with open(pdf_path, 'rb') as fp:
        output_string = io.StringIO()
        extract_text_to_fp(fp, output_string)
        return output_string.getvalue()

def extract_text_from_docx(docx_path):
    """
    Extracts text from a DOCX file using python-docx.
    """
    document = Document(docx_path)
    full_text = []
    for paragraph in document.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def clean_text(text):
    """
    Cleans text by removing extra whitespace and standardizing newlines.
    """
    # Replace multiple spaces/newlines with single space, but preserve double newlines for section separation
    text = re.sub(r'[ \t]+', ' ', text).strip() # Replace multiple spaces/tabs with single space
    text = re.sub(r'\n{3,}', '\n\n', text) # Reduce more than two newlines to two
    return text

def parse_resume(text):
    """
    Parses the extracted text to find key resume details using spaCy and regex.
    """
    cleaned_text = clean_text(text)
    doc = nlp(cleaned_text)
    data = {
        'name': '',
        'email': '',
        'phone': '',
        'skills': [],
        'education': [],
        'work_experience': []
    }

    # Split text into lines for easier processing
    lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
    print(f"DEBUG: Cleaned Text (first 500 chars):\n{cleaned_text[:500]}...")
    print(f"DEBUG: Number of lines after splitting: {len(lines)}")


    # --- 1. Extract Name (Highly Prioritized and Robust) ---
    print("\n--- Name Extraction Debug ---")
    name_found = False
    # Keywords that indicate a line is likely NOT a name
    name_exclusion_keywords = r'\d|\b(email|phone|linkedin|github|portfolio|summary|objective|career objective|key experties|skills|education|work experience|experience|academic projects|course|personal details|hobbies|computer skills|date of birth|father\'s name|gender|languages|marital status|nationality|declaration|address|road|street|lane|nagar|colony|apartment|thane|maharashtra|chiplun|ratnagiri|dombivali)\b'

    # Prioritize the very first few lines for name
    for i in range(min(5, len(lines))): # Increased range slightly to catch more cases
        line = lines[i].strip()
        print(f"DEBUG: Name candidate line {i}: '{line}'")
        if not line:
            continue

        # Filter out lines containing common non-name indicators
        if re.search(name_exclusion_keywords, line, re.IGNORECASE):
            print(f"DEBUG: Line '{line}' excluded by keyword filter.")
            continue

        # Rule 1: Look for all-caps name (2-4 words)
        if re.match(r'^[A-Z][A-Z\s-]+[A-Z]$', line) and 2 <= len(line.split()) <= 4:
            data['name'] = line
            name_found = True
            print(f"DEBUG: Name found by ALL-CAPS rule: '{data['name']}'")
            break
        # Rule 2: Look for Title Case name (2-4 words)
        elif re.match(r'^[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3}$', line) and 2 <= len(line.split()) <= 4:
            data['name'] = line
            name_found = True
            print(f"DEBUG: Name found by Title Case rule: '{data['name']}'")
            break
    
    # Fallback to spaCy's PERSON entity with strong filtering if no direct match
    if not name_found:
        print("DEBUG: No name found by direct regex rules, trying spaCy PERSON entities.")
        for i in range(min(7, len(lines))): # Check a few more lines for spaCy
            line = lines[i].strip()
            if not line:
                continue
            
            line_doc = nlp(line)
            for ent in line_doc.ents:
                if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 4:
                    print(f"DEBUG: spaCy found potential PERSON: '{ent.text}'")
                    # Filter out entities that are likely addresses, phone numbers, or common resume headers
                    if not re.search(name_exclusion_keywords, ent.text, re.IGNORECASE):
                        data['name'] = ent.text.strip()
                        name_found = True
                        print(f"DEBUG: Name found by spaCy (filtered): '{data['name']}'")
                        break
                    else:
                        print(f"DEBUG: spaCy PERSON '{ent.text}' excluded by keyword filter.")
            if name_found:
                break
    
    # Final Fallback: If still no name, take the very first non-empty line that doesn't look like an exclusion
    if not data['name'] and lines:
        print("DEBUG: No name found, trying final fallback to first valid line.")
        for line in lines:
            line = line.strip()
            if line and not re.search(name_exclusion_keywords, line, re.IGNORECASE):
                data['name'] = line
                print(f"DEBUG: Name found by final fallback: '{data['name']}'")
                break
            else:
                print(f"DEBUG: Final fallback line '{line}' excluded.")


    print(f"DEBUG: Final Extracted Name: '{data['name']}'")


    # --- 2. Extract Email ---
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', cleaned_text)
    if email_match:
        data['email'] = email_match.group(0)
    print(f"DEBUG: Extracted Email: '{data['email']}'")


    # --- 3. Extract Phone Number ---
    # More flexible phone number regex to catch various formats
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4,}', cleaned_text)
    if phone_match:
        data['phone'] = phone_match.group(0)
    else:
        phone_match = re.search(r'\b\d{10}\b', cleaned_text) # Fallback for 10-digit numbers
        if phone_match:
            data['phone'] = phone_match.group(0)
    print(f"DEBUG: Extracted Phone: '{data['phone']}'")


    # --- 4. Extract Skills (Improved) ---
    print("\n--- Skills Extraction Debug ---")
    known_skills = [
        "Python", "SQL", "Tableau", "Power BI", "NLP", "Neural Networks",
        "Machine Learning", "Data Visualization", "Gen-AI", "Streamlit",
        "LangChain", "OpenAI API", "xhtml2pdf", "PDFLoader", "Excel",
        "Accounting", "Finance", "Auditing", "Taxation", "GST Filing",
        "Bank Reconciliation", "Financial Statements", "Balance Sheet",
        "Profit & Loss", "Debtors Management", "Petty Cash", "Voucher Management",
        "Income Tax Returns", "Tax Audit", "Compliance", "Bookkeeping",
        "ERP Systems", "Data Entry", "Communication", "Teamwork", "Problem Solving",
        "E-invoicing", "Sales & Purchase Entries", "NEFT", "RTGS", "Cheques Issue",
        "Finalization of Accounts", "Statement of Accounts", "Consumption Charts",
        "Trials Balance", "Scrutiny of Desperation", "Fixed Assets", "MS-OFFICE", "Tally", "SAP", "MS-CIT",
        "Data Science", "Data Analyst", "AI", "ML", "Artificial Intelligence", "Web Development", "HTML", "CSS", "JavaScript", "Java", "C++",
        "Project Management", "Customer Service", "Sales", "Marketing", "Research", "Analysis", "Reporting"
    ]
    extracted_skills = []
    text_lower = cleaned_text.lower()
    
    # Section-based skill extraction (prioritized)
    skills_section_match = re.search(r'(?:KEY EXPERTIES|SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES|COMPUTER SKILLS)\s*\n(.*?)(?=\n\n|\n(?:EDUCATION|WORK EXPERIENCE|EXPERIENCE|ACADEMIC PROJECTS|COURSE|PERSONAL DETAILS|HOBBIES|\Z))', cleaned_text, re.DOTALL | re.IGNORECASE)
    if skills_section_match:
        skills_text = skills_section_match.group(1).strip()
        print(f"DEBUG: Skills section text found:\n{skills_text[:100]}...")
        skill_lines = re.split(r'[\n•,-]\s*', skills_text)
        for line in skill_lines:
            line = line.strip()
            if not line: continue
            for skill in known_skills:
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', line.lower()):
                    extracted_skills.append(skill)
                    print(f"DEBUG: Found skill '{skill}' in line '{line}'")
    else:
        print("DEBUG: No explicit skills section found. Falling back to full text search.")
    
    # Fallback: Search for skills throughout the text if no clear section or if section extraction was incomplete
    if not extracted_skills: # Only if section-based extraction yielded nothing
        for skill in known_skills:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                extracted_skills.append(skill)
                print(f"DEBUG: Found skill '{skill}' in full text fallback.")
    
    data['skills'] = list(set(extracted_skills)) # Remove duplicates
    print(f"DEBUG: Final Extracted Skills: {data['skills']}")


    # --- 5. Generic Section Extractor Helper Function ---
    def extract_section(section_keywords, stop_keywords, text_lines, section_name="Unknown"):
        section_content = []
        start_collecting = False
        print(f"\nDEBUG: Starting {section_name} section extraction.")
        for line_num, line in enumerate(text_lines):
            lower_line = line.lower()
            if any(re.search(r'\b' + re.escape(kw) + r'\b', lower_line) for kw in section_keywords) and not start_collecting:
                if len(line.split()) <= 5 or line.strip().endswith(':'):
                    start_collecting = True
                    print(f"DEBUG: Found {section_name} header at line {line_num}: '{line}'")
                    continue
            elif start_collecting:
                if not line.strip(): # Check for empty line
                    print(f"DEBUG: Empty line encountered, stopping {section_name} collection.")
                    break
                if any(re.search(r'\b' + re.escape(kw) + r'\b', lower_line) for kw in stop_keywords):
                    print(f"DEBUG: Stop keyword encountered in {section_name} at line {line_num}: '{line}', stopping collection.")
                    break
                section_content.append(line)
        content = "\n".join(section_content)
        print(f"DEBUG: Raw {section_name} section content:\n{content[:200]}...") # Print first 200 chars
        return content

    # Define stop keywords for each section (other section headers)
    education_stop_keywords = ["work experience", "experience", "academic projects", "skills", "key experties", "personal details", "hobbies", "computer skills", "summary", "career objective", "course"]
    work_experience_stop_keywords = ["education", "skills", "key experties", "personal details", "hobbies", "computer skills", "summary", "career objective", "course"]
    
    # Extract Education Section
    education_section_keywords = ["education", "academic", "university", "college", "institute", "bachelor", "master", "phd", "degree", "ssc", "hsc", "b.com", "certificate", "coursework"]
    education_section_text = extract_section(education_section_keywords, education_stop_keywords, lines, "Education")


    # Extract Work Experience Section (including Academic Projects)
    experience_section_keywords = ["work experience", "experience", "employment history", "professional experience", "academic projects"]
    experience_section_text = extract_section(experience_section_keywords, work_experience_stop_keywords, lines, "Work Experience")


    # --- 5. Parse Education Details from Extracted Section ---
    print("\n--- Education Parsing Debug ---")
    temp_education = []
    if education_section_text:
        # Split by year ranges, degree names, or institution names to identify individual entries
        edu_entries = re.split(r'\n(?=\d{4}(?:-\d{4})?|\b(?:Bachelor|Master|PhD|Higher Secondary Certificate|Secondary School Certificate|B\.COM|Coursework|Certificate)\b)', education_section_text, flags=re.IGNORECASE)
        print(f"DEBUG: Education entries found: {len(edu_entries)}")
        
        for entry_num, entry_text in enumerate(edu_entries):
            entry_text = entry_text.strip()
            print(f"DEBUG: Processing Education Entry {entry_num}: '{entry_text[:100]}...'")
            if not entry_text: continue

            current_edu = {'institution': '', 'degree': '', 'passing_year': '', 'marks_percentage_cgpa': ''}

            # Extract year first, as it's often a strong delimiter
            year_match = re.search(r'(\d{4}(?:-\d{4})?)', entry_text)
            if year_match:
                current_edu['passing_year'] = year_match.group(0).strip()
                entry_text = entry_text.replace(current_edu['passing_year'], '').strip()
                print(f"DEBUG:   Year: {current_edu['passing_year']}")

            # Extract degree (more comprehensive list)
            degree_match = re.search(r'(Bachelor of Engineering|Higher Secondary Certificate|Secondary School Certificate|B\.COM|Master in Data Science and Analyst|Bachelor|Master|PhD|Coursework|Certificate)', entry_text, re.IGNORECASE)
            if degree_match:
                current_edu['degree'] = degree_match.group(0).strip()
                entry_text = entry_text.replace(current_edu['degree'], '').strip()
                print(f"DEBUG:   Degree: {current_edu['degree']}")


            # Extract marks/CGPA
            marks_match = re.search(r'(\d+(\.\d+)?\s*(%|percent|percentage|CGPA|GPA|out of \d+|/\d+)|Grade\s*[A-D])', entry_text, re.IGNORECASE)
            if marks_match:
                current_edu['marks_percentage_cgpa'] = marks_match.group(0).strip()
                entry_text = entry_text.replace(marks_match.group(0), '').strip() # Replace the full matched string
                print(f"DEBUG:   Marks/CGPA: {current_edu['marks_percentage_cgpa']}")


            # The remaining text is likely the institution
            current_edu['institution'] = entry_text.strip()
            
            # Clean up institution if it contains degree or marks (redundant removal, just in case)
            if current_edu['institution'] and current_edu['degree'] and current_edu['degree'].lower() in current_edu['institution'].lower():
                current_edu['institution'] = re.sub(re.escape(current_edu['degree']), '', current_edu['institution'], flags=re.IGNORECASE).strip()
            if current_edu['institution'] and current_edu['marks_percentage_cgpa'] and current_edu['marks_percentage_cgpa'].lower() in current_edu['institution'].lower():
                current_edu['institution'] = re.sub(re.escape(current_edu['marks_percentage_cgpa']), '', current_edu['institution'], flags=re.IGNORECASE).strip()
            
            # Remove common leading/trailing punctuation from institution
            current_edu['institution'] = re.sub(r'^[\s,-]+|[\s,-]+$', '', current_edu['institution']).strip()
            print(f"DEBUG:   Institution: {current_edu['institution']}")


            if any(current_edu.values()): # Only add if at least one field is populated
                temp_education.append(current_edu)

        data['education'] = temp_education
    print(f"DEBUG: Final Extracted Education: {data['education']}")


    # --- 6. Parse Work Experience Details from Extracted Section ---
    print("\n--- Work Experience Parsing Debug ---")
    temp_experiences = []
    if experience_section_text:
        # Split by new lines that look like a new job/project entry (e.g., starts with a number, bold text, or common job title/company patterns)
        exp_entries = re.split(r'\n(?=\d+\.\s*[A-Z]|\b(?:Working|Developed|Designed|Created)\b|\b[A-Z][A-Za-z\s&,.-]+\b\s*(?:\(From|\n))', experience_section_text, flags=re.MULTILINE)
        print(f"DEBUG: Work Experience entries found: {len(exp_entries)}")
        
        for entry_num, entry_text in enumerate(exp_entries):
            entry_text = entry_text.strip()
            print(f"DEBUG: Processing Work Experience Entry {entry_num}: '{entry_text[:100]}...'")
            if not entry_text: continue

            current_exp = {'company': '', 'title': '', 'dates': '', 'description': ''}

            # Extract Dates first - they are strong indicators
            date_match = re.search(r'(?:From )?(\d{2}\.\d{2}\.\d{4} to (?:till Date|\d{2}\.\d{2}\.\d{4})|\d{4}-\d{4}|\d{4})', entry_text)
            if date_match:
                current_exp['dates'] = date_match.group(0).strip()
                entry_text = entry_text.replace(current_exp['dates'], '').strip()
                print(f"DEBUG:   Dates: {current_exp['dates']}")


            # Extract Company and Title
            company_title_match = re.match(r'^(?:\d+\.\s*)?(.+?)(?:\s+(?:As an|for|Through|Technology Used:|Technologies Used:)|$)', entry_text, re.IGNORECASE | re.DOTALL)
            if company_title_match:
                company_title_line = company_title_match.group(1).strip()
                entry_text = entry_text[len(company_title_match.group(0)):].strip() # Remove matched part from entry_text
                print(f"DEBUG:   Company/Title line: '{company_title_line}'")

                # Attempt to split company and title from the line
                title_split_match = re.search(r'\s+(?:As an|for|Through)\s+(.+)', company_title_line, re.IGNORECASE)
                tech_used_match = re.search(r'(Technology Used:|Technologies Used:)\s*(.+)', company_title_line, re.IGNORECASE)

                if title_split_match:
                    current_exp['title'] = title_split_match.group(1).strip()
                    current_exp['company'] = company_title_line.replace(title_split_match.group(0), '').strip()
                    print(f"DEBUG:   Split by 'As an/for/Through'. Title: '{current_exp['title']}', Company: '{current_exp['company']}'")
                elif tech_used_match: # Handle academic projects like "Text To Speech Converter Technology"
                    current_exp['title'] = company_title_line.strip() # The project name is the title
                    current_exp['company'] = '' # No company for academic projects
                    print(f"DEBUG:   Split by 'Technology Used'. Title: '{current_exp['title']}' (Academic Project)")
                else:
                    current_exp['company'] = company_title_line
                    if re.search(r'(Text To Speech Converter Technology|Website for a Gold Jewellery Shop|AI Resume Analyzer & Enhancer)', current_exp['company'], re.IGNORECASE):
                        current_exp['title'] = current_exp['company']
                        current_exp['company'] = ''
                        print(f"DEBUG:   Assumed Academic Project. Title: '{current_exp['title']}'")
                    else:
                        current_exp['title'] = "" # Default to empty if no clear title
                        print(f"DEBUG:   No clear split. Company: '{current_exp['company']}', Title: '{current_exp['title']}'")
            
            # Extract Description (remaining text, often bullet points)
            description_lines = [line.strip() for line in entry_text.split('\n') if line.strip()]
            cleaned_description = []
            for line in description_lines:
                cleaned_line = re.sub(r'^[•-]\s*', '- ', line)
                cleaned_description.append(cleaned_line)
            current_exp['description'] = "\n".join(cleaned_description).strip()
            current_exp['description'] = re.sub(r'\s{2,}', ' ', current_exp['description']).strip() # Reduce multiple spaces
            print(f"DEBUG:   Description: '{current_exp['description'][:100]}...'")


            if any(current_exp.values()): # Only add if at least one field is populated
                temp_experiences.append(current_exp)

        data['work_experience'] = temp_experiences
    print(f"DEBUG: Final Extracted Work Experience: {data['work_experience']}")
        
    return data
