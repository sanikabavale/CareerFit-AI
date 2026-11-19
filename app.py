
import sys
import getpass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_connection
from database.auth import _hash_password
import streamlit as st
from database.db import init_db
from database.auth import authenticate, register_user, get_user_by_id
from database.repositories import get_analysis_history
from utils.ui import apply_theme
from utils.analysis import analyze_resume
from utils.reports import create_pdf_report
from pathlib import Path
import json

st.set_page_config(page_title="CareerFit AI", page_icon="✦", layout="wide")
init_db()
apply_theme()

if "user" not in st.session_state:
    st.session_state.user = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None

def logout():
    st.session_state.user = None
    st.session_state.analysis = None
    st.rerun()

def login_screen():
    st.markdown("<div class='hero'><div class='eyebrow'>CAREER INTELLIGENCE PLATFORM</div><h1>CareerFit <span>AI</span></h1><p>Discover Your Skills. Find Your Fit.</p></div>", unsafe_allow_html=True)
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("### Turn your resume into a career direction.")
        st.write("Understand your skills, explore matching roles, identify skill gaps and build a practical learning roadmap.")
        st.markdown("- Resume insights and candidate profile\n- Job-role matching and recommendations\n- Skill-gap analysis and learning roadmap\n- Downloadable career report")
    with right:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        mode = st.radio("Account", ["Login", "Create account"], horizontal=True)
        if mode == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                user, message = authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error(message)
        else:
            username = st.text_input("Choose username")
            email = st.text_input("Email")
            password = st.text_input("Create password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            if st.button("Request access", use_container_width=True):
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, message = register_user(username, email, password)
                    (st.success if ok else st.error)(message)
                    if ok:
                        st.info("Your account is pending admin approval. You can log in after approval.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Resume information is used for career-related analysis. Do not upload documents containing information you do not want processed.")

if not st.session_state.user:
    login_screen()
    st.stop()

user = get_user_by_id(st.session_state.user["id"])
if not user or user["status"] != "approved":
    st.session_state.user = None
    st.error("This account is not currently approved. Contact the administrator.")
    st.stop()

with st.sidebar:
    st.markdown("## ✦ CareerFit AI")
    st.caption(f"Signed in as **{user['username']}** · {user['role'].title()}")
    pages = [
    "Overview",
    "Resume Analyzer",
    "My Profile",
    "Job Recommendations",
    "Skill Gap Analysis",
    "Career Roadmap",
    "Analytics",
    "Reports",
    "History"
]
    if user["role"] == "admin":
        pages += ["Admin Panel"]
    page = st.radio("NAVIGATION", pages)
    st.button("Log out", on_click=logout, use_container_width=True)

st.title(page)

if page == "Overview":
    import pandas as pd

    records = get_analysis_history(user["id"])
    r = st.session_state.analysis

    st.markdown("""
    <style>
    .welcome-card {
        background: linear-gradient(115deg, #102c55, #10213c, #07172c);
        border: 1px solid #176b9e;
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 22px;
        box-shadow: 0 8px 30px rgba(0, 180, 255, .10);
    }
    .welcome-title {
        font-size: 30px;
        font-weight: 800;
        color: #f1f8ff;
    }
    .welcome-sub {
        color: #9cc9ed;
        font-size: 15px;
        margin-top: 7px;
    }
    .section-title {
        color: #53dafa;
        font-size: 20px;
        font-weight: 700;
        margin: 18px 0 12px 0;
    }
    .glass-card {
        background: linear-gradient(145deg, #142943, #0d1c31);
        border: 1px solid #254b70;
        border-radius: 16px;
        padding: 18px;
        min-height: 112px;
    }
    .card-label {
        color: #a9c2dc;
        font-size: 13px;
    }
    .card-value {
        color: #40dafa;
        font-size: 29px;
        font-weight: 800;
        margin-top: 8px;
    }
    .mini-card {
        background: #10243c;
        border: 1px solid #245477;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Welcome section
    st.markdown(f"""
    <div class="welcome-card">
        <div class="welcome-title">Welcome back, {user['username']} ✦</div>
        <div class="welcome-sub">
            Your career journey starts with understanding your potential.
            Explore your skills, discover opportunities and grow with CareerFit AI.
        </div>
    </div>
    """, unsafe_allow_html=True)

    skills = r.get("skills", []) if r else []
    matches = r.get("matches", []) if r else []
    top = matches[0] if matches else {}

    # Statistics
    st.markdown('<div class="section-title">✦ Your Career Snapshot</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    stats = [
        ("Resume Analyses", len(records)),
        ("Skills Identified", len(skills)),
        ("Career Roles", len(matches)),
        ("Top Match", f"{top.get('score', 0)}%" if top else "—")
    ]

    for col, (label, value) in zip([c1, c2, c3, c4], stats):
        with col:
            st.markdown(f"""
            <div class="glass-card">
                <div class="card-label">{label}</div>
                <div class="card-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    # Main dashboard columns
    left, right = st.columns([1.35, 1])

    with left:
        st.markdown('<div class="section-title">✦ Top Career Opportunities</div>',
                    unsafe_allow_html=True)

        if matches:
            for i, item in enumerate(matches[:4], 1):
                st.markdown(f"""
                <div class="mini-card">
                    <span style="color:#48dcfa;font-weight:700">
                        #{i} &nbsp; {item['role']}
                    </span>
                    <span style="float:right;color:#ffffff;font-weight:700">
                        {item['score']}%
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Analyze your resume to discover suitable career roles.")

    with right:
        st.markdown('<div class="section-title">✦ Career Match</div>',
                    unsafe_allow_html=True)

        if top:
            st.metric("Best matching role", top["role"])
            st.progress(top["score"] / 100)
            st.caption(f"Estimated match: {top['score']}%")
        else:
            st.info("Your career match will appear after resume analysis.")

    # Skills section
    st.markdown('<div class="section-title">✦ Your Skill Universe</div>',
                unsafe_allow_html=True)

    if skills:
        skill_columns = st.columns(4)
        for i, skill in enumerate(skills):
            with skill_columns[i % 4]:
                st.markdown(f"""
                <div class="mini-card" style="text-align:center;color:#bcefff">
                    ✧ {skill}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Your extracted skills will appear here after analysis.")

    # Match analytics
    st.markdown('<div class="section-title">✦ Role Match Analytics</div>',
                unsafe_allow_html=True)

    if matches:
        chart_data = pd.DataFrame(matches)[["role", "score"]]
        chart_data = chart_data.set_index("role")
        st.bar_chart(chart_data, height=280)
        st.caption("Scores are estimated skill-based matches, not hiring probabilities.")
    else:
        st.info("Complete your first resume analysis to unlock career analytics.")

    # Skill gap and recent activity
    gap_col, activity_col = st.columns(2)

    with gap_col:
        st.markdown('<div class="section-title">✦ Skills to Develop</div>',
                    unsafe_allow_html=True)

        if top:
            missing = top.get("missing_skills", [])
            if missing:
                for skill in missing[:6]:
                    st.markdown(f"""
                    <div class="mini-card">
                        <span style="color:#ffd38b">＋ {skill}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Great! No skill gaps in the current role skill map.")
        else:
            st.caption("Analyze a resume to see your skill gaps.")

    with activity_col:
        st.markdown('<div class="section-title">✦ Recent Activity</div>',
                    unsafe_allow_html=True)

        if records:
            for rec in records[:5]:
                st.markdown(f"""
                <div class="mini-card">
                    <div style="color:#d9efff;font-weight:600">
                        📄 {rec['filename']}
                    </div>
                    <div style="color:#8baac7;font-size:12px">
                        {rec['created_at']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Your recent resume analyses will appear here.")

    st.markdown("""
    <div style="text-align:center;padding:25px;color:#7296b8">
        ✦ CareerFit AI · Discover Your Skills. Find Your Fit.
    </div>
    """, unsafe_allow_html=True)


elif page == "Resume Analyzer":
    import html
    import pandas as pd
    import plotly.express as px

    st.markdown("""
    <style>
    .ra-hero {
        background: linear-gradient(120deg, #102747, #101D35, #123C62);
        border: 1px solid #24517C;
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
    }
    .ra-hero h1 {
        color: #FFFFFF;
        font-size: 30px;
        margin-bottom: 8px;
    }
    .ra-hero p {
        color: #A9C8E8;
        font-size: 14px;
    }
    .ra-card {
        background: linear-gradient(145deg, #172D49, #101D30);
        border: 1px solid #284866;
        border-radius: 16px;
        padding: 19px;
        margin-bottom: 14px;
    }
    .ra-label {
        color: #9CB5D1;
        font-size: 12px;
        letter-spacing: 1px;
    }
    .ra-value {
        color: #67E8C0;
        font-size: 28px;
        font-weight: bold;
        margin-top: 7px;
    }
    .ra-section {
        color: #EAF3FF;
        font-size: 21px;
        font-weight: bold;
        margin-top: 26px;
        margin-bottom: 14px;
    }
    .ra-skill {
        display: inline-block;
        background: #203B5A;
        color: #8DE8F0;
        border: 1px solid #315A7B;
        border-radius: 20px;
        padding: 7px 13px;
        margin: 4px;
        font-size: 13px;
    }
    .ra-upload {
        background: linear-gradient(145deg, #142943, #101D30);
        border: 1px dashed #21C7D9;
        border-radius: 17px;
        padding: 22px;
        text-align: center;
        margin-bottom: 15px;
    }
    .ra-upload h3 {
        color: #EAF3FF;
    }
    .ra-upload p {
        color: #9CB5D1;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ra-hero">
        <h1>✦ AI Resume Intelligence</h1>
        <p>Transform your resume into career insights with intelligent analysis.</p>
        <p>Discover your strengths · Explore job matches · Identify your potential</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="ra-section">01 · Upload Your Resume</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="ra-upload">
        <h3>📄 Start Your Resume Analysis</h3>
        <p>Upload your professional resume in PDF or DOCX format.</p>
        <p>Our analyzer will extract your skills and identify suitable career roles.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Choose your resume",
        type=["pdf", "docx"],
        key="resume_analyzer_upload"
    )

    if uploaded:
        file_size = uploaded.size / 1024

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"""
            <div class="ra-card">
                <div class="ra-label">SELECTED FILE</div>
                <div style="color:white;font-size:16px;font-weight:bold;margin-top:8px;">
                    📄 {html.escape(uploaded.name)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="ra-card">
                <div class="ra-label">FILE SIZE</div>
                <div class="ra-value">{file_size:.1f} KB</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button(
            "✦ Analyze My Resume",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Analyzing your resume and discovering career opportunities..."):
                try:
                    result = analyze_resume(
                        uploaded.getvalue(),
                        uploaded.name
                    )

                    from database.repositories import save_analysis

                    analysis_id = save_analysis(
                        user["id"],
                        uploaded.name,
                        result
                    )

                    result["analysis_id"] = analysis_id
                    st.session_state.analysis = result

                    st.success("Resume analyzed and saved successfully!")
                    st.rerun()

                except Exception as exc:
                    st.error(f"Could not analyze this file: {exc}")

    else:
        st.info("Upload your resume above to begin your analysis.")

    # Display the latest analysis
    result = st.session_state.analysis

    if result:
        profile = result.get("profile", {})
        skills = result.get("skills", [])
        matches = result.get("matches", [])

        top_match = max(
            matches,
            key=lambda item: float(item.get("score", 0)),
            default=None
        )

        top_score = float(top_match.get("score", 0)) if top_match else 0
        top_role = top_match.get("role", "Not available") if top_match else "Not available"

        st.markdown(
            '<div class="ra-section">02 · Analysis Overview</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)

        metrics = [
            (c1, "SKILLS IDENTIFIED", len(skills)),
            (c2, "CAREER MATCHES", len(matches)),
            (c3, "TOP MATCH SCORE", f"{top_score:.0f}%")
        ]

        for col, label, value in metrics:
            with col:
                st.markdown(f"""
                <div class="ra-card">
                    <div class="ra-label">{label}</div>
                    <div class="ra-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(
            '<div class="ra-section">03 · Candidate Profile Preview</div>',
            unsafe_allow_html=True
        )

        candidate_name = profile.get("name") or "Candidate Profile"
        candidate_email = profile.get("email") or "Email not detected"

        st.markdown(f"""
        <div class="ra-card">
            <div class="ra-label">CANDIDATE PROFILE</div>
            <div style="color:white;font-size:26px;font-weight:bold;margin-top:10px;">
                {html.escape(str(candidate_name))}
            </div>
            <div style="color:#A9C8E8;margin-top:5px;">
                {html.escape(str(candidate_email))}
            </div>
            <div style="color:#67E8C0;margin-top:15px;font-size:13px;">
                ✦ Recommended Career: {html.escape(str(top_role))}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="ra-section">04 · Your Extracted Skills</div>',
            unsafe_allow_html=True
        )

        if skills:
            skill_html = "".join(
                f'<span class="ra-skill">{html.escape(str(skill))}</span>'
                for skill in skills
            )
            st.markdown(skill_html, unsafe_allow_html=True)
        else:
            st.info("No skills detected. Try a text-based PDF or DOCX.")

        st.markdown(
            '<div class="ra-section">05 · Career Match Intelligence</div>',
            unsafe_allow_html=True
        )

        if matches:
            left, right = st.columns([1, 1.4])

            with left:
                st.markdown("**Your Best Career Match**")

                fig = px.pie(
                    names=["Match", "Remaining"],
                    values=[top_score, max(0, 100 - top_score)],
                    hole=0.76
                )

                fig.update_traces(
                    marker=dict(colors=["#21C7D9", "#203B5A"]),
                    textinfo="none"
                )

                fig.update_layout(
                    annotations=[dict(
                        text=f"<b>{top_score:.0f}%</b>",
                        x=0.5,
                        y=0.5,
                        font_size=25,
                        font_color="white",
                        showarrow=False
                    )],
                    showlegend=False,
                    height=250,
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(fig, use_container_width=True)

                st.markdown(f"**{top_role}**")

            with right:
                st.markdown("**Top Recommended Roles**")

                chart_data = pd.DataFrame([
                    {
                        "Role": item.get("role", "Unknown"),
                        "Match Score": float(item.get("score", 0))
                    }
                    for item in matches
                ])

                chart_data = chart_data.sort_values("Match Score")

                fig = px.bar(
                    chart_data,
                    x="Match Score",
                    y="Role",
                    orientation="h",
                    text="Match Score"
                )

                fig.update_traces(
                    marker_color="#21C7D9",
                    texttemplate="%{text:.0f}%",
                    textposition="outside"
                )

                fig.update_layout(
                    height=max(280, len(matches) * 45),
                    xaxis=dict(range=[0, 110]),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#DCEBFA",
                    margin=dict(t=10, b=10, l=5, r=35)
                )

                st.plotly_chart(fig, use_container_width=True)

            st.markdown("**Detailed Job Matches**")

            st.dataframe(
                matches,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No job-role matches were generated.")

        st.caption(
            "Match scores are estimates based on resume skills and the available role dataset, not hiring probabilities."
        )


elif page == "My Profile":
    r = st.session_state.analysis

    if r:
        p = r["profile"]
        skills = r.get("skills", [])
        matches = r.get("matches", [])
        top_match = matches[0] if matches else {}
        
        st.markdown("""
        <style>
        .profile-card {
            background: linear-gradient(135deg, #10284b, #09172e);
            border: 1px solid #168bd0;
            border-radius: 20px;
            padding: 26px;
            margin-bottom: 18px;
            box-shadow: 0 0 22px rgba(0, 190, 255, 0.10);
        }
        .profile-name {
            color: #e8f6ff;
            font-size: 28px;
            font-weight: 700;
        }
        .profile-role {
            color: #35d9f5;
            font-size: 15px;
        }
        .skill-tag {
            display: inline-block;
            background: #103d59;
            border: 1px solid #13b9d5;
            color: #baf5ff;
            border-radius: 18px;
            padding: 7px 13px;
            margin: 4px;
            font-size: 13px;
        }
        .section-card {
            background: #101f36;
            border: 1px solid #23496d;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 14px;
        }
        .section-heading {
            color: #42dafa;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 12px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Candidate header
        left, right = st.columns([3, 1])

        with left:
            st.markdown(f"""
            <div class="profile-card">
                <div class="profile-name">
                    {p.get('name') or 'Candidate Profile'}
                </div>
                <div class="profile-role">
                    {top_match.get('role', 'Career Profile')}
                </div>
                <br>
                <div>✉️ {p.get('email') or 'Email not available'}</div>
                <div>☎️ {p.get('phone') or 'Phone not available'}</div>
                <div>🔗 {p.get('linkedin') or 'LinkedIn not available'}</div>
                <div>💻 {p.get('github') or 'GitHub not available'}</div>
            </div>
            """, unsafe_allow_html=True)

        with right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("### Overall Match")
            st.markdown(
                f"<h1 style='color:#32dafa;text-align:center'>"
                f"{top_match.get('score', 0)}%</h1>",
                unsafe_allow_html=True
            )
            st.caption("Top recommended role")
            st.markdown('</div>', unsafe_allow_html=True)

        # Summary
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">✦ Professional Summary</div>',
                    unsafe_allow_html=True)
        st.write(p.get("summary") or "Summary not available in resume.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Skills
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">✦ Technical Skills</div>',
                    unsafe_allow_html=True)

        if skills:
            skill_html = "".join(
                f'<span class="skill-tag">{skill}</span>'
                for skill in skills
            )
            st.markdown(skill_html, unsafe_allow_html=True)
        else:
            st.info("No skills detected.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Skill match
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">✦ Skill Match</div>',
                    unsafe_allow_html=True)

        if top_match:
            matched = top_match.get("matched_skills", [])
            missing = top_match.get("missing_skills", [])

            for skill in matched:
                st.write(f"**{skill}**")
                st.progress(1.0)

            for skill in missing:
                st.write(f"**{skill}** — To develop")
                st.progress(0.0)
        else:
            st.info("No role match available.")

        st.markdown('</div>', unsafe_allow_html=True)

        # Education, experience and projects
        sections = [
            ("Education", p.get("education", [])),
            ("Experience", p.get("experience", [])),
            ("Projects", p.get("projects", []))
        ]

        for heading, items in sections:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-heading">✦ {heading}</div>',
                unsafe_allow_html=True
            )
            if items:
                for item in items:
                    st.write("• " + item)
            else:
                st.caption(f"{heading} details not detected in resume.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Profile insights
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">✦ Profile Insights</div>',
                    unsafe_allow_html=True)
        st.write(f"**Skills detected:** {len(skills)}")
        st.write(f"**Recommended role:** {top_match.get('role', 'Not available')}")
        st.write(f"**Skills matched:** {len(top_match.get('matched_skills', []))}")
        st.write(f"**Skills to develop:** {len(top_match.get('missing_skills', []))}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Analyze a resume first to preview your candidate profile.")


elif page == "Job Recommendations":
    r = st.session_state.analysis

    st.markdown("""
    <style>
    .job-hero {
        background: linear-gradient(120deg, #102747, #101D35, #123C62);
        border: 1px solid #24517C;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 22px;
    }
    .job-hero h1 {
        color: white;
        font-size: 29px;
    }
    .job-hero p {
        color: #A9C8E8;
    }
    .job-card {
        background: linear-gradient(145deg, #172D49, #101D30);
        border: 1px solid #284866;
        border-radius: 16px;
        padding: 19px;
        margin-bottom: 14px;
    }
    .job-title {
        color: #F0F6FF;
        font-size: 19px;
        font-weight: 700;
    }
    .job-score {
        color: #67E8C0;
        font-size: 27px;
        font-weight: bold;
    }
    .job-muted {
        color: #9CB5D1;
        font-size: 12px;
    }
    .job-tag {
        display: inline-block;
        background: #203B5A;
        color: #8DE8F0;
        border: 1px solid #315A7B;
        border-radius: 20px;
        padding: 5px 10px;
        margin: 4px 3px 4px 0;
        font-size: 12px;
    }
    .job-section {
        color: #EAF3FF;
        font-size: 20px;
        font-weight: bold;
        margin-top: 24px;
        margin-bottom: 13px;
    }
    .job-top {
        background: linear-gradient(110deg, #123C52, #142944);
        border: 1px solid #21C7D9;
        border-radius: 17px;
        padding: 22px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="job-hero">
        <h1>✦ AI Job Recommendations</h1>
        <p>Discover career opportunities that align with your resume skills and professional profile.</p>
    </div>
    """, unsafe_allow_html=True)

    if r:
        matches = r.get("matches", [])
        skills = r.get("skills", [])

        if matches:
            ranked = sorted(
                matches,
                key=lambda x: float(x.get("score", 0)),
                reverse=True
            )

            top = ranked[0]
            top_role = top.get("role", "Not available")
            top_score = float(top.get("score", 0))

            st.markdown(
                '<div class="job-section">Your Best Career Match</div>',
                unsafe_allow_html=True
            )

            st.markdown(f"""
            <div class="job-top">
                <div style="color:#8DE8F0;font-size:12px;font-weight:bold;">
                    ✦ TOP RECOMMENDED ROLE
                </div>
                <div style="color:white;font-size:26px;font-weight:bold;margin-top:8px;">
                    {top_role}
                </div>
                <div style="color:#67E8C0;font-size:34px;font-weight:bold;margin-top:8px;">
                    {top_score:.0f}% Match
                </div>
                <div style="color:#B7D0E8;font-size:13px;">
                    Based on the skills detected in your uploaded resume
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Recommended Roles", len(ranked))

            with c2:
                st.metric("Resume Skills", len(skills))

            with c3:
                st.metric(
                    "Top Role Skill Gaps",
                    len(top.get("missing_skills", []))
                )

            st.markdown(
                '<div class="job-section">Explore Your Career Matches</div>',
                unsafe_allow_html=True
            )

            for index, item in enumerate(ranked, 1):
                role = item.get("role", "Unknown Role")
                score = float(item.get("score", 0))
                matched = item.get("matched_skills", [])
                missing = item.get("missing_skills", [])

                with st.container(border=True):
                    left, right = st.columns([3, 1])

                    with left:
                        st.markdown(f"### {index:02d} · {role}")
                        st.caption(
                            f"{len(matched)} matched skills · "
                            f"{len(missing)} skills to develop"
                        )

                    with right:
                        st.markdown(
                            f"<div class='job-score'>{score:.0f}%</div>",
                            unsafe_allow_html=True
                        )
                        st.caption("Estimated match")

                    st.progress(max(0.0, min(1.0, score / 100)))

                    with st.expander("View skill analysis"):
                        st.markdown("**Matched Skills**")

                        if matched:
                            st.markdown(
                                " ".join(
                                    f"`{skill}`" for skill in matched
                                )
                            )
                        else:
                            st.info("No matched skills detected.")

                        st.markdown("**Skills to Develop**")

                        if missing:
                            st.markdown(
                                " ".join(
                                    f"`{skill}`" for skill in missing
                                )
                            )
                        else:
                            st.success("No missing skills in this role map.")

            st.markdown(
                '<div class="job-section">Your Career Insights</div>',
                unsafe_allow_html=True
            )

            st.info(
                f"Your strongest current match is **{top_role}** "
                f"with an estimated skill match of **{top_score:.0f}%**. "
                "Use the Skill Gap Analysis and Career Roadmap pages "
                "to explore areas for further development."
            )

        else:
            st.info("No job recommendations available. Analyze your resume again.")

    else:
        st.info("Analyze your resume first to discover suitable career roles.")

elif page == "Skill Gap Analysis":
    import pandas as pd
    import plotly.express as px

    r = st.session_state.analysis

    st.markdown("""
    <style>
    .gap-hero {
        background: linear-gradient(120deg, #102747, #101D35, #123C62);
        border: 1px solid #24517C;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 22px;
    }
    .gap-hero h1 {
        color: white;
        font-size: 29px;
    }
    .gap-hero p {
        color: #A9C8E8;
        font-size: 14px;
    }
    .gap-card {
        background: linear-gradient(145deg, #172D49, #101D30);
        border: 1px solid #284866;
        border-radius: 15px;
        padding: 19px;
        min-height: 120px;
    }
    .gap-label {
        color: #9CB5D1;
        font-size: 13px;
    }
    .gap-value {
        color: #67E8C0;
        font-size: 29px;
        font-weight: bold;
        margin-top: 8px;
    }
    .gap-section {
        color: #EAF3FF;
        font-size: 20px;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 12px;
    }
    .skill-box {
        background: #142943;
        border: 1px solid #284866;
        border-radius: 12px;
        padding: 13px;
        margin-bottom: 9px;
        color: #EAF3FF;
    }
    .matched-box {
        border-left: 4px solid #67E8C0;
    }
    .missing-box {
        border-left: 4px solid #F6A65A;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="gap-hero">
        <h1>✦ Skill Gap Intelligence</h1>
        <p>Discover your strengths, identify missing skills and build a smarter career learning path.</p>
    </div>
    """, unsafe_allow_html=True)

    if r:
        matches = r.get("matches", [])
        resume_skills = r.get("skills", [])

        if matches:
            role_names = [m.get("role", "Unknown") for m in matches]

            selected = st.selectbox(
                "Select your target career role",
                role_names,
                key="skill_gap_target_role"
            )

            match = next(
                m for m in matches
                if m.get("role") == selected
            )

            score = float(match.get("score", 0))
            matched_skills = match.get("matched_skills", [])
            missing_skills = match.get("missing_skills", [])

            total_skills = len(matched_skills) + len(missing_skills)

            if total_skills:
                calculated_score = (
                    len(matched_skills) / total_skills
                ) * 100
            else:
                calculated_score = score

            st.markdown(
                '<div class="gap-section">Your Skill Performance</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3, c4 = st.columns(4)

            cards = [
                ("Match Score", f"{score:.0f}%", "Estimated role match"),
                ("Matched Skills", str(len(matched_skills)), "Skills already identified"),
                ("Missing Skills", str(len(missing_skills)), "Areas to develop"),
                ("Total Role Skills", str(total_skills), "Skills in role comparison")
            ]

            for col, item in zip([c1, c2, c3, c4], cards):
                with col:
                    st.markdown(f"""
                    <div class="gap-card">
                        <div class="gap-label">{item[0]}</div>
                        <div class="gap-value">{item[1]}</div>
                        <div class="gap-label">{item[2]}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(
                '<div class="gap-section">Skill Match Distribution</div>',
                unsafe_allow_html=True
            )

            left, right = st.columns([1, 1.4])

            with left:
                fig = px.pie(
                    names=["Matched", "Missing"],
                    values=[
                        len(matched_skills),
                        len(missing_skills)
                    ],
                    hole=0.72
                )

                fig.update_traces(
                    marker=dict(
                        colors=["#21C7D9", "#F6A65A"]
                    ),
                    textinfo="none"
                )

                fig.update_layout(
                    annotations=[dict(
                        text=f"<b>{score:.0f}%</b>",
                        x=0.5,
                        y=0.5,
                        font_size=27,
                        font_color="white",
                        showarrow=False
                    )],
                    showlegend=True,
                    legend_font_color="#DCEBFA",
                    height=280,
                    margin=dict(t=15, b=15, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(fig, use_container_width=True)

            with right:
                st.markdown("**Your skill coverage**")

                st.progress(
                    max(0.0, min(1.0, score / 100))
                )

                st.markdown(
                    f"**{len(matched_skills)} matched** out of **{total_skills} role skills**"
                )

                st.caption(
                    "This score is an estimate from the current resume and role skill map."
                )

                if missing_skills:
                    st.warning(
                        f"{len(missing_skills)} skills need further development."
                    )
                else:
                    st.success("All skills in this role's current skill map are matched.")

            # Matched skills
            st.markdown(
                '<div class="gap-section">✓ Your Existing Skills</div>',
                unsafe_allow_html=True
            )

            if matched_skills:
                cols = st.columns(3)

                for i, skill in enumerate(matched_skills):
                    with cols[i % 3]:
                        st.markdown(
                            f'<div class="skill-box matched-box">✓ {skill}</div>',
                            unsafe_allow_html=True
                        )
            else:
                st.info("No matched skills found for this role.")

            # Missing skills
            st.markdown(
                '<div class="gap-section">✦ Skills You Need to Develop</div>',
                unsafe_allow_html=True
            )

            if missing_skills:
                cols = st.columns(2)

                for i, skill in enumerate(missing_skills):
                    with cols[i % 2]:
                        st.markdown(
                            f'<div class="skill-box missing-box">◈ {skill}</div>',
                            unsafe_allow_html=True
                        )
            else:
                st.success("No missing skills found for the selected role.")

            # Recommendations
            st.markdown(
                '<div class="gap-section">Your Development Strategy</div>',
                unsafe_allow_html=True
            )

            if missing_skills:
                st.info(
                    "Focus on the skills listed above. Study the fundamentals, "
                    "practice with small projects and document your learning."
                )

                st.markdown("**Suggested learning sequence**")

                for i, skill in enumerate(missing_skills, 1):
                    st.markdown(
                        f"**Step {i}:** Build your knowledge of {skill}"
                    )
            else:
                st.success(
                    "Your resume covers all skills in the selected role's current skill map."
                )

        else:
            st.info("No job role matches are available. Analyze your resume again.")

    else:
        st.info("Analyze a resume first to view your Skill Gap Analysis.")


elif page == "Career Roadmap":
    import html

    r = st.session_state.analysis

    st.markdown("""
    <style>
    .roadmap-hero {
        background: linear-gradient(120deg, #102747, #101D35, #123C62);
        border: 1px solid #24517C;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 22px;
    }
    .roadmap-hero h1 {
        color: #FFFFFF;
        font-size: 29px;
    }
    .roadmap-hero p {
        color: #A9C8E8;
    }
    .roadmap-card {
        background: linear-gradient(145deg, #172D49, #101D30);
        border: 1px solid #284866;
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 12px;
    }
    .roadmap-label {
        color: #9CB5D1;
        font-size: 13px;
    }
    .roadmap-value {
        color: #67E8C0;
        font-size: 27px;
        font-weight: bold;
    }
    .roadmap-step {
        background: #142943;
        border: 1px solid #284866;
        border-left: 4px solid #21C7D9;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    .roadmap-step h4 {
        color: #EAF3FF;
        margin: 0 0 6px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="roadmap-hero">
        <h1>✦ Your Career Learning Roadmap</h1>
        <p>Turn your skill gaps into learning goals and track your career development.</p>
    </div>
    """, unsafe_allow_html=True)

    if r:
        matches = r.get("matches", [])

        if matches:
            role_names = [
                m.get("role", "Unknown")
                for m in matches
            ]

            selected = st.selectbox(
                "Choose your target career",
                role_names,
                key="roadmap_target_role"
            )

            match = next(
                m for m in matches
                if m.get("role") == selected
            )

            missing_skills = match.get("missing_skills", [])
            matched_skills = match.get("matched_skills", [])
            score = float(match.get("score", 0))

            analysis_key = str(
                r.get("filename", "current_resume")
            ).replace(" ", "_")

            st.markdown(f"""
            <div class="roadmap-card">
                <div class="roadmap-label">YOUR SELECTED CAREER PATH</div>
                <div style="color:white;font-size:24px;font-weight:bold;">
                    {html.escape(selected)}
                </div>
                <div class="roadmap-label">Estimated resume match</div>
                <div class="roadmap-value">{score:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

            total = len(missing_skills)
            completed = 0

            st.markdown("### Learning Progress")

            if total:
                for skill in missing_skills:
                    checkbox_key = (
                        f"roadmap_{analysis_key}_{selected}_{skill}"
                    )

                    done = st.checkbox(
                        f"Learn {skill}",
                        key=checkbox_key
                    )

                    if done:
                        completed += 1

                progress = completed / total

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric("Total Skills", total)

                with c2:
                    st.metric("Completed", completed)

                with c3:
                    st.metric("Remaining", total - completed)

                st.progress(progress)

                st.caption(
                    f"{completed} of {total} learning goals completed"
                )

                if completed == total:
                    st.success(
                        "Congratulations! You have completed this learning roadmap."
                    )
                else:
                    st.info(
                        f"{total - completed} skills remaining on your learning journey."
                    )

                st.markdown("### Your Learning Path")

                for index, skill in enumerate(missing_skills, 1):
                    safe_skill = html.escape(str(skill))

                    st.markdown(f"""
                    <div class="roadmap-step">
                        <h4>Step {index:02d} · {safe_skill}</h4>
                        <div class="roadmap-label">
                            Focus on understanding the concepts and practising with small projects.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.success(
                    "Excellent! No missing skills were found for this role in the current skill map."
                )

            st.markdown("### Your Existing Strengths")

            if matched_skills:
                st.write(" · ".join(
                    f"**{skill}**" for skill in matched_skills
                ))
            else:
                st.info("No matched skills detected yet.")

        else:
            st.info("No career matches available. Please analyze your resume again.")

    else:
        st.info("Upload and analyze your resume first to create your career roadmap.")


elif page == "AI Career Assistant":
    st.info("Starter version: ask general career-planning questions. This page does not call a paid AI API.")
    q = st.text_input("Ask a career question")
    if st.button("Get guidance") and q:
        st.write("Start by comparing your current skills with the requirements of your target role. Pick one missing skill, learn the fundamentals, build a small project, and add the evidence to your resume.")
elif page == "AI Mock Interview":
    st.info("Practice questions are generated from a small local question bank in this starter build.")
    role = st.selectbox("Select role", ["Python Developer","Data Analyst","Machine Learning Engineer","Web Developer"])
    questions = {"Python Developer":["What are Python lists and tuples?","Explain exception handling.","What is a Python decorator?"],
                 "Data Analyst":["What is data cleaning?","Explain the difference between mean and median.","What is a SQL JOIN?"],
                 "Machine Learning Engineer":["What is overfitting?","Explain train-test split.","What is precision and recall?"],
                 "Web Developer":["What is the DOM?","Explain HTTP methods.","What is responsive design?"]}
    for i,q in enumerate(questions[role],1):
        st.write(f"{i}. {q}")
elif page == "Analytics":
    r = st.session_state.analysis
    if r:
        import pandas as pd
        st.subheader("Your latest analysis")
        st.bar_chart(pd.DataFrame(r["matches"]).set_index("role")[["score"]])
        st.caption("Match scores are estimates based on the included role-skill dataset, not hiring probabilities.")
    else:
        st.info("Analytics will appear after your first resume analysis.")

elif page == "Reports":
    import pandas as pd
    import plotly.express as px

    r = st.session_state.analysis

    st.markdown("""
    <style>
    .report-hero {
        background: linear-gradient(120deg, #102747, #101D35, #123C62);
        border: 1px solid #24517C;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 22px;
    }
    .report-hero h1 {
        color: white;
        font-size: 29px;
    }
    .report-hero p {
        color: #A9C8E8;
    }
    .report-card {
        background: linear-gradient(145deg, #172D49, #101D30);
        border: 1px solid #284866;
        border-radius: 15px;
        padding: 18px;
        min-height: 115px;
    }
    .report-label {
        color: #9CB5D1;
        font-size: 13px;
    }
    .report-value {
        color: #67E8C0;
        font-size: 29px;
        font-weight: bold;
    }
    .report-heading {
        color: #EAF3FF;
        font-size: 20px;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 12px;
    }
    .role-card {
        background: #142943;
        border: 1px solid #284866;
        border-radius: 13px;
        padding: 15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="report-hero">
        <h1>✦ Career Intelligence Reports</h1>
        <p>Explore your resume performance, career opportunities and skill insights.</p>
    </div>
    """, unsafe_allow_html=True)

    if r:
        profile = r.get("profile", {})
        skills = r.get("skills", [])
        matches = r.get("matches", [])

        top_match = max(
            matches,
            key=lambda x: float(x.get("score", 0)),
            default=None
        )

        top_score = float(top_match.get("score", 0)) if top_match else 0
        top_role = top_match.get("role", "Not available") if top_match else "Not available"
        missing = top_match.get("missing_skills", []) if top_match else []

        st.write(
            f"**Candidate:** {profile.get('name') or user['username']} "
            f"  ·  **Resume:** {r.get('filename', 'Uploaded resume')}"
        )

        st.markdown(
            '<div class="report-heading">Performance Overview</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)

        metrics = [
            ("Top Match Score", f"{top_score:.0f}%", "Best role match"),
            ("Skills Identified", str(len(skills)), "Resume skills"),
            ("Role Matches", str(len(matches)), "Career opportunities"),
            ("Skills to Develop", str(len(missing)), "Top role skill gaps")
        ]

        for col, metric in zip([c1, c2, c3, c4], metrics):
            with col:
                st.markdown(f"""
                <div class="report-card">
                    <div class="report-label">{metric[0]}</div>
                    <div class="report-value">{metric[1]}</div>
                    <div class="report-label">{metric[2]}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(
            '<div class="report-heading">Career Match Analysis</div>',
            unsafe_allow_html=True
        )

        left, right = st.columns([1, 1.5])

        with left:
            st.markdown("**Overall Best Match**")

            if top_match:
                fig = px.pie(
                    names=["Match", "Remaining"],
                    values=[top_score, max(0, 100 - top_score)],
                    hole=0.75
                )
                fig.update_traces(
                    marker=dict(colors=["#21C7D9", "#203B5A"]),
                    textinfo="none"
                )
                fig.update_layout(
                    annotations=[dict(
                        text=f"<b>{top_score:.0f}%</b>",
                        x=0.5, y=0.5,
                        font_size=27,
                        font_color="white",
                        showarrow=False
                    )],
                    showlegend=False,
                    height=260,
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
                st.success(f"Best role: {top_role}")
            else:
                st.info("No role matches available.")

        with right:
            st.markdown("**Role-wise Match Comparison**")

            if matches:
                chart_df = pd.DataFrame([
                    {
                        "Role": item.get("role", "Unknown"),
                        "Match Score": float(item.get("score", 0))
                    }
                    for item in matches
                ])

                chart_df = chart_df.sort_values("Match Score")

                fig = px.bar(
                    chart_df,
                    x="Match Score",
                    y="Role",
                    orientation="h",
                    text="Match Score"
                )
                fig.update_traces(
                    marker_color="#21C7D9",
                    texttemplate="%{text:.0f}%",
                    textposition="outside"
                )
                fig.update_layout(
                    height=max(280, len(matches) * 48),
                    xaxis=dict(range=[0, 110]),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#DCEBFA",
                    margin=dict(t=10, b=10, l=5, r=35)
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            '<div class="report-heading">Skills Intelligence</div>',
            unsafe_allow_html=True
        )

        skill_col1, skill_col2 = st.columns(2)

        with skill_col1:
            st.markdown("**Extracted Skills**")
            if skills:
                st.write(" · ".join(str(s) for s in skills))
            else:
                st.info("No skills detected.")

        with skill_col2:
            st.markdown("**Skills to Develop**")
            if missing:
                for skill in missing:
                    st.markdown(f"- :orange[{skill}]")
            else:
                st.success("No missing skills for the top role.")

        st.markdown(
            '<div class="report-heading">Recommended Career Paths</div>',
            unsafe_allow_html=True
        )

        for item in sorted(
            matches,
            key=lambda x: float(x.get("score", 0)),
            reverse=True
        ):
            role = item.get("role", "Unknown")
            score = float(item.get("score", 0))
            role_missing = item.get("missing_skills", [])

            st.markdown(f"""
            <div class="role-card">
                <div style="color:white;font-size:16px;font-weight:bold;">
                    {role}
                </div>
                <div style="color:#67E8C0;font-size:23px;font-weight:bold;">
                    {score:.0f}% Match
                </div>
                <div style="color:#9CB5D1;font-size:12px;">
                    {len(role_missing)} skills to develop
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(max(0.0, min(1.0, score / 100)))

        st.markdown(
            '<div class="report-heading">Download Your Report</div>',
            unsafe_allow_html=True
        )

        pdf = create_pdf_report(r, user["username"])

        st.download_button(
            "⬇ Download Professional PDF Report",
            pdf,
            file_name="CareerFit_AI_Career_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.caption(
            "Match scores are estimates based on resume skills and the available role dataset, not hiring probabilities."
        )

    else:
        st.info("Analyze a resume first to generate your career report.")

elif page == "History":
    from database.repositories import (
        get_analysis_by_id,
        delete_analysis
    )

    st.markdown("""
    <style>
    .history-hero {
        background: linear-gradient(120deg, #102747, #101D35, #123C62);
        border: 1px solid #24517C;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 22px;
    }
    .history-hero h1 {
        color: white;
        font-size: 28px;
    }
    .history-hero p {
        color: #A9C8E8;
    }
    .history-card {
        background: linear-gradient(145deg, #172D49, #101D30);
        border: 1px solid #284866;
        border-radius: 14px;
        padding: 17px;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="history-hero">
        <h1>✦ Resume Analysis History</h1>
        <p>Access and manage your previously analyzed resumes.</p>
    </div>
    """, unsafe_allow_html=True)

    records = get_analysis_history(user["id"])

    st.markdown("### Your Saved Analyses")

    if records:
        st.caption(f"{len(records)} saved resume analyses")

        for rec in records:
            analysis_id = rec["id"]

            with st.container(border=True):
                left, right = st.columns([3, 1])

                with left:
                    st.markdown(f"### 📄 {rec['filename']}")
                    st.caption(f"Analysis ID: #{analysis_id}")
                    st.caption(f"Saved on: {rec['created_at']}")

                with right:
                    if st.button(
                        "↗ Load Analysis",
                        key=f"load_{analysis_id}",
                        use_container_width=True
                    ):
                        saved_result = get_analysis_by_id(
                            user["id"],
                            analysis_id
                        )

                        if saved_result:
                            saved_result["analysis_id"] = analysis_id
                            st.session_state.analysis = saved_result
                            st.success("Analysis loaded successfully!")
                            st.rerun()
                        else:
                            st.error("Saved analysis could not be found.")

                if st.button(
                    "🗑 Delete",
                    key=f"delete_{analysis_id}",
                    use_container_width=True
                ):
                    st.session_state["confirm_delete_id"] = analysis_id
                    st.rerun()

                if st.session_state.get("confirm_delete_id") == analysis_id:
                    st.warning(
                        f"Are you sure you want to delete {rec['filename']}?"
                    )

                    confirm_col, cancel_col = st.columns(2)

                    with confirm_col:
                        if st.button(
                            "Yes, Delete",
                            key=f"confirm_{analysis_id}",
                            type="primary",
                            use_container_width=True
                        ):
                            deleted = delete_analysis(
                                user["id"],
                                analysis_id
                            )

                            st.session_state.pop("confirm_delete_id", None)

                            if deleted:
                                st.success("Analysis deleted successfully!")
                            else:
                                st.error("Could not delete this analysis.")

                            st.rerun()

                    with cancel_col:
                        if st.button(
                            "Cancel",
                            key=f"cancel_{analysis_id}",
                            use_container_width=True
                        ):
                            st.session_state.pop(
                                "confirm_delete_id",
                                None
                            )
                            st.rerun()

    else:
        st.info("No saved analyses yet. Upload a resume to get started.")

elif page == "Settings":
    st.write("Account settings")
    st.write("Username:", user["username"])
    st.write("Role:", user["role"])
    st.write("Status:", user["status"])
elif page == "Admin Panel":
    if user["role"] != "admin":
        st.error("Admin access required.")
        st.stop()
    from database.repositories import list_users, set_user_status, get_system_stats
    stats = get_system_stats()
    a,b,c = st.columns(3)
    a.metric("Users", stats["users"])
    b.metric("Pending", stats["pending"])
    c.metric("Analyses", stats["analyses"])
    st.subheader("User access requests")
    for item in list_users():
        cols = st.columns([2,2,1,1,1])
        cols[0].write(item["username"])
        cols[1].write(item["email"])
        cols[2].write(item["status"])
        if item["role"] != "admin":
            if cols[3].button("Approve", key=f"approve_{item['id']}"):
                set_user_status(item["id"], "approved")
                st.rerun()
            if cols[4].button("Reject", key=f"reject_{item['id']}"):
                set_user_status(item["id"], "rejected")
                st.rerun()
