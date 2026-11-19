import io, re, json
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

SKILL_BANK = [
"Python","Java","C++","C#","SQL","MySQL","PostgreSQL","MongoDB","Excel","Power BI",
"Tableau","Pandas","NumPy","Scikit-learn","TensorFlow","PyTorch","Machine Learning",
"Deep Learning","NLP","Data Analysis","Statistics","HTML","CSS","JavaScript","React",
"Node.js","Django","Flask","FastAPI","Streamlit","Git","GitHub","AWS","Azure","Docker",
"Linux","REST API","Problem Solving"
]
ROLE_SKILLS = {
"Python Developer":["Python","SQL","Git","REST API","Django","Flask","Problem Solving"],
"Data Analyst":["SQL","Excel","Power BI","Tableau","Python","Pandas","Statistics","Data Analysis"],
"Machine Learning Engineer":["Python","Machine Learning","Scikit-learn","Pandas","NumPy","Statistics","TensorFlow","SQL"],
"AI Engineer":["Python","Machine Learning","Deep Learning","TensorFlow","PyTorch","NLP","REST API"],
"Web Developer":["HTML","CSS","JavaScript","React","Node.js","REST API","Git"],
"Backend Developer":["Python","Java","SQL","REST API","Django","FastAPI","Docker","Git"],
"Data Scientist":["Python","SQL","Pandas","NumPy","Statistics","Machine Learning","Scikit-learn","Data Analysis"],
"Cloud Engineer":["AWS","Azure","Docker","Linux","Git","Python"]
}




def extract_text(data, filename):
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Only PDF and DOCX files are supported.")


def extract_profile_details(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalized = "\n".join(lines)

    email = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        normalized
    )
    phone = re.search(r"\+?\d[\d\s()-]{8,}\d", normalized)
    linkedin = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[^\s]+",
        normalized,
        re.IGNORECASE
    )
    github = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[^\s]+",
        normalized,
        re.IGNORECASE
    )

    section_names = {
        "education": ["education", "academic background"],
        "experience": ["experience", "work experience", "internship"],
        "projects": ["projects", "personal projects", "academic projects"],
        "summary": ["summary", "career objective", "professional summary"]
    }

    sections = {key: [] for key in section_names}
    current_section = None

    for line in lines:
        heading = line.lower().strip(" :")
        matched_section = None

        for key, names in section_names.items():
            if heading in names:
                matched_section = key
                break

        if matched_section:
            current_section = matched_section
            continue

        if heading in ["technical skills", "skills", "certifications"]:
            current_section = None
            continue

        if current_section:
            sections[current_section].append(line)

    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0).strip() if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
        "education": sections["education"],
        "experience": sections["experience"],
        "projects": sections["projects"],
        "summary": " ".join(sections["summary"])
    }




def extract_profile_details(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalized = "\n".join(lines)

    email = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        normalized
    )
    phone = re.search(r"\+?\d[\d\s()-]{8,}\d", normalized)
    linkedin = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[^\s]+",
        normalized,
        re.IGNORECASE
    )
    github = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[^\s]+",
        normalized,
        re.IGNORECASE
    )

    section_names = {
        "education": ["education", "academic background"],
        "experience": ["experience", "work experience", "internship"],
        "projects": ["projects", "personal projects", "academic projects"],
        "summary": ["summary", "career objective", "professional summary"]
    }

    sections = {key: [] for key in section_names}
    current_section = None

    for line in lines:
        heading = line.lower().strip(" :")
        matched_section = None

        for key, names in section_names.items():
            if heading in names:
                matched_section = key
                break

        if matched_section:
            current_section = matched_section
            continue

        if heading in ["technical skills", "skills", "certifications"]:
            current_section = None
            continue

        if current_section:
            sections[current_section].append(line)

    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0).strip() if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
        "education": sections["education"],
        "experience": sections["experience"],
        "projects": sections["projects"],
        "summary": " ".join(sections["summary"])
    }


  
def analyze_resume(data, filename):
    text = extract_text(data, filename)
    if not text.strip():
        raise ValueError("No selectable text was found. Scanned PDFs need OCR; this starter version supports text-based PDFs.")
    normalized = re.sub(r"\s+", " ", text)
    lower = normalized.lower()
    skills = sorted({s for s in SKILL_BANK if re.search(r"(?<![a-z0-9])" + re.escape(s.lower()) + r"(?![a-z0-9])", lower)})
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", normalized)
    name = next((line.strip() for line in text.splitlines() if line.strip() and "@" not in line and len(line.strip()) < 65), "")
    matches = []
    for role, required in ROLE_SKILLS.items():
        present = [s for s in required if s in skills]
        missing = [s for s in required if s not in skills]
        role_text = " ".join(required)
        try:
            matrix = TfidfVectorizer().fit_transform([normalized, role_text])
            similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        except ValueError:
            similarity = 0.0
        coverage = len(present) / max(len(required),1)
        score = round(min(100, (coverage * 0.75 + similarity * 0.25) * 100))
        matches.append({"role":role,"score":score,"matched_skills":present,"missing_skills":missing})
    matches.sort(key=lambda x:x["score"], reverse=True)
   
    profile_details = extract_profile_details(text)

    profile = {
        "name": name,
        "email": profile_details["email"],
        "phone": profile_details["phone"],
        "linkedin": profile_details["linkedin"],
        "github": profile_details["github"],
        "summary": profile_details["summary"] or normalized[:1200],
        "education": profile_details["education"],
        "experience": profile_details["experience"],
        "projects": profile_details["projects"]
    }

   
    profile_details = extract_profile_details(text)

    profile = {
        "name": name,
        "email": profile_details["email"],
        "phone": profile_details["phone"],
        "linkedin": profile_details["linkedin"],
        "github": profile_details["github"],
        "summary": profile_details["summary"] or normalized[:1200],
        "education": profile_details["education"],
        "experience": profile_details["experience"],
        "projects": profile_details["projects"]
    }

    return {
        "filename": filename,
        "profile": profile,
        "skills": skills,
        "matches": matches,
        "resume_text": normalized[:12000]
    }
