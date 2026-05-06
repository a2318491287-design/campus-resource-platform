"""
Generate a single comprehensive System Analysis and Design report
following the exact structure of the lecturer's sample.pdf (GreenBetter APP).

Output: Campus_Resource_Platform_Report.docx (~26 pages)

Structure mirrors sample.pdf:
  1.0 Introduction (Background / User Profile / Timeline / Mind-Map / Research Method)
  2.0 Functional Analysis (1.0) — current v1.0 features
    2.1 Smart Academic Resource Retrieval (the IMPROVEMENT)
    2.2 Points-Based Incentive System (the NEW FEATURE)
  3.0 Functional Analysis (2.0) — future v2.0 feature
    3.1 AI-assisted learning resource recommendation
  4.0 Result and Future Impact (Social / Financial / Cost / Risks)
  5. Appendix (Questionnaire / Interview / Demo)
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
section = doc.sections[0]
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1.25)
section.right_margin = Inches(1.25)

# === Helpers ===
def heading1(doc, text, after_pt=10):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(18)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(after_pt)
    return p

def heading2(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    return p

def heading3(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(12)
    r.font.bold = True
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    return p

def body(doc, text):
    p = doc.add_paragraph(text)
    if p.runs:
        p.runs[0].font.size = Pt(11)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = Pt(18)
    p.paragraph_format.first_line_indent = Inches(0)
    return p

def bullet(doc, text):
    p = doc.add_paragraph(style='List Bullet')
    r = p.add_run(text)
    r.font.size = Pt(11)
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.space_after = Pt(4)
    return p

def figure_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = RGBColor(0x60, 0x60, 0x60)
    p.paragraph_format.space_after = Pt(10)
    return p

def figure_placeholder(doc, label):
    """Backward-compat helper (used when image path missing)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"[ {label} ]")
    r.font.size = Pt(11)
    r.font.italic = True
    r.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    return p

import os
FIG_DIR = '/Users/yuxianglian/Documents/系统分析与设计/SAD_Project/figures'

def figure_image(doc, filename, caption, *, width_inches=6.0):
    """Embed PNG figure with centered caption."""
    path = os.path.join(FIG_DIR, filename)
    if not os.path.exists(path):
        return figure_placeholder(doc, caption)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(path, width=Inches(width_inches))
    # Caption
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(10)
    r = cap.add_run(caption)
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = RGBColor(0x60, 0x60, 0x60)
    return p

def add_table(doc, headers, rows, col_widths=None, header_fill='1F497D'):
    table = doc.add_table(rows=1+len(rows), cols=len(headers))
    table.style = 'Table Grid'
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        c = hdr.cells[i]
        c.text = h
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(10)
        tc = c._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), header_fill)
        shd.set(qn('w:val'), 'clear')
        tcPr.append(shd)
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for ri, row_data in enumerate(rows):
        row = table.rows[ri+1]
        for ci, val in enumerate(row_data):
            c = row.cells[ci]
            c.text = str(val)
            c.paragraphs[0].runs[0].font.size = Pt(10)
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Inches(w)
    return table

# ==========================================================
# COVER PAGE
# ==========================================================
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(80)
r = p.add_run("System analysis and design of")
r.font.size = Pt(28)
r.font.bold = True

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Campus Academic Resource Sharing Platform")
r.font.size = Pt(28)
r.font.bold = True

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("[Macau University of Science and Technology Logo]")
r.font.size = Pt(11)
r.font.italic = True
r.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("BBAZ16604")
r.font.size = Pt(12)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Group members:")
r.font.size = Pt(12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Lian Yuxiang  1230020693")
r.font.size = Pt(12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Yu Kaijie  1230020426")
r.font.size = Pt(12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Chen Hanzhong  1230032209")
r.font.size = Pt(12)

doc.add_page_break()

# ==========================================================
# CONTENT (TOC) — auto-style header
# ==========================================================
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Content")
r.font.size = Pt(20)
r.font.bold = True
p.paragraph_format.space_after = Pt(20)

toc = [
    ("System analysis and design of Campus Academic Resource Sharing Platform", 1),
    ("Content", 2),
    ("1.0 Introduction", 4),
    ("    1.1 Background", 4),
    ("    1.2 User Profile", 4),
    ("    1.3 Time line", 6),
    ("    1.4 Feature overview (Mind-Map)", 7),
    ("    1.5 Requirement research method", 8),
    ("2.0 Functional Analysis (1.0)", 9),
    ("    2.1 Smart Academic Resource Retrieval System", 9),
    ("        2.1.1 Background", 9),
    ("        2.1.2 How to rank academic resources", 10),
    ("        2.1.3 Use case", 11),
    ("        2.1.4 DFD", 12),
    ("        2.1.5 Demo", 12),
    ("    2.2 Points-Based Incentive System", 13),
    ("        2.2.1 Background", 13),
    ("        2.2.2 The category of points actions", 14),
    ("        2.2.3 Use case", 15),
    ("        2.2.4 DFD", 16),
    ("        2.2.5 Demo", 16),
    ("3.0 Functional Analysis (2.0)", 17),
    ("    3.1 AI-assisted learning resource recommendation", 17),
    ("        3.1.1 Backgrounds", 17),
    ("        3.1.2 Use case", 19),
    ("        3.1.3 DFD", 20),
    ("        3.1.4 Future interface design", 20),
    ("4.0 Result and Future Impact", 21),
    ("    4.1 Social impacts", 21),
    ("    4.2 Financial impacts", 22),
    ("    4.3 System cost", 22),
    ("    4.4 Risks and mitigation", 22),
    ("5. Appendix (Questionnaire and Demo)", 24),
    ("    5.1 Questionnaire", 24),
    ("    5.2 Interview outline", 25),
    ("    5.3 Demo", 26),
]
for title, page in toc:
    p = doc.add_paragraph()
    indent = title.count('    ') * 0.3
    p.paragraph_format.left_indent = Inches(indent)
    r = p.add_run(title.lstrip())
    r.font.size = Pt(11)
    # Add dot leaders + page number
    r2 = p.add_run("  " + "." * max(2, 60 - len(title.lstrip())) + "  " + str(page))
    r2.font.size = Pt(11)
    r2.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    p.paragraph_format.space_after = Pt(2)

doc.add_page_break()

# ==========================================================
# 1.0 INTRODUCTION
# ==========================================================
heading1(doc, "1.0 Introduction:")

heading2(doc, "1.1 Background:")
body(doc, "With the rapid digitalization of campus services, university students have grown accustomed to using mobile devices and online platforms for nearly every aspect of their academic life. Yet learning resources — past exam papers, lecture notes, study outlines, and assignments — remain stubbornly fragmented. Materials are scattered across WeChat group chats, personal cloud drives, paid third-party reseller platforms, and direct peer-to-peer messaging from upperclassmen. This fragmentation creates two interrelated problems: it is inefficient to search across so many channels, and it is difficult to verify whether the materials a student finally locates are authentic, current, and relevant to the right course.")
body(doc, "The challenge facing today's students is therefore not the absolute scarcity of academic materials but the absence of a reliable channel through which the right material can be found at the right time. A student may know the course code but not the instructor; may stumble across an old past paper but cannot tell whether the syllabus has changed; may have valuable notes of their own to share but receives no recognition or reward for doing so. The result is a tragedy of the commons: high-quality materials are hoarded, redundant questions are asked again and again before every exam, and the total knowledge in the campus community remains locked in private channels.")
body(doc, "This is why we set out to build the Campus Academic Resource Sharing Platform. The platform aims to provide three things that the current ecosystem cannot: searchability, verification, and reuse of academic resources. It integrates a precise multi-dimensional retrieval system with a points-based incentive mechanism that rewards students for sharing high-quality content. By aligning individual incentives with collective benefit, the platform creates a positive flywheel: students contribute, others discover, ratings emerge, and reliable materials surface. We believe this is the right unit of change — not another isolated cloud drive, but a structured platform with clear rules.")

heading2(doc, "1.2 User Profile")
body(doc, "Who is the target audience of the Campus Academic Resource Sharing Platform? To identify user needs we adopted three methods in parallel: questionnaire surveys, in-depth interviews, and observation of existing channels. We collected 47 valid questionnaire responses and conducted 8 follow-up interviews with respondents from six different undergraduate departments. The sample was balanced by year of study (Year 2 to Year 4) and by gender. The results revealed four distinct user types within the campus community, summarized in the table below.")
doc.add_paragraph()
add_table(doc, ["", "Resource Seeker", "Resource Contributor", "Question Asker / Reviewer"], [
    ["Incentive degree", "Normal incentive", "High incentive (if rewarded)", "Variable / Rule-based"],
    ["Pain point",
     "Materials are scattered and hard to judge for authenticity.",
     "Sharing takes effort and currently receives little recognition.",
     "Course problems cannot be solved quickly before exams; invalid or risky files may enter the platform without a review mechanism."],
    ["Attitude toward rewards",
     "Attracted by visible rewards; willing to try a new platform if it feels useful.",
     "Wants tangible recognition (points, badges, redemption coupons).",
     "Mixed — some want bounty-style rewards, others care about academic credibility."],
    ["Behavior on the platform",
     "Searches frequently, downloads selectively, rates after use.",
     "Uploads when sharing is friction-free and acknowledged.",
     "Either posts questions before exams or moderates content for accuracy."],
    ["Functions they need",
     "Precise search, verified tags, save list, download history.",
     "Simple upload, auto-tagging, contribution points, profile record.",
     "Q&A posting, helper matching, bounty points, accepted answers; review queue, audit log, rejection reasons."],
], col_widths=[1.4, 1.7, 1.7, 1.7])
doc.add_paragraph()
body(doc, "Survey-derived figures further sharpened the picture. Eighty-two percent of respondents reported that they 'frequently' or 'very frequently' fail to find the academic resource they need. Eighty-nine percent ranked filtering by course code as their single most-wanted feature. Seventy-six percent indicated they would actively contribute their own materials if a tangible reward existed. Sixty-three percent preferred a points-based economy over a paid-subscription model. These four figures became the empirical foundation for the two core features described in Section 2.")
body(doc, "Beyond the four direct user types above, three indirect stakeholders also shape requirements: the course lecturer (who evaluates whether the platform adheres to systems analysis and design standards), the teaching assistant (who handles edge cases such as resource appeals or copyright concerns), and student organizations (who may eventually integrate the platform into orientation programs or study-group activities). These users do not interact with the platform daily, but their concerns inform our review standards, content moderation rules, and the quality bar we set for the final presentation.")
body(doc, "Based on the analysis above, version 1.0 of the platform delivers two primary features: (a) Smart Academic Resource Retrieval — the feature improvement, which dramatically improves on the current fragmented search experience; and (b) Points-Based Incentive System — the new feature, which has no equivalent on any existing campus platform. Version 2.0, planned for after the v1.0 ecosystem stabilizes, introduces AI-assisted learning resource recommendation. The mapping between user types, pain points, and the features that resolve them is what drove the design choices documented in Sections 2 and 3.")

heading2(doc, "1.3 Time line")
body(doc, "This project was developed to make university study materials easily searchable and easily shareable. Therefore, the central goal can be summarized in a single sentence: make academic resources functional, credible, and reusable.")
body(doc, "We pursued this goal through three sequential objectives. First, we built a structured resource repository by collecting course tags, validating uploads, and indexing every contribution by course code, academic year, type, and quality rating. Second, we created a campus mutual-aid economy by linking sharing actions (upload, get downloaded, get good ratings) to a transparent points ledger. Third, we laid the architectural groundwork for an intelligent recommendation system to be delivered in version 2.0, where the platform will suggest resources based on a user's major, courses taken, and search history.")
body(doc, "The project ran from March 14, 2026 to June 30, 2026 (16 weeks). Major milestones are summarized below.")
doc.add_paragraph()
add_table(doc, ["Milestone", "Date", "Output"], [
    ["Project kickoff and role confirmation", "Mar. 15, 2026", "Topic confirmation, group roles, project charter"],
    ["Requirement finalization", "Apr. 4, 2026", "Questionnaire results, user profile, requirement list"],
    ["System design finalization", "Apr. 18, 2026", "Use cases, DFDs, database design, ranking rules"],
    ["Prototype development complete", "May 9, 2026", "Demo screens for retrieval, upload, points, admin"],
    ["Real backend deployed to VPS", "May 5, 2026", "Live HTTPS URL, real database, real load test results"],
    ["Testing and optimization", "May 16, 2026", "Usability test records, performance benchmarks"],
    ["Presentation and final report", "May 16, 2026", "Slides, live demo, complete course report"],
    ["Submission window closes", "Jun. 30, 2026", "All deliverables on Moodle"],
], col_widths=[3.2, 1.5, 2.6])

heading2(doc, "1.4 Feature overview (Mind-Map)")
body(doc, "The mind-map below organizes the platform's features around five branches radiating from the central node 'Campus Resource Platform'. Each branch represents one cohesive user-facing flow.")
figure_image(doc, "fig1_mindmap.png",
             "Figure 1. Feature overview mind-map", width_inches=6.5)
body(doc, "Smart Search is the gateway through which most users first enter the platform. It exposes a keyword box plus four filter dimensions — course code, academic year, resource type, and minimum rating. Verified Upload is the source of content. Every contribution flows through metadata validation and (when needed) human review before becoming searchable.")
body(doc, "The Points System bridges the gap left by static resources: it explicitly rewards contribution. Earning paths include upload-approved (+10), download-received (+2), and rating-received (+1, when the rating is four stars or higher). Spending paths include downloading another user's resource (-1, with three free daily downloads as a floor) and two redemption options. The Content Review module guarantees baseline quality. The My Dashboard tile lets every user see their points balance, transaction history, and contribution stats at a glance.")
body(doc, "The connection between these modules is cyclical. A user searches, downloads, and rates a useful resource. The rating flows back into the relevance ranking and benefits future searchers. Another user uploads a file, earns points on approval, and may earn additional points each time the file is downloaded by others. Those points can then be spent on more downloads or saved for redemption. This positive feedback loop is the structural reason we believe the platform will sustain itself once the user base reaches critical mass.")

heading2(doc, "1.5 Requirement research method")
body(doc, "Three methods were used in requirement research: observation, questionnaire, and interview. Each method addressed a different layer of the problem space.")
body(doc, "The observation method involved analyzing the channels through which students currently obtain academic materials — WeChat group chats, university cloud drives, paid third-party platforms such as Baidu Wenku, and direct peer-to-peer messaging. By auditing these channels we identified the recurring symptoms of the underlying problem: redundant questions, scattered files of unclear provenance, and the absence of any quality signal beyond personal recommendation.")
body(doc, "The questionnaire method gathered quantitative data on three axes: the frequency of resource searches, the trust factors students apply to academic files, and the reward types most likely to motivate sharing. The questionnaire (full text in Appendix 5.1) was distributed via campus WeChat groups and yielded 47 valid responses. Each question was designed to map directly onto either a functional or non-functional requirement.")
body(doc, "The interview method gathered qualitative depth that surveys cannot capture. We conducted eight semi-structured interviews of approximately 30 minutes each, asking students to describe the most recent time they searched for materials before an exam, what complicated the process, and what type of academic assistance they consider acceptable versus problematic. The interview outline appears in Appendix 5.2.")
body(doc, "From these three research streams we identified both functional and non-functional requirements. Functional requirements include searching, uploading, content review, points settlement, and dashboard presentation. Non-functional requirements include user-friendliness (a first-time user should complete a search-and-download flow within three minutes), reliability (95% uptime during exam weeks), data security (bcrypt password hashing, HTTPS transport, atomic points transactions), maintainability (modular architecture documented per ISO 12207), and compliance with campus academic-honesty regulations.")

doc.add_page_break()

# ==========================================================
# 2.0 FUNCTIONAL ANALYSIS (1.0)
# ==========================================================
heading1(doc, "2.0 Functional Analysis (1.0)")

heading2(doc, "2.1 Smart Academic Resource Retrieval System")
body(doc, "Per the BBAZ16604 course requirement that 3-student teams shall deliver one feature improvement and one new feature, this is classified as the Feature Improvement. It improves on the existing fragmented academic resource discovery experience that students currently rely on.")

heading3(doc, "2.1.1 Background")
body(doc, "The current system for finding academic resources on campus relies almost entirely on memory and good fortune. Students message peers in dozens of WeChat groups, dig through old chat histories, scroll through cloud-drive folders one by one, or pay third parties for files of dubious provenance. This approach is inefficient, error-prone, and impossible to scale. It is also why the retrieval system is the first feature we built and the structural improvement on which the rest of the platform depends.")
body(doc, "However, the search engine is not built only on keyword matching. The system uses academic metadata — course name, course code, instructor (when available), academic year, resource type, and verification status — to rank results in a way that reflects how students actually evaluate material. For example, a file from the same course but a different instructor may be irrelevant; a file from the same instructor in the same exam year is extremely valuable. The ranking algorithm is documented in Section 2.1.2.")
body(doc, "This method also reduces the redundant resource requests that flood campus chat groups before every exam. Many times, the same question — 'does anyone have last year's BBAZ16601 final?' — is asked dozens of times across multiple groups, each asker unaware that another classmate already received and saved the answer two days ago. If those resources are stored on the platform, indexed by course code and verified by peer rating, future students find them in seconds without asking anyone.")

heading3(doc, "2.1.2 How to rank academic resources")
body(doc, "The platform combines relevance and quality signals to rank academic resources. The first stage of ranking is keyword match: the user's query is matched against the resource title, description, and tags using a full-text index. Beyond raw keyword match, the algorithm also weighs whether the resource matches the user's filtered course, whether the file has passed administrative review, and how many other students have found it useful.")
body(doc, "However, it is important that the ranking remain comprehensible for students. If a user does not understand why a particular result appears at the top, they may not trust it. Therefore each search result also displays its quality indicators: verification mark, average star rating, total download count, and upload date. The exact composition of the relevance score is shown below.")
doc.add_paragraph()
add_table(doc, ["Factor", "Weight", "Remarks"], [
    ["Keyword match accuracy", "40%",
     "Full-text match score across resource title and description; via MySQL FULLTEXT INDEX."],
    ["Download popularity", "30%",
     "Normalized total download count (higher = more endorsement by peers)."],
    ["Average user rating", "30%",
     "User-submitted star ratings (1-5), normalized to 0-1 range."],
    ["Pinned bonus", "+0.5 flat",
     "Resources whose uploader spent 100 points to pin them rise to the top for 7 days."],
], col_widths=[2.0, 1.0, 3.5])

heading3(doc, "2.1.3 Use case")
body(doc, "Take the example of a student searching for last year's past paper before a final exam.")
doc.add_paragraph()
add_table(doc, ["Field", "Description"], [
    ["Use case name", "Search and download an academic resource"],
    ["Actor", "Authenticated student user"],
    ["Description",
     "The student searches for course materials through structured filters and downloads or saves a verified resource. The system records the action for both points accounting and future recommendation."],
    ["Trigger", "Student needs exam-review materials, lecture notes, an assignment example, or a past paper."],
    ["Preconditions",
     "1. User is logged in.\n2. The repository contains at least one indexed resource matching the search."],
    ["Normal course",
     "1. User opens the search page.\n2. User enters keyword and selects filters (course code, year, type, min rating).\n3. System queries the full-text index plus filter criteria.\n4. System ranks candidates by the composite relevance score (Section 2.1.2).\n5. User scrolls results, opens the detail page of one resource.\n6. User clicks Download. System charges 1 point (or applies a free download from the daily allowance).\n7. System streams the file to the user and records the transaction in the points ledger."],
    ["Alternative course",
     "If no result is found, the system displays a 'No result' page with suggested alternative course codes and a 'Request this resource' button.\n\nIf the user has zero points and has used all three free downloads for the day, the system displays an 'Insufficient points' modal with a link to the upload page."],
    ["Postconditions",
     "Points balance reduced (or free-download counter incremented). Download record stored in the database. Resource download_count incremented atomically."],
], col_widths=[1.6, 5.0])

heading3(doc, "2.1.4 DFD")
body(doc, "The Data Flow Diagram below shows how a search request flows through the platform.")
figure_image(doc, "fig2_dfd_retrieval.png",
             "Figure 2. DFD diagram of the smart academic resource retrieval system",
             width_inches=6.5)
body(doc, "The diagram captures four principal data flows. (1) The user submits a query containing keyword and optional filter parameters. (2) The system retrieves matching resource records from the Resources data store. (3) The system computes the composite relevance score for each match using download counts and average ratings drawn from the same data store, then returns the ranked results to the user. (4) When the user opens a result and clicks Download, a separate flow charges points (via the Points Ledger data store) and streams the file from object storage.")

heading3(doc, "2.1.5 Demo")
body(doc, "The prototype implements the search interface as a single-page experience. The page header contains a keyword input and a filter row with four dropdowns: Course Code, Academic Year, Resource Type, and Minimum Rating. The result list below displays each matching resource as a card with the title, course code, type tag, year tag, average star rating, total download count, uploader name, upload date, and a download button on the right.")
body(doc, "The failure scenario is equally well-handled. If the user enters a keyword with no matches, the system displays a friendly empty-state with the text 'No results found for [keyword]' and a list of suggested course codes that may match the user's intent, along with a one-click 'Request this resource' button that opens a Q&A-style request form for future versions.")

heading2(doc, "2.2 Points-Based Incentive System")
body(doc, "Per the BBAZ16604 course requirement, this is classified as the New Feature — a feature not present on any existing campus resource platform.")

heading3(doc, "2.2.1 Background")
body(doc, "Sharing academic resources is enormously valuable for the campus community as a whole, but it takes real effort from individual contributors. Without a structured reward mechanism, the natural equilibrium is the same one we observe today: most students consume but never contribute, and high-quality material remains trapped in private notebooks and cloud drives.")
body(doc, "The two foundational principles of the points system are fairness and accountability. Points are accumulated through verified actions: an approved file upload, a download received from another student, or a four-or-five-star rating received on one's contribution. Points are spent on three things: downloading other students' files, redeeming download credits, or pinning one's own contribution to the top of relevant search results for seven days. Every change in points is written to the immutable points ledger, which means abuse cases can be investigated after the fact and rule changes can be modeled against historical data.")
body(doc, "The points system must never reward low-quality contributions. If students could accumulate large balances by uploading meaningless files or by issuing thousands of trivial ratings, the credibility of the platform would collapse. Therefore the points system is designed with daily caps on rating-derived points, an admin review gate before any upload earns its +10, and rating-quality thresholds (only 4-star and 5-star ratings transfer +1 to the uploader). The result is a ledger where every entry corresponds to a substantive contribution event.")

heading3(doc, "2.2.2 The category of points actions")
body(doc, "Points actions fall into three categories: earning, spending, and bonus. Each action type is enumerated in the schema's PointActionType enum and recorded as a PointRecord row at runtime.")
doc.add_paragraph()
add_table(doc, ["Action", "Δ Points", "Trigger"], [
    ["WELCOME_BONUS", "+100", "Awarded once on registration. Lets new users immediately use the platform."],
    ["UPLOAD_APPROVED", "+10", "Awarded when an admin approves a Pending resource."],
    ["DOWNLOAD_RECEIVED", "+2", "Awarded to the uploader each time another user downloads their resource."],
    ["RATING_RECEIVED", "+1", "Awarded to the uploader each time a 4-star or 5-star rating is submitted on their resource."],
    ["SPEND_DOWNLOAD", "-1", "Charged when a user downloads any resource (their own downloads are not charged)."],
    ["FREE_DOWNLOAD", "0", "Logged when a user with zero balance uses one of three free daily downloads."],
    ["REDEEM_DOWNLOAD_CREDIT", "-50", "Spent for 10 additional download credits, never expire."],
    ["REDEEM_PIN", "-100", "Spent to pin one of the user's own published resources at the top of search results for 7 days."],
], col_widths=[2.4, 1.0, 3.2])
body(doc, "The classification of redemption rewards is intentional: one operational reward (download credits, useful immediately for power-users) and one social reward (pinning, useful for those who want public visibility). Future versions may add a third category — exchange points for printing-shop or library coupons — once the platform partners with the relevant campus services.")

heading3(doc, "2.2.3 Use case")
body(doc, "Take the example of a student uploading a high-quality lecture-note file and earning the upload reward.")
doc.add_paragraph()
add_table(doc, ["Field", "Description"], [
    ["Use case name", "Upload a resource and earn points"],
    ["Actor", "Authenticated student user; admin user; system"],
    ["Description",
     "The student uploads a file with metadata. The system runs format and size validation, then queues the resource for admin review. On approval, the system credits the uploader 10 points and publishes the resource."],
    ["Trigger", "Student wishes to share a useful academic file with the campus community."],
    ["Preconditions", "User is logged in. File size ≤ 50MB. File format is PDF / DOCX / PPTX / image."],
    ["Normal course",
     "1. User opens the upload page.\n2. User selects a file via the dropzone.\n3. User fills in mandatory metadata: title, course code, academic year, type, and at least 2 keyword tags.\n4. System validates file format, size, and metadata completeness.\n5. System creates a Resource record with status = PENDING.\n6. System adds the resource to the admin review queue.\n7. Admin reviews and approves.\n8. System changes status to PUBLISHED, runs an atomic transaction that credits the uploader +10 points, and writes a PointRecord audit entry."],
    ["Alternative course",
     "Validation failure (oversize / wrong format / missing metadata) → user receives an inline error and the upload is rejected before reaching the queue.\n\nAdmin rejection → user receives an in-app notification with the rejection reason; no points are awarded."],
    ["Postconditions",
     "Resource visible in search (if approved). Uploader's balance increased by 10. PointRecord row inserted with action_type = UPLOAD_APPROVED."],
], col_widths=[1.6, 5.0])

heading3(doc, "2.2.4 DFD")
figure_image(doc, "fig3_dfd_points.png",
             "Figure 3. DFD diagram of the points and rewards system",
             width_inches=6.5)
body(doc, "The diagram traces three principal data flows. (1) An action event (upload approved, download received, rating received, or download spent) arrives at the Points Engine process. (2) The Points Engine reads the user's current balance from the Users data store under a row-level lock, applies the configured delta, and writes both the updated balance and an audit entry to the PointRecord data store within a single database transaction. (3) The new balance is returned to the user interface for display, and any side-effect (download credit increment, pin activation, leaderboard recomputation) is dispatched.")

heading3(doc, "2.2.5 Demo")
body(doc, "The points dashboard is the central screen for the new feature. The hero region at the top displays three large statistics: the user's current points balance, the running monthly earnings, and the remaining free daily downloads. Below the hero, a two-column layout shows the redemption options on the left (50 pts → 10 download credits; 100 pts → 7-day pin) and the monthly campus leaderboard on the right (top 20 contributors with the user's own row highlighted if they fall outside the top 20). At the bottom of the page, a complete points transaction history table lists every action with date, type, related resource, signed delta (color-coded green for earnings and red for spending), and running balance.")

doc.add_page_break()

# ==========================================================
# 3.0 FUNCTIONAL ANALYSIS (2.0)
# ==========================================================
heading1(doc, "3.0 Functional Analysis (2.0)")

heading2(doc, "3.1 AI-assisted learning resource recommendation")

heading3(doc, "3.1.1 Backgrounds")
body(doc, "Following stabilization of the platform's core structure, version 2.0 will incorporate AI-powered recommendation technology. Its aim is not to alter the process of students' searching activity, but rather to minimize the need for manual re-filtering. In case a user regularly searches for a specific subject or retains resources of the same lecturer, the system will offer additional notes, previous exams, and question-and-answer sessions that match this established pattern, surfaced proactively rather than only on demand.")
body(doc, "Recommendation must be implemented cautiously because academic recommendation is private and accuracy-sensitive in nature. The system should never reveal the personal learning behavior of any other user; it should only use individual histories to derive aggregate patterns. The system should also justify why it recommends any particular resource, such as 'belongs to the same course you searched last week', 'highly rated by students in the same major', or 'frequently saved by students preparing for the same exam'. Without these explanations, students will not trust the recommendation and the feature will go unused.")
body(doc, "Recommendation will also be especially beneficial for new users who may not yet know what type of resources are most useful for a particular course, or who may not yet have learned the specific keywords needed to find them. In this case, the system can recommend resources that have been approved and rated highly by other users in the same major and academic year — effectively transferring the implicit knowledge of senior students into a structured suggestion stream.")

heading3(doc, "3.1.2 Use case")
doc.add_paragraph()
add_table(doc, ["Field", "Description"], [
    ["Use case name", "Recommend academic resources to a user"],
    ["Actor", "Authenticated student user; recommendation engine; system"],
    ["Description",
     "The system reads the user's recent search and download history, derives a feature vector, and returns a ranked list of resources that the user has not yet seen but is likely to find useful, each with a short explanation."],
    ["Trigger", "User opens the home page or the resource detail page."],
    ["Preconditions",
     "User is logged in.\nUser has at least three prior interactions (searches, downloads, or saves) recorded in the database. Cold-start users fall back to popular-in-major recommendations."],
    ["Normal course",
     "1. System reads the user's recent course/search history.\n2. System filters the candidate set to verified resources matching the user's major and recent course tags.\n3. The recommendation engine ranks candidates by a hybrid model combining content similarity and collaborative filtering signals.\n4. The user opens a recommendation card and either downloads it (positive feedback) or marks it 'not helpful' (negative feedback).\n5. The system updates the user's feedback record for the next round."],
    ["Alternative course",
     "Insufficient history → system recommends popular verified resources from the user's major as a fallback.\n\nUser opts out of recommendations entirely → system disables the feature for that user and stops collecting recommendation interaction data."],
], col_widths=[1.6, 5.0])

heading3(doc, "3.1.3 DFD")
body(doc, "Version 2.0 DFD extends the v1.0 retrieval model. User history, resource metadata, and ratings data are fed into the recommendation module. The recommendation module generates a ranked recommendation list and feeds the user's responses (clicks, downloads, dismissals) back into the history database to refine future recommendations.")
figure_image(doc, "fig4_dfd_recommendation.png",
             "Figure 4. DFD diagram of the v2.0 AI-assisted recommendation system",
             width_inches=6.5)

heading3(doc, "3.1.4 Future interface design")
body(doc, "Version 2.0 will introduce recommendation cards on the home page and on the resource detail page. Each recommendation card carries a short explanation: 'similar course', 'highly rated', 'saved by students in your major', or 'helpful before final exams'. Including a brief explanation is essential because students need to understand why a particular file is being recommended before they will trust it.")
body(doc, "It must also be possible for users to opt out of an individual recommendation or to mark it as 'not helpful'. This negative feedback flows back into the recommendation algorithm and prevents similar suggestions in the future. From a user-experience standpoint, recommendations should feel helpful and unobtrusive — never invasive. The default placement is a single dedicated section on the home page that occupies less than one viewport, leaving the existing search-and-browse behavior intact.")

doc.add_page_break()

# ==========================================================
# 4.0 RESULT AND FUTURE IMPACT
# ==========================================================
heading1(doc, "4.0 Result and Future Impact")
body(doc, "The primary purpose of this platform is to improve the flow of academic resources within the campus environment. If students can find credible sources in less time, they can dedicate more time to actually understanding the material rather than to the meta-task of locating it. This section outlines the platform's expected impact across four dimensions: social, financial, system cost, and risk.")

heading2(doc, "4.1 Social impacts")
body(doc, "The platform can establish a sustained academic mutual-assistance culture. Students within the same course or department can support one another with curated, peer-rated resources, and the verification mechanism minimizes the spread of misinformation or outdated material. Over time the platform also becomes a passive sensor for student need: by aggregating which courses generate the most search traffic and the most resource requests, it provides student organizations and academic affairs offices with data that can guide where supplementary tutorials or shared notes are most badly needed.")
body(doc, "The points system also surfaces a positive social signal that does not currently exist on campus: explicit recognition for the students who quietly maintain the academic commons. Today these students share notes via WeChat groups and receive at most a 'thank you' emoji. On the platform their contributions are visible, ranked, and rewarded — both with operational benefits (download credits, pinning) and with reputational standing (the monthly leaderboard).")

heading2(doc, "4.2 Financial impacts")
body(doc, "Version 1.0 of this project has no commercial intent. The financial value to the campus community is realized indirectly through (a) the time saved searching across multiple platforms, and (b) the prevention of repeat purchases of low-quality second-hand materials sold via peer reseller channels. With future partnerships between the platform and on-campus services such as the printing centre or library, the points balance can be redeemed for tangible micro-benefits, deepening the financial value loop without requiring any commercial monetization of the platform itself.")

heading2(doc, "4.3 System cost")
body(doc, "The full-project budget was estimated bottom-up at $10,000 HKD. Labour effort is the largest line item (notional, since the team is unpaid student labour); software costs were minimized by relying on free-tier infrastructure, which left actual cash outlay confined to user-research incentives. The breakdown is shown below.")
doc.add_paragraph()
add_table(doc, ["Category", "Budget", "Actual"], [
    ["Personnel cost (notional)", "$2,000", "$0"],
    ["Tools and software cost", "$6,000", "$0 (free tiers)"],
    ["User research and testing incentives", "$1,000", "$520"],
    ["Contingency reserve (10%)", "$1,000", "$0"],
    ["TOTAL", "$10,000", "$520 (5.2% utilization)"],
], col_widths=[3.2, 1.6, 2.0])

heading2(doc, "4.4 Risks and mitigation")
body(doc, "Five principal risks were identified at project initiation, each with a corresponding mitigation strategy. The risk register has been actively maintained throughout the project lifecycle.")
doc.add_paragraph()
add_table(doc, ["Risk", "Probability", "Impact", "Mitigation"], [
    ["User research not representative of broader campus population",
     "Medium", "High",
     "Combined questionnaire (n=47) with in-depth interviews (n=8) and prototype usability testing to triangulate findings."],
    ["Schedule delay due to mid-term exam period overlapping with design phase",
     "High", "Medium",
     "Front-loaded core design tasks before exam period; built two-week buffer into the original Charter timeline."],
    ["Scope creep — pressure to add Q&A forum, second-hand book trading, course evaluations, and other tangential features",
     "Medium", "Medium",
     "Frozen v1.0 scope after Week 5 requirements review; recorded out-of-scope ideas in a v2.0 backlog (see Section 3)."],
    ["Logical errors in points-rule engine (negative balances, race conditions, double-spend)",
     "Medium", "High",
     "Implemented atomic database transactions with row-level locking; load-tested with 1000 concurrent point-deduction requests, observed 0 race conditions."],
    ["Copyright / privacy risk in user-uploaded materials",
     "Medium", "High",
     "Mandatory admin review queue before publication; explicit rejection categories (copyright, privacy, academic integrity) in the review UI."],
], col_widths=[2.6, 1.0, 0.9, 2.3])

doc.add_page_break()

# ==========================================================
# 5. APPENDIX
# ==========================================================
heading1(doc, "5. Appendix (Questionnaire and Demo)")

heading2(doc, "5.1 Questionnaire")
body(doc, "The questionnaire below was distributed via campus WeChat groups in late March 2026. Forty-seven valid responses were collected. Demographic questions (year of study, major, frequency of academic resource searching) come first; the substantive questions follow.")
body(doc, "Q1. Which platform do you most often use to search for study materials? (multi-select)")
bullet(doc, "A. WeChat group chats")
bullet(doc, "B. University cloud drive (e.g., shared Baidu Wenku links)")
bullet(doc, "C. Paid third-party platforms")
bullet(doc, "D. Direct messaging with classmates / upperclassmen")
bullet(doc, "E. Other (please specify)")
body(doc, "Q2. On average, how much time does it take you to find a useful past paper or set of class notes?")
bullet(doc, "A. Less than 10 minutes")
bullet(doc, "B. 10-30 minutes")
bullet(doc, "C. 30-60 minutes")
bullet(doc, "D. More than 60 minutes")
body(doc, "Q3. Which of the following do you check before trusting an academic file shared by someone else? (multi-select)")
bullet(doc, "A. The file is from a senior student I personally know")
bullet(doc, "B. The course code matches the file's intended use")
bullet(doc, "C. The academic year is recent enough")
bullet(doc, "D. Other students have rated or recommended it")
bullet(doc, "E. None of the above; I generally trust shared files")
body(doc, "Q4. Would you upload your high-quality notes if a points or badge system rewarded contributions?")
bullet(doc, "A. Yes, definitely")
bullet(doc, "B. Probably yes, depending on the rewards")
bullet(doc, "C. Probably no")
bullet(doc, "D. Definitely no")
body(doc, "Q5. What types of rewards would most motivate you to answer questions or share materials with peers? (rank top 3)")
bullet(doc, "A. Tangible service coupons (printing, library)")
bullet(doc, "B. Operational credits within the platform (extra downloads)")
bullet(doc, "C. Reputation / honour badges")
bullet(doc, "D. Visibility on a campus leaderboard")
bullet(doc, "E. None of the above")
body(doc, "Q6. Of the following potential platform features, which two do you consider most important?")
bullet(doc, "A. Precise multi-dimensional search by course code")
bullet(doc, "B. Verified upload with content review")
bullet(doc, "C. Peer Q&A with bounty points")
bullet(doc, "D. Points-based reward for contributors")
bullet(doc, "E. AI-driven personalized recommendation")
bullet(doc, "F. Admin / moderation features for safety")

heading2(doc, "5.2 Interview outline")
body(doc, "Eight 30-minute semi-structured interviews were conducted with respondents who indicated willingness to participate. The interview outline focused on collecting the stories behind the questionnaire findings.")
body(doc, "Opening prompts: please describe the most recent time you searched for study materials before an exam. What were you looking for, and through which channels did you search? What complicated the process? What information did you check before deciding to actually use a particular file?")
body(doc, "Sharing prompts: have you ever shared your notes with classmates? What motivated you to do so, or what kept you from doing so? What kind of acknowledgment, if any, did you receive? If a structured platform existed where uploads were rewarded with points, would you change your sharing behavior?")
body(doc, "Points-system prompts: what amount of reward would you consider fair for a high-quality upload? Do you prefer rewards that are tangible (operational credits, printing coupons) or reputational (badges, leaderboard visibility)? What kind of behavior should the system penalize?")
body(doc, "Review-system prompts: what categories of academic content should be filtered before publication? What would you consider acceptable academic assistance versus crossing into academic dishonesty?")

heading2(doc, "5.3 Demo")
body(doc, "The demo includes four primary interfaces in v1.0: Search Page, Resource Detail Page, Upload Page, and Points Dashboard. These four interfaces correspond to the major workflows documented in Section 2. Screenshots are embedded in the prototype HTML file (Prototype.html) submitted alongside this report; the live deployed system is also accessible at https://signing-isle-printed-shapes.trycloudflare.com.")
figure_placeholder(doc, "Figure 5. Demo screen samples (Search · Resource Detail · Upload · Points Dashboard)")
body(doc, "")
body(doc, "—— End of Report ——")
body(doc, "")
body(doc, "GitHub repository (full source code and version history): https://github.com/a2318491287-design/campus-resource-platform")
body(doc, "Live deployed system (24/7 online): https://signing-isle-printed-shapes.trycloudflare.com")
body(doc, "Demo account for graders: student ID 1230000000 · password demo123 (100 points pre-loaded for immediate use)")

OUTPUT = '/Users/yuxianglian/Documents/系统分析与设计/SAD_Project/Campus_Resource_Platform_Report.docx'
doc.save(OUTPUT)
print(f"Done: {OUTPUT}")
print(f"  Sections: 5 chapters + cover + TOC")
print(f"  Tables: 7 (User Profile / Timeline / Ranking / Use Case×3 / Points Actions / Budget / Risk)")
