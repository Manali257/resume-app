"""
Resume Tailoring & Job Tracker - Manali Jiwane
Streamlit app: JD matching, resume generation, job tracker
"""
import streamlit as st
import json
import os
import io
from datetime import date
from urllib.parse import quote_plus

st.set_page_config(page_title="Resume Tailor – Manali Jiwane", page_icon="📄", layout="wide")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🔍 JD Matcher", "📄 Generate Resume", "🌐 Job Search", "📋 Job Tracker"],
)

# ── PROFILE DATA ──────────────────────────────────────────────────────────────
PROFILE = {
    "name": "Manali Jiwane",
    "email": "manali.jiwane@email.com",
    "phone": "+91-XXXXXXXXXX",
    "location": "Mumbai, India",
    "linkedin": "linkedin.com/in/manali-jiwane",
    "summary": (
        "Java Backend Developer with 4+ years of experience in Spring Boot "
        "microservices, REST APIs, and cloud-native applications. "
        "Skilled in AWS, Pega, and mainframe modernization."
    ),
    "skills": [
        "Java", "Spring Boot", "Spring MVC", "Microservices",
        "REST API", "Hibernate", "JPA", "Maven", "Git",
        "AWS", "Docker", "Kafka", "MySQL", "PostgreSQL",
        "Pega PRPC", "JUnit", "Mockito", "CI/CD", "Agile",
    ],
    "experience": [
        {
            "title": "Software Engineer",
            "company": "Current Company",
            "duration": "2021 – Present",
            "bullets": [
                "Built Spring Boot microservices for AWS Mainframe Modernization test automation.",
                "Developed REST APIs consumed by 3+ downstream systems.",
                "Reduced regression test time by 40% via automated test harness.",
                "Collaborated with Pega team to integrate modernization agent workflows.",
            ],
        }
    ],
    "projects": [
        {
            "id": "mainframe",
            "name": "AWS Mainframe Modernization Test Automation",
            "tech": "Java, Spring Boot, AWS, JUnit, TestNG",
            "desc": (
                "Automated end-to-end test suite for mainframe modernization pipelines on AWS. "
                "Integrated with CI/CD for nightly regression."
            ),
            "keywords": ["aws", "mainframe", "test", "automation", "spring boot", "java", "ci/cd"],
        },
        {
            "id": "pega",
            "name": "Pega Modernization Agent",
            "tech": "Pega PRPC, Java, REST API",
            "desc": (
                "Built a Pega-based agent to orchestrate legacy-to-modern migration workflows, "
                "reducing manual effort by 60%."
            ),
            "keywords": ["pega", "modernization", "agent", "java", "rest", "workflow"],
        },
    ],
    "education": "B.E. Computer Engineering – University, Year",
    "certifications": ["AWS Certified Developer – Associate (in progress)"],
}

TARGET_ROLES = ["Java Backend Developer", "Java Full Stack Developer", "Spring Boot Microservices Engineer"]
LOCATIONS = ["Mumbai", "Pune", "Bengaluru", "Remote"]
SALARY_RANGE = "₹10–20 LPA"

TRACKER_PATH = os.path.join(os.path.dirname(__file__), "tracker.json")

def load_tracker():
    if os.path.exists(TRACKER_PATH):
        with open(TRACKER_PATH) as f:
            return json.load(f)
    return []

def save_tracker(data):
    with open(TRACKER_PATH, "w") as f:
        json.dump(data, f, indent=2)

# ── WEIGHTED JD MATCHING ──────────────────────────────────────────────────────
SKILL_WEIGHTS = {
    "Java": 3, "Spring Boot": 3, "Microservices": 3, "REST API": 2,
    "Spring MVC": 2, "Hibernate": 2, "JPA": 2, "AWS": 2,
    "Docker": 2, "Kafka": 2, "Pega PRPC": 2, "CI/CD": 2,
    "MySQL": 1, "PostgreSQL": 1, "Maven": 1, "Git": 1,
    "JUnit": 1, "Mockito": 1, "Agile": 1,
}

def score_jd(jd_text):
    jd_lower = jd_text.lower()
    matched, missed = [], []
    total_weight = sum(SKILL_WEIGHTS.values())
    earned = 0
    for skill in PROFILE["skills"]:
        w = SKILL_WEIGHTS.get(skill, 1)
        if skill.lower() in jd_lower:
            matched.append(skill)
            earned += w
        else:
            missed.append(skill)
    return int(earned / total_weight * 100), matched, missed

def select_projects(jd_text):
    jd_lower = jd_text.lower()
    ranked = sorted(
        [(sum(1 for kw in p["keywords"] if kw in jd_lower), p) for p in PROFILE["projects"]],
        reverse=True
    )
    return [p for hits, p in ranked if hits > 0]

# ── RESUME TEXT ───────────────────────────────────────────────────────────────
def build_resume_text(jd_text, chosen_projects):
    _, matched, _ = score_jd(jd_text) if jd_text.strip() else (0, [], [])
    skills = matched + [s for s in PROFILE["skills"] if s not in matched]
    lines = [
        PROFILE["name"],
        f"{PROFILE['email']}  |  {PROFILE['phone']}  |  {PROFILE['location']}",
        PROFILE["linkedin"], "",
        "SUMMARY", "-------", PROFILE["summary"], "",
        "SKILLS", "------", ", ".join(skills), "",
        "EXPERIENCE", "----------",
    ]
    for exp in PROFILE["experience"]:
        lines += [f"{exp['title']} – {exp['company']} ({exp['duration']})"]
        lines += [f"  • {b}" for b in exp["bullets"]]
        lines.append("")
    if chosen_projects:
        lines += ["PROJECTS", "--------"]
        for p in chosen_projects:
            lines += [f"{p['name']}  |  {p['tech']}", f"  {p['desc']}", ""]
    lines += ["EDUCATION", "---------", PROFILE["education"], "",
              "CERTIFICATIONS", "--------------"] + PROFILE["certifications"]
    return "\n".join(lines)

# ── PDF RESUME ────────────────────────────────────────────────────────────────
def build_resume_pdf(jd_text, chosen_projects):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.enums import TA_CENTER

        _, matched, _ = score_jd(jd_text) if jd_text.strip() else (0, [], [])
        skills = matched + [s for s in PROFILE["skills"] if s not in matched]

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=15*mm, bottomMargin=15*mm)

        BLUE = colors.HexColor("#1a237e")
        name_s = ParagraphStyle("n", fontSize=18, fontName="Helvetica-Bold",
                                alignment=TA_CENTER, spaceAfter=2)
        contact_s = ParagraphStyle("c", fontSize=9, alignment=TA_CENTER, spaceAfter=6)
        sec_s = ParagraphStyle("s", fontSize=11, fontName="Helvetica-Bold",
                               spaceBefore=10, spaceAfter=3, textColor=BLUE)
        body_s = ParagraphStyle("b", fontSize=9, spaceAfter=2, leading=13)
        bul_s = ParagraphStyle("bl", fontSize=9, spaceAfter=2, leading=13, leftIndent=12)

        story = [
            Paragraph(PROFILE["name"], name_s),
            Paragraph(f"{PROFILE['email']}  •  {PROFILE['phone']}  •  "
                      f"{PROFILE['location']}  •  {PROFILE['linkedin']}", contact_s),
            HRFlowable(width="100%", thickness=1, color=BLUE),
        ]

        def sec(title):
            story.append(Paragraph(title, sec_s))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))

        sec("SUMMARY"); story.append(Paragraph(PROFILE["summary"], body_s))
        sec("SKILLS"); story.append(Paragraph(", ".join(skills), body_s))
        sec("EXPERIENCE")
        for exp in PROFILE["experience"]:
            story.append(Paragraph(
                f"<b>{exp['title']} – {exp['company']}</b>  ({exp['duration']})", body_s))
            for b in exp["bullets"]:
                story.append(Paragraph(f"• {b}", bul_s))
            story.append(Spacer(1, 4))
        if chosen_projects:
            sec("PROJECTS")
            for p in chosen_projects:
                story.append(Paragraph(f"<b>{p['name']}</b>  |  <i>{p['tech']}</i>", body_s))
                story.append(Paragraph(p["desc"], bul_s))
                story.append(Spacer(1, 4))
        sec("EDUCATION"); story.append(Paragraph(PROFILE["education"], body_s))
        sec("CERTIFICATIONS")
        for c in PROFILE["certifications"]:
            story.append(Paragraph(f"• {c}", bul_s))

        doc.build(story)
        buf.seek(0)
        return buf.getvalue(), None
    except ImportError:
        return None, "missing"

# ── JOB PORTAL URLS ───────────────────────────────────────────────────────────
def job_urls(role, location):
    r, l = quote_plus(role), quote_plus(location)
    sr = quote_plus(role.lower().replace(" ", "-"))
    sl = quote_plus(location.lower())
    return {
        "Naukri":     f"https://www.naukri.com/{sr}-jobs-in-{sl}",
        "LinkedIn":   f"https://www.linkedin.com/jobs/search/?keywords={r}&location={l}",
        "Indeed":     f"https://www.indeed.co.in/jobs?q={r}&l={l}",
        "Shine":      f"https://www.shine.com/job-search/{sr}-jobs-in-{sl}",
        "Glassdoor":  f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={r}&locKeyword={l}",
        "Instahyre":  f"https://www.instahyre.com/search-jobs/?q={r}&location={l}",
        "Wellfound":  f"https://wellfound.com/jobs?q={r}&l={l}",
    }

# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Home":
    st.title("📄 Resume Tailor")
    st.subheader(PROFILE["name"])
    st.write(f"**Target roles:** {', '.join(TARGET_ROLES)}")
    st.write(f"**Locations:** {', '.join(LOCATIONS)}  |  **Salary:** {SALARY_RANGE}")
    st.markdown("---")
    st.write("- 🔍 **JD Matcher** – weighted score + gap analysis")
    st.write("- 📄 **Generate Resume** – tailored PDF or TXT download")
    st.write("- 🌐 **Job Search** – one-click Naukri, LinkedIn, Indeed & more")
    st.write("- 📋 **Job Tracker** – log every application")

elif page == "🔍 JD Matcher":
    st.title("🔍 JD Match Score")
    jd = st.text_area("Paste the Job Description here", height=300)
    if st.button("Analyse Match") and jd.strip():
        score, matched, missed = score_jd(jd)
        projects = select_projects(jd)

        c1, c2, c3 = st.columns(3)
        c1.metric("Weighted Match", f"{score}%")
        c2.metric("Skills Matched", f"{len(matched)} / {len(PROFILE['skills'])}")
        c3.metric("Skill Gaps", len(missed))

        if score >= 70:
            st.success("Strong match – apply now!")
        elif score >= 40:
            st.warning("Moderate match – highlight matched skills.")
        else:
            st.error("Low match – consider skipping or upskilling first.")

        ca, cb = st.columns(2)
        with ca:
            st.markdown("**✅ Matched:**")
            st.write(", ".join(matched) or "None")
        with cb:
            st.markdown("**❌ Gaps:**")
            st.write(", ".join(missed) or "None – perfect!")

        st.markdown("**📌 Projects to highlight:**")
        for p in projects:
            st.write(f"- {p['name']}")
        if not projects:
            st.write("No strong project match.")

elif page == "📄 Generate Resume":
    st.title("📄 Generate Tailored Resume")
    jd = st.text_area("Paste Job Description (improves skill ordering)", height=200)
    selected_ids = [p["id"] for p in PROFILE["projects"]
                    if st.checkbox(p["name"], value=True, key=p["id"])]
    chosen = [p for p in PROFILE["projects"] if p["id"] in selected_ids]

    if st.button("Generate"):
        resume_text = build_resume_text(jd, chosen)
        st.text_area("Preview", resume_text, height=400)
        c1, c2 = st.columns(2)
        c1.download_button("⬇ Download .txt", data=resume_text,
                           file_name="Manali_Jiwane_Resume.txt", mime="text/plain")
        pdf_bytes, err = build_resume_pdf(jd, chosen)
        if pdf_bytes:
            c2.download_button("⬇ Download PDF", data=pdf_bytes,
                               file_name="Manali_Jiwane_Resume.pdf", mime="application/pdf")
        else:
            c2.info("PDF needs reportlab: `python -m pip install reportlab`")

elif page == "🌐 Job Search":
    st.title("🌐 Search Jobs on Portals")
    c1, c2 = st.columns(2)
    role = c1.selectbox("Role", TARGET_ROLES + ["Custom"])
    if role == "Custom":
        role = c1.text_input("Enter custom role")
    location = c2.selectbox("Location", LOCATIONS + ["All India"])

    if role:
        urls = job_urls(role, location)
        st.markdown(f"**Searching:** `{role}` in `{location}`")
        cols = st.columns(4)
        for i, (name, url) in enumerate(urls.items()):
            cols[i % 4].link_button(f"🔗 {name}", url)
        st.markdown("---")
        for name, url in urls.items():
            st.markdown(f"- [{name}]({url})")

elif page == "📋 Job Tracker":
    st.title("📋 Job Application Tracker")
    tracker = load_tracker()

    with st.expander("➕ Add Application"):
        with st.form("add_job"):
            c1, c2 = st.columns(2)
            company = c1.text_input("Company")
            role = c2.text_input("Role")
            portal = c1.selectbox("Portal", ["Naukri", "LinkedIn", "Indeed", "Shine",
                                             "Glassdoor", "Instahyre", "Wellfound", "Other"])
            location = c2.selectbox("Location", LOCATIONS + ["Other"])
            status = c1.selectbox("Status", ["Applied", "Interview", "Offer", "Rejected", "Withdrawn"])
            applied_on = c2.date_input("Applied On", value=date.today())
            job_url_input = st.text_input("Job URL (optional)")
            notes = st.text_area("Notes")
            if st.form_submit_button("Add") and company and role:
                tracker.append({
                    "company": company, "role": role, "portal": portal,
                    "location": location, "status": status,
                    "applied_on": str(applied_on), "job_url": job_url_input, "notes": notes,
                })
                save_tracker(tracker)
                st.success("Added!")
                st.rerun()

    if tracker:
        st.markdown(f"**Total: {len(tracker)} applications**")
        counts = {}
        for j in tracker:
            counts[j["status"]] = counts.get(j["status"], 0) + 1
        cols = st.columns(len(counts))
        for i, (s, c) in enumerate(counts.items()):
            cols[i].metric(s, c)
        st.markdown("---")
        filt = st.multiselect("Filter by status",
                              ["Applied", "Interview", "Offer", "Rejected", "Withdrawn"],
                              default=["Applied", "Interview", "Offer"])
        for job in [j for j in tracker if j["status"] in filt]:
            cols = st.columns([3, 3, 2, 2, 2, 1])
            cols[0].write(job["company"])
            cols[1].write(job["role"])
            cols[2].write(job.get("portal", ""))
            cols[3].write(job["location"])
            cols[4].write(job["status"])
            cols[5].write(job["applied_on"])
            if job.get("job_url"):
                st.caption(f"   ↳ [View Job]({job['job_url']})")
            if job.get("notes"):
                st.caption(f"   ↳ {job['notes']}")
    else:
        st.info("No applications yet. Add your first one above!")
