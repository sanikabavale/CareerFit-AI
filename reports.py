
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)


NAVY = colors.HexColor("#101D35")
DARK = colors.HexColor("#172B4D")
BLUE = colors.HexColor("#2878F0")
CYAN = colors.HexColor("#21C7D9")
LIGHT = colors.HexColor("#EEF4FC")
TEXT = colors.HexColor("#26364D")
MUTED = colors.HexColor("#718096")
BORDER = colors.HexColor("#DCE5F0")
WHITE = colors.white


def safe_text(value):
    if value is None:
        return "Not available"

    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value) or "Not available"

    if isinstance(value, dict):
        return ", ".join(
            f"{key}: {val}" for key, val in value.items()
        ) or "Not available"

    return escape(str(value))


def make_paragraph(value, style):
    return Paragraph(safe_text(value), style)


def add_section(story, title, styles):
    story.append(Spacer(1, 12))
    story.append(Paragraph(title.upper(), styles["Section"]))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=CYAN,
            spaceAfter=8
        )
    )


def add_detail(story, label, value, styles):
    if value:
        story.append(
            Paragraph(
                f"<b>{escape(label)}:</b> {safe_text(value)}",
                styles["BodyCustom"]
            )
        )


def draw_page(canvas, doc):
    canvas.saveState()

    page_width, page_height = A4

    canvas.setFillColor(NAVY)
    canvas.rect(
        0,
        page_height - 13 * mm,
        page_width,
        13 * mm,
        fill=1,
        stroke=0
    )

    canvas.setFillColor(CYAN)
    canvas.rect(
        0,
        page_height - 13 * mm,
        5 * mm,
        13 * mm,
        fill=1,
        stroke=0
    )

    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(WHITE)
    canvas.drawString(18 * mm, page_height - 8.5 * mm, "CAREERFIT AI")

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, "Discover Your Skills. Find Your Fit.")

    canvas.drawRightString(
        page_width - 18 * mm,
        10 * mm,
        f"Page {doc.page}"
    )

    canvas.setStrokeColor(BORDER)
    canvas.line(
        18 * mm,
        15 * mm,
        page_width - 18 * mm,
        15 * mm
    )

    canvas.restoreState()


def create_pdf_report(result, username):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        title="CareerFit AI Career Analysis Report",
        author="CareerFit AI"
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="MainTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=29,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="SubtitleCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=MUTED,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=BLUE,
        spaceBefore=5,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="BodyCustom",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        textColor=TEXT,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="SmallCustom",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=TEXT
    ))

    styles.add(ParagraphStyle(
        name="TableHeaderCustom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=WHITE
    ))

    story = []

    profile = result.get("profile") or {}
    skills = result.get("skills") or []
    matches = result.get("matches") or []

    # Report heading
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Career Analysis Report",
        styles["MainTitle"]
    ))
    story.append(Paragraph(
        "AI-Powered Resume Analysis & Job Recommendation System",
        styles["SubtitleCustom"]
    ))

    story.append(HRFlowable(
        width="100%",
        thickness=2,
        color=BLUE,
        spaceAfter=12
    ))

    # Candidate information
    add_section(story, "Candidate Profile", styles)

    candidate_name = profile.get("name") or username
    email = profile.get("email")
    phone = profile.get("phone")
    linkedin = profile.get("linkedin")
    github = profile.get("github")

    profile_rows = [
        [
            Paragraph("<b>Candidate</b>", styles["SmallCustom"]),
            make_paragraph(candidate_name, styles["SmallCustom"]),
            Paragraph("<b>Account</b>", styles["SmallCustom"]),
            make_paragraph(username, styles["SmallCustom"])
        ],
        [
            Paragraph("<b>Email</b>", styles["SmallCustom"]),
            make_paragraph(email, styles["SmallCustom"]),
            Paragraph("<b>Phone</b>", styles["SmallCustom"]),
            make_paragraph(phone, styles["SmallCustom"])
        ]
    ]

    profile_table = Table(
        profile_rows,
        colWidths=[65, 155, 55, 155]
    )

    profile_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(profile_table)

    if linkedin:
        add_detail(story, "LinkedIn", linkedin, styles)

    if github:
        add_detail(story, "GitHub", github, styles)

    # Summary
    summary = profile.get("summary")

    if summary:
        add_section(story, "Professional Summary", styles)
        story.append(make_paragraph(summary, styles["BodyCustom"]))

    # Extracted skills
    add_section(story, "Extracted Skills", styles)

    if skills:
        skill_text = "  |  ".join(str(skill) for skill in skills)
        story.append(
            Paragraph(safe_text(skill_text), styles["BodyCustom"])
        )
    else:
        story.append(
            Paragraph("No skills detected in the uploaded resume.", styles["BodyCustom"])
        )

    # Job role matches
    add_section(story, "Job Role Recommendations", styles)

    if matches:
        rows = [[
            Paragraph("JOB ROLE", styles["TableHeaderCustom"]),
            Paragraph("MATCH", styles["TableHeaderCustom"]),
            Paragraph("MISSING SKILLS", styles["TableHeaderCustom"])
        ]]

        for item in matches:
            role = item.get("role", "Unknown role")
            score = item.get("score", 0)
            missing = item.get("missing_skills") or []

            rows.append([
                make_paragraph(role, styles["SmallCustom"]),
                make_paragraph(f"{score}%", styles["SmallCustom"]),
                make_paragraph(", ".join(missing) or "None", styles["SmallCustom"])
            ])

        match_table = Table(
            rows,
            colWidths=[125, 55, 250],
            repeatRows=1
        )

        match_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ]))

        story.append(match_table)
    else:
        story.append(
            Paragraph("No job role matches are available.", styles["BodyCustom"])
        )

    # Education, experience and projects
    optional_sections = [
        ("Education", profile.get("education")),
        ("Experience", profile.get("experience")),
        ("Projects", profile.get("projects"))
    ]

    for section_title, section_data in optional_sections:
        if section_data:
            add_section(story, section_title, styles)
            story.append(
                make_paragraph(section_data, styles["BodyCustom"])
            )

    # Important note
    add_section(story, "Important Note", styles)

    story.append(Paragraph(
        "CareerFit AI match scores are estimates based on extracted resume "
        "skills and the available job-role skill map. They are intended to "
        "support career exploration and are not hiring probabilities, "
        "recruiter decisions, or guarantees of employment.",
        styles["BodyCustom"]
    ))

    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "Generated by CareerFit AI",
        ParagraphStyle(
            name="FinalNote",
            parent=styles["BodyCustom"],
            alignment=TA_CENTER,
            textColor=BLUE,
            fontName="Helvetica-Bold"
        )
    ))

    doc.build(
        story,
        onFirstPage=draw_page,
        onLaterPages=draw_page
    )

    return buffer.getvalue()
