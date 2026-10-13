"""Short presentation version of the original Standardization Pathfinder.
Keeps the original design, page order, and recommendation engine.
Starts blank. Shortens prompts within each stage rather than combining stages.
Run: python -m streamlit run standardization_pathfinder_demo.py
Requires streamlit>=1.54,<2. Requires streamlit-mic-recorder for speech-to-text.
"""

import re
import streamlit as st
from streamlit_mic_recorder import speech_to_text
import copy
import html

st.set_page_config(
    page_title="Standardization Pathfinder · Short demo",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# Visual design
# ============================================================

st.markdown(
    """
    <style>
        :root {
            --ink: #18241f;
            --muted: #69766f;
            --line: #e1e7e2;
            --panel: #ffffff;
            --cream: #f7f6f0;
            --forest: #315843;
            --forest-dark: #173a2b;
            --sage: #7c9b83;
            --blue: #4d7781;
        }

        .stApp {
            background:
                radial-gradient(circle at 88% 8%, rgba(105,145,120,.09), transparent 25rem),
                linear-gradient(180deg, #fafbf8 0%, #f3f5f1 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1120px;
            padding-top: 1.35rem;
            padding-bottom: 4rem;
        }

        #MainMenu, footer {visibility: hidden;}

        .topbar {
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:.9rem;
            gap:1rem;
        }

        .brand {
            font-weight:800;
            letter-spacing:-.025em;
            color:#173a2b;
            font-size:1.08rem;
        }

        .session-note {
            color:var(--muted);
            font-size:.83rem;
        }

        /* ---------- LANDING ILLUSTRATION ---------- */

        .landing-shell {
            position:relative;
            min-height:640px;
            overflow:hidden;
            border-radius:32px;
            margin-top:.65rem;
            box-shadow:0 28px 80px rgba(31,60,45,.20);
            background:#adc9c1;
            isolation:isolate;
        }

        .landing-sky {
            position:absolute;
            inset:0;
            background:
                radial-gradient(circle at 76% 15%, rgba(255,246,199,.95) 0 4%, rgba(255,246,199,.33) 10%, transparent 23%),
                linear-gradient(180deg,#a9cac8 0%,#dfe4d5 55%,#bbcbb8 100%);
            z-index:0;
        }

        .mist {
            position:absolute;
            left:-8%;
            right:-8%;
            top:37%;
            height:18%;
            background:rgba(244,247,239,.32);
            filter:blur(18px);
            z-index:1;
        }

        .mountains-back {
            position:absolute;
            inset:auto -5% 30% -5%;
            height:43%;
            background:#78988a;
            clip-path:polygon(
                0 66%, 7% 54%, 14% 60%, 23% 30%, 31% 55%,
                39% 39%, 46% 57%, 55% 20%, 64% 53%, 72% 35%,
                80% 56%, 89% 28%, 100% 50%, 100% 100%, 0 100%
            );
            z-index:1;
        }

        .mountains-front {
            position:absolute;
            inset:auto -5% 12% -5%;
            height:48%;
            background:#4d745d;
            clip-path:polygon(
                0 57%, 8% 35%, 17% 58%, 26% 27%, 36% 55%,
                46% 31%, 57% 60%, 67% 23%, 78% 54%, 87% 32%,
                95% 49%, 100% 38%, 100% 100%, 0 100%
            );
            z-index:2;
        }

        .forest-floor {
            position:absolute;
            left:0;
            right:0;
            bottom:0;
            height:33%;
            background:linear-gradient(180deg,#496d52 0%,#274835 100%);
            z-index:2;
        }

        .path {
            position:absolute;
            z-index:3;
            left:50%;
            bottom:-5%;
            width:57%;
            height:64%;
            transform:translateX(-50%);
            background:
                linear-gradient(90deg, rgba(126,100,64,.12), transparent 20%, transparent 80%, rgba(126,100,64,.12)),
                linear-gradient(180deg,#dfcfa9 0%,#c8b17f 100%);
            clip-path:polygon(
                48% 0%, 53% 0%,
                59% 15%, 51% 29%, 62% 43%,
                55% 56%, 72% 72%, 100% 100%,
                0 100%, 31% 72%, 45% 57%,
                38% 43%, 47% 29%, 43% 15%
            );
        }

        .tree {
            position:absolute;
            z-index:4;
            width:0;
            height:0;
            border-left:44px solid transparent;
            border-right:44px solid transparent;
            border-bottom:120px solid #1f4633;
            filter:drop-shadow(0 10px 8px rgba(21,45,33,.15));
        }

        .tree:before {
            content:"";
            position:absolute;
            left:-37px;
            top:34px;
            width:0;
            height:0;
            border-left:37px solid transparent;
            border-right:37px solid transparent;
            border-bottom:105px solid #2a553d;
        }

        .tree:after {
            content:"";
            position:absolute;
            left:-29px;
            top:65px;
            width:0;
            height:0;
            border-left:29px solid transparent;
            border-right:29px solid transparent;
            border-bottom:90px solid #37684a;
        }

        .tree.t1 {left:5%; bottom:7%; transform:scale(1.58);}
        .tree.t2 {left:17%; bottom:18%; transform:scale(1.02);}
        .tree.t3 {left:28%; bottom:26%; transform:scale(.62);}
        .tree.t4 {right:6%; bottom:6%; transform:scale(1.52);}
        .tree.t5 {right:19%; bottom:17%; transform:scale(1.03);}
        .tree.t6 {right:30%; bottom:27%; transform:scale(.62);}

        .landing-overlay {
            position:relative;
            z-index:10;
            min-height:640px;
            display:flex;
            align-items:center;
            padding:4rem 4.2rem;
            background:
                linear-gradient(90deg,
                    rgba(16,44,32,.88) 0%,
                    rgba(16,44,32,.68) 38%,
                    rgba(16,44,32,.24) 65%,
                    rgba(16,44,32,.03) 100%);
        }

        .landing-copy {
            max-width:610px;
            color:white;
        }

        .landing-eyebrow {
            display:inline-flex;
            align-items:center;
            gap:.5rem;
            padding:.45rem .75rem;
            border:1px solid rgba(255,255,255,.28);
            border-radius:999px;
            background:rgba(255,255,255,.10);
            backdrop-filter:blur(8px);
            font-size:.76rem;
            font-weight:800;
            letter-spacing:.13em;
            text-transform:uppercase;
            margin-bottom:1rem;
        }

        .landing-copy h1 {
            color:white;
            font-size:clamp(3rem,6vw,5.25rem);
            line-height:.94;
            letter-spacing:-.06em;
            max-width:570px;
            margin:0 0 1.25rem 0;
        }

        .landing-copy p {
            color:rgba(255,255,255,.91);
            font-size:1.15rem;
            line-height:1.64;
            max-width:590px;
            margin:0;
        }

        .journey-strip {
            display:grid;
            grid-template-columns:repeat(3,1fr);
            gap:.85rem;
            margin:1rem 0 1.25rem 0;
        }

        .journey-stop {
            background:rgba(255,255,255,.96);
            border:1px solid var(--line);
            border-radius:17px;
            padding:1rem 1.1rem;
            box-shadow:0 8px 25px rgba(20,42,31,.04);
        }

        .journey-stop .num {
            width:29px;
            height:29px;
            border-radius:50%;
            display:flex;
            align-items:center;
            justify-content:center;
            background:#315843;
            color:white;
            font-size:.8rem;
            font-weight:800;
            margin-bottom:.62rem;
        }

        .journey-stop b {
            display:block;
            color:#173a2b;
            margin-bottom:.28rem;
        }

        .journey-stop span {
            color:var(--muted);
            font-size:.9rem;
            line-height:1.47;
        }

        /* ---------- INTERNAL PAGES ---------- */

        .step-strip {
            display:grid;
            grid-template-columns:repeat(6,1fr);
            gap:.45rem;
            margin:1.15rem 0 1.5rem 0;
        }

        .step {
            min-height:5px;
            border-radius:999px;
            background:#dfe5e0;
        }
        .step.done {background:#83a18c;}
        .step.active {background:#315843;}

        .page-heading {margin:.35rem 0 1.35rem 0;}
        .page-heading .eyebrow {
            color:#315843;
            font-size:.77rem;
            font-weight:800;
            letter-spacing:.12em;
            text-transform:uppercase;
            margin-bottom:.35rem;
        }
        .page-heading h2 {
            color:var(--ink);
            font-size:2rem;
            letter-spacing:-.035em;
            margin:0 0 .38rem 0;
        }
        .page-heading p {
            color:var(--muted);
            margin:0;
            line-height:1.55;
            max-width:820px;
        }

        .prompt-card {
            background:#edf4ef;
            border:1px solid #d9e7dd;
            color:#315843;
            border-radius:16px;
            padding:1rem 1.1rem;
            margin:.45rem 0 1rem 0;
        }

        .microcopy {
            color:var(--muted);
            font-size:.88rem;
            margin-top:-.2rem;
            margin-bottom:.7rem;
        }

        .result-hero {
            background:linear-gradient(135deg,#173a2b 0%,#315843 100%);
            color:white;
            border-radius:22px;
            padding:2rem 2.1rem;
            box-shadow:0 16px 44px rgba(21,50,36,.14);
            margin-bottom:1.2rem;
        }

        .result-hero .label {
            text-transform:uppercase;
            font-size:.74rem;
            letter-spacing:.13em;
            opacity:.75;
            font-weight:800;
        }

        .result-hero h2 {
            color:white;
            font-size:2.15rem;
            margin:.35rem 0 .6rem 0;
        }

        .result-hero p {
            color:rgba(255,255,255,.89);
            max-width:820px;
            line-height:1.55;
        }

        .badge-row {
            display:flex;
            gap:.45rem;
            flex-wrap:wrap;
            margin-top:.8rem;
        }

        .badge {
            display:inline-flex;
            border-radius:999px;
            padding:.34rem .68rem;
            background:rgba(255,255,255,.12);
            border:1px solid rgba(255,255,255,.18);
            font-size:.82rem;
            font-weight:650;
            color:white;
        }

        .fit-card {
            background:white;
            border:1px solid var(--line);
            border-radius:16px;
            padding:1.15rem 1.25rem;
            min-height:210px;
        }

        .fit-card h4 {margin:0 0 .35rem 0;}
        .score {
            font-size:1.7rem;
            font-weight:800;
            color:#315843;
            letter-spacing:-.03em;
        }
        .why {
            color:#55625b;
            font-size:.92rem;
            line-height:1.48;
        }

        .review-k {
            font-size:.76rem;
            color:var(--muted);
            font-weight:800;
            text-transform:uppercase;
            letter-spacing:.06em;
            margin-bottom:.2rem;
        }
        .review-v {
            color:var(--ink);
            white-space:pre-wrap;
            margin-bottom:.9rem;
            line-height:1.5;
        }

        .framework-step {
            background:white;
            border:1px solid var(--line);
            border-radius:14px;
            padding:1rem 1.1rem;
            margin-bottom:.65rem;
        }

        .framework-step .n {
            display:inline-flex;
            align-items:center;
            justify-content:center;
            width:27px;
            height:27px;
            border-radius:50%;
            background:#315843;
            color:white;
            font-size:.78rem;
            font-weight:800;
            margin-right:.55rem;
        }

        div[data-testid="stProgress"] > div > div > div > div {
            background-color:#315843;
        }

        div.stButton > button {
            border-radius:12px;
            min-height:2.8rem;
            font-weight:700;
        }

        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="input"] input {
            border-radius:12px !important;
        }

        @media (max-width:800px) {
            .landing-shell,
            .landing-overlay {min-height:570px;}
            .landing-overlay {
                align-items:flex-end;
                padding:2.3rem 1.6rem;
                background:linear-gradient(0deg,
                    rgba(16,44,32,.91) 0%,
                    rgba(16,44,32,.63) 52%,
                    rgba(16,44,32,.08) 100%);
            }
            .landing-copy h1 {font-size:3.1rem;}
            .journey-strip {grid-template-columns:1fr;}
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Content
# ============================================================

PAGES = [
    "Welcome",
    "Define the problem",
    "Understand the current state",
    "Size the issue",
    "Imagine the better way",
    "Solution fit",
    "Review",
    "Recommendation",
]

ROOT_CAUSE_CATEGORIES = [
    "Lack of clarity",
    "Knowledge gap",
    "Process not defined",
    "Process not followed",
    "Missing ownership",
    "Unclear roles or responsibilities",
    "Unclear decision authority",
    "Information not captured",
    "Information captured too late",
    "Information difficult to find",
    "Information scattered across locations",
    "Information not current",
    "Duplicate effort",
    "Manual data transfer",
    "Repetitive calculations",
    "Repetitive administrative work",
    "High complexity",
    "Too many handoffs",
    "Lack of standard inputs",
    "Lack of standard outputs",
    "Inconsistent terminology",
    "Inconsistent file structure or naming",
    "Insufficient QA/QC",
    "Late QA/QC",
    "No feedback loop",
    "System limitations",
    "Systems do not integrate",
]

SCOPE_OPTIONS = [
    "One specific project or task type",
    "Several related project or task types",
    "Most projects or tasks in a team",
    "Organization-wide or cross-team",
]

FREQUENCY_OPTIONS = [
    "Less than once per project / occurrence",
    "About once per project / occurrence",
    "2–3 times per project / occurrence",
    "4+ times per project / occurrence",
    "Daily or near-daily operational work",
]

USER_OPTIONS = [
    "1 person",
    "2–5 people",
    "6–20 people",
    "21–50 people",
    "More than 50 people",
]

VARIABILITY_OPTIONS = [
    "Low — the same logic and steps apply most of the time",
    "Moderate — there are a few recurring pathways or scenarios",
    "High — the work changes substantially case by case",
]

DATA_SHAPE_OPTIONS = [
    "Mostly narrative / documents",
    "Mostly structured rows, columns, tables, or parameters",
    "A mix of structured data and narrative information",
    "Mostly files moving between systems",
]

SOLUTION_CATEGORIES = {
    "Document based": [
        "SOP / procedure document",
        "Technical guidance document",
        "Reference guide",
        "Checklist",
        "Requirements matrix",
        "Report template",
        "Training material",
        "Example deliverable",
    ],
    "Spreadsheet based": [
        "Excel calculation workbook",
        "Macro-enabled workbook",
        "Standard input / parameter lookup table",
    ],
    "Process based": [
        "Process adjustment",
        "Clear roles / responsibilities / expectations",
        "Standardized workflow",
        "Decision tree",
        "Standard folder structure",
        "Standard naming conventions",
    ],
    "Code based": [
        "Standalone code or script",
        "Executable tool",
    ],
    "App based": [
        "Internal app",
        "Web-based tool",
        "Mobile or field app",
        "Guided decision-support tool",
    ],
}

EXCEL_BUILD_FRAMEWORK = [
    ("Define calculation scope", "Start with the final outputs. Identify major calculation components, supported scenarios, and anything intentionally excluded."),
    ("Identify governing requirements", "Gather the methodology, standard, procedure, equations, tables, and internal requirements that affect the calculation."),
    ("Map the calculation logic", "Work backward from final results through calculation components, decision points, intermediate results, and aggregation."),
    ("Define inputs and parameters", "Separate project-specific user inputs from controlled parameters, lookup values, units, sources, and conditions."),
    ("Define the data structure", "Decide what one row represents and which fields uniquely define a record before building input tables."),
    ("Design the workbook", "Create only the worksheets needed for instructions, inputs, parameters, calculations, QA/QC, results, and change control."),
    ("Build inputs and parameters", "Use clear editable cells, units, dropdowns, validation rules, Excel Tables, and centralized controlled parameters."),
    ("Build and verify calculations", "Build in logical modules, expose useful intermediate results, and check each component independently."),
    ("Build aggregation and final results", "Define sums, means, weighting, ratios, or other required rollups and reconcile outputs to detailed records."),
    ("Add QA/QC controls", "Target missing inputs, invalid values, inconsistent dates, duplicates, missing parameters, incompatible selections, and reconciliation failures."),
    ("Test the complete workbook", "Test known-value examples, realistic data, blanks, zeros, optional pathways, boundary values, copied data, and added rows."),
    ("Finalize and release", "Add version information, source references, owner, instructions, change log, appropriate protection, and independent user testing."),
]

DEFAULTS = {
    "page": 0,
    "problem_title": "",
    "pain_point": "",
    "why_matter": "",
    "current_workflow": "",
    "existing_tools": "",
    "root_causes": [],
    "root_cause_details": "",
    "scope": SCOPE_OPTIONS[0],
    "frequency": FREQUENCY_OPTIONS[1],
    "user_count": USER_OPTIONS[1],
    "time_hours": 1.0,
    "bau_outcome": "",
    "daydream": "",
    "desired_outcome": "",
    "data_shape": DATA_SHAPE_OPTIONS[1],
    "variability": VARIABILITY_OPTIONS[1],
    "calculation_heavy": False,
    "comparison_needed": False,
    "standard_inputs": False,
    "standard_outputs": False,
    "repeatable_decisions": False,
    "qa_important": False,
    "excel_native": False,
    "file_processing": False,
    "central_multiuser": False,
    "real_time": False,
    "offline": False,
    "nontechnical": True,
}

# Blank answers; preserve widget values between pages.
DEFAULTS.update(scope=None, frequency=None, user_count=None, time_hours=None,
                data_shape=None, variability=None, nontechnical=False)
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = copy.deepcopy(v)
    else:
        st.session_state[k] = st.session_state[k]

# ============================================================
# Helpers
# ============================================================

def goto(index):
    st.session_state.page = max(0, min(index, len(PAGES) - 1))
    st.rerun()

def reset_app():
    for k, v in DEFAULTS.items():
        st.session_state[k] = copy.deepcopy(v)
    st.rerun()

def topbar():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">Standardization Pathfinder</div>
            <div class="session-note">Session only · nothing is saved</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def step_strip():
    if st.session_state.page == 0:
        return

    current = st.session_state.page
    total = 6
    html = '<div class="step-strip">'
    for i in range(1, total + 1):
        cls = "step"
        if i < current:
            cls += " done"
        elif i == current:
            cls += " active"
        html += f'<div class="{cls}"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    if current <= total:
        st.caption(f"Part {current} of {total} · {PAGES[current]}")
    else:
        st.caption("Recommendation")

def heading(kicker, title, text):
    st.markdown(
        f"""
        <div class="page-heading">
            <div class="eyebrow">{kicker}</div>
            <h2>{title}</h2>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def nav(next_disabled=False, next_label="Continue", back=True):
    left, middle, right = st.columns([1.1, 5.3, 1.35])
    with left:
        if back and st.button("Back", width="stretch"):
            goto(st.session_state.page - 1)
    with right:
        if st.button(next_label, type="primary", width="stretch", disabled=next_disabled):
            goto(st.session_state.page + 1)

def voice_textarea(label, key, placeholder="", height=140, help_text=None):
    st.markdown(f"**{label}**")
    if help_text:
        st.markdown(f'<div class="microcopy">{help_text}</div>', unsafe_allow_html=True)

    mic, note = st.columns([1.1, 4.9])
    with mic:
        transcript = speech_to_text(
            language="en",
            start_prompt="🎙 Speak",
            stop_prompt="Stop",
            just_once=True,
            use_container_width=True,
            key=f"{key}_speech",
        )

    if transcript:
        existing = st.session_state.get(key, "").strip()
        addition = transcript.strip()
        st.session_state[key] = f"{existing} {addition}".strip() if existing else addition

    with note:
        st.caption("Type normally, or use the microphone and your words will be added below.")

    return st.text_area(
        label,
        key=key,
        placeholder=placeholder,
        height=height,
        label_visibility="collapsed",
    )

def normalized_text(text):
    return re.sub(r"\s+", " ", (text or "").lower()).strip()

def recommendation_engine():
    roots = set(st.session_state.root_causes)
    daydream = normalized_text(st.session_state.daydream)
    workflow = normalized_text(st.session_state.current_workflow)
    tools = normalized_text(st.session_state.existing_tools)
    desired = normalized_text(st.session_state.desired_outcome)
    combined = " ".join([daydream, workflow, tools, desired])

    scores = {
        "Excel calculation workbook": 0,
        "Macro-enabled workbook": 0,
        "Checklist": 0,
        "SOP / procedure document": 0,
        "Requirements matrix": 0,
        "Reference guide": 0,
        "Process adjustment": 0,
        "Clear roles / responsibilities / expectations": 0,
        "Standardized workflow": 0,
        "Decision tree": 0,
        "Standalone code or script": 0,
        "Executable tool": 0,
        "Internal app": 0,
        "Guided decision-support tool": 0,
        "Report template": 0,
        "Standard input / parameter lookup table": 0,
    }

    why = {k: [] for k in scores}

    def add(name, points, reason=None):
        scores[name] += points
        if reason and reason not in why[name]:
            why[name].append(reason)

    # Strong spreadsheet weighting for transparent, structured calculation work
    if st.session_state.calculation_heavy:
        add("Excel calculation workbook", 9, "The work contains repeatable calculations.")
        add("Macro-enabled workbook", 5)
        add("Standalone code or script", 3)
        add("Internal app", 2)

    if st.session_state.data_shape.startswith("Mostly structured"):
        add("Excel calculation workbook", 5, "The information naturally fits rows, columns, tables, and parameters.")
        add("Standard input / parameter lookup table", 4)
        add("Standalone code or script", 2)

    if st.session_state.comparison_needed:
        add("Excel calculation workbook", 5, "The desired output includes a direct comparison of results.")
        add("Report template", 1)

    if st.session_state.standard_inputs:
        add("Excel calculation workbook", 3, "Standardized inputs are part of the future state.")
        add("Standard input / parameter lookup table", 5)
        add("Internal app", 2)

    if st.session_state.standard_outputs:
        add("Excel calculation workbook", 3, "Standardized outputs are required.")
        add("Report template", 3)
        add("Internal app", 2)

    if st.session_state.qa_important:
        add("Excel calculation workbook", 3, "Transparent QA/QC and reviewability are important.")
        add("Checklist", 3)
        add("Requirements matrix", 2)
        add("Internal app", 1)

    if st.session_state.excel_native or any(x in combined for x in ["excel", "workbook", "spreadsheet"]):
        add("Excel calculation workbook", 10, "The existing or ideal workflow is explicitly Excel/workbook-based.")
        add("Macro-enabled workbook", 4)

    if any(x in daydream for x in ["calculation workbook", "excel workbook", "spreadsheet", "workbook"]):
        add("Excel calculation workbook", 10, "Your ideal future state explicitly describes a workbook.")
        add("Internal app", -3)

    # Documents and controls
    if roots & {"Process not defined", "Lack of clarity", "Process not followed"}:
        add("SOP / procedure document", 6, "The root cause includes process clarity or definition.")
        add("Checklist", 3)

    if roots & {"Knowledge gap", "Information difficult to find", "Information scattered across locations", "Information not current"}:
        add("Reference guide", 6, "The main issue includes finding or understanding information.")
        add("SOP / procedure document", 2)

    if roots & {"Insufficient QA/QC", "Late QA/QC"}:
        add("Checklist", 6, "The root cause includes missing or late QA/QC.")
        add("Requirements matrix", 3)
        add("Excel calculation workbook", 2)

    if roots & {"Lack of standard inputs", "Information not captured"}:
        add("Standard input / parameter lookup table", 5)
        add("Excel calculation workbook", 2)

    if roots & {"Lack of standard outputs"}:
        add("Report template", 5)
        add("Excel calculation workbook", 2)

    # Process / ownership
    if roots & {"Missing ownership", "Unclear roles or responsibilities", "Unclear decision authority"}:
        add("Clear roles / responsibilities / expectations", 9, "The root cause is primarily ownership or responsibility.")
        add("Process adjustment", 5)
        add("Standardized workflow", 4)
        add("Internal app", -2)

    if roots & {"Too many handoffs", "No feedback loop"}:
        add("Process adjustment", 7, "The issue is structural in the workflow.")
        add("Standardized workflow", 6)

    # Code
    if roots & {"Manual data transfer", "Repetitive administrative work", "Duplicate effort"}:
        add("Standalone code or script", 5, "Automation could remove repetitive data handling.")
        add("Executable tool", 4)
        add("Macro-enabled workbook", 3)

    if st.session_state.file_processing:
        add("Standalone code or script", 7, "The work involves repeatable file or data processing.")
        add("Executable tool", 5)
        add("Internal app", 2)

    # Decision support
    if st.session_state.repeatable_decisions:
        add("Decision tree", 5, "The work contains repeatable decision logic.")
        add("Guided decision-support tool", 5)
        add("Internal app", 2)
        if st.session_state.variability.startswith("Moderate"):
            add("Excel calculation workbook", 2)

    # App should require app-specific needs
    if st.session_state.central_multiuser:
        add("Internal app", 8, "Multiple users need a shared, centralized interface or source of truth.")
        add("Guided decision-support tool", 4)

    if st.session_state.real_time:
        add("Internal app", 7, "The process benefits from real-time shared state or immediate cross-user updates.")
        add("Standalone code or script", 2)

    if st.session_state.user_count in {"21–50 people", "More than 50 people"}:
        add("Internal app", 4, "The solution may need to serve a larger user group.")
        add("SOP / procedure document", 2)

    if st.session_state.user_count in {"1 person", "2–5 people"}:
        add("Excel calculation workbook", 2)
        add("Internal app", -2)

    if st.session_state.offline:
        add("Excel calculation workbook", 3)
        add("Executable tool", 2)
        add("Internal app", -4, "Offline use makes a hosted app less attractive.")

    if st.session_state.nontechnical:
        add("Excel calculation workbook", 2, "The primary users are nontechnical and a familiar interface may reduce adoption friction.")
        add("Checklist", 1)
        add("Internal app", 1)

    if st.session_state.variability.startswith("High"):
        add("SOP / procedure document", -2)
        add("Excel calculation workbook", -1)
        add("Guided decision-support tool", 3)

    if st.session_state.data_shape.startswith("Mostly narrative"):
        add("Reference guide", 3)
        add("SOP / procedure document", 2)
        add("Excel calculation workbook", -3)

    # Avoid "complex = app"
    if not st.session_state.central_multiuser and not st.session_state.real_time:
        add("Internal app", -3)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked, why

def category_for(solution):
    for category, options in SOLUTION_CATEGORIES.items():
        if solution in options:
            return category
    return "Other"

def solution_description(solution):
    descriptions = {
        "Excel calculation workbook": "A transparent, structured workbook with controlled inputs, parameters, calculation modules, QA/QC, and clear results.",
        "Macro-enabled workbook": "An Excel workbook with controlled VBA automation where ordinary formulas are not enough.",
        "Checklist": "A lightweight execution or QA/QC aid for a process that largely already exists.",
        "SOP / procedure document": "A durable written process defining what to do, when, and how.",
        "Requirements matrix": "A structured mapping between requirements, evidence, calculations, controls, or outputs.",
        "Reference guide": "A concise source of truth for information users currently have to search for or remember.",
        "Process adjustment": "A change to the workflow itself rather than creation of a new technical tool.",
        "Clear roles / responsibilities / expectations": "Explicit ownership and responsibility definitions where ambiguity is the core problem.",
        "Standardized workflow": "A consistent sequence of tasks, handoffs, and controls.",
        "Decision tree": "A visual or structured way to guide repeatable choices.",
        "Standalone code or script": "Code that automates repeated processing, calculations, transformations, or file handling.",
        "Executable tool": "Packaged code for users who need automation without interacting directly with source code.",
        "Internal app": "A shared interactive interface suited to centralized multi-user workflows, cross-user state, or app-like interaction.",
        "Guided decision-support tool": "An interactive tool that walks users through recurring decision logic and produces a standardized result.",
        "Report template": "A standardized structure for recurring outputs and reporting.",
        "Standard input / parameter lookup table": "A controlled source for recurring values, factors, units, mappings, and allowed inputs.",
    }
    return descriptions.get(solution, "")

# ============================================================
# Pages
# ============================================================

topbar()
step_strip()
page = st.session_state.page

if page == 0:
    landing_html = """<div class="landing-shell">
<div class="landing-sky"></div>
<div class="mist"></div>
<div class="mountains-back"></div>
<div class="mountains-front"></div>
<div class="forest-floor"></div>
<div class="path"></div>
<div class="tree t1"></div>
<div class="tree t2"></div>
<div class="tree t3"></div>
<div class="tree t4"></div>
<div class="tree t5"></div>
<div class="tree t6"></div>
<div class="landing-overlay">
<div class="landing-copy">
<div class="landing-eyebrow">🧭 Standardization Pathfinder</div>
<h1>Find the clearest path forward.</h1>
<p>Every recurring problem does not need an app. Follow the trail from friction to root cause, picture the better way, and discover the simplest standardization that actually fits.</p>
</div>
</div>
</div>"""
    st.markdown(landing_html, unsafe_allow_html=True)

    journey_html = """<div class="journey-strip">
<div class="journey-stop">
<div class="num">1</div>
<b>Notice the friction</b>
<span>Capture what is slow, inconsistent, repetitive, unclear, or risky.</span>
</div>
<div class="journey-stop">
<div class="num">2</div>
<b>Follow it to the source</b>
<span>Understand the workflow, root cause, scale, and what happens if nothing changes.</span>
</div>
<div class="journey-stop">
<div class="num">3</div>
<b>Choose the best path forward</b>
<span>Match the problem to a practical document, workbook, process, code, or app solution.</span>
</div>
</div>"""
    st.markdown(journey_html, unsafe_allow_html=True)

    _, center, _ = st.columns([2.0, 2.0, 2.0])
    with center:
        if st.button("Begin the journey  →", type="primary", width="stretch"):
            goto(1)

    st.caption("Short presentation version · Type or use the microphone on longer questions.")

elif page == 1:
    heading(
        "Part 1 · Define",
        "What are you actually trying to fix?",
        "Keep the description factual and neutral. Focus on the recurring problem and its consequence, not the solution you already have in mind.",
    )
    with st.container(border=True):
        st.text_input('Problem title', key='problem_title', placeholder='A short name you would recognize later')
        voice_textarea('Pain point', 'pain_point', placeholder='Describe the issue in two or three sentences.', height=130, help_text='What is difficult, slow, inconsistent, error-prone, or frustrating?')
        voice_textarea('Why does it matter?', 'why_matter', placeholder='Describe the result of the pain point in one sentence.', height=100, help_text='Think time, quality, error risk, rework, consistency, cost, or employee experience.')
    complete = all(st.session_state[k].strip() for k in ("problem_title", "pain_point", "why_matter"))
    nav(next_disabled=not complete)

elif page == 2:
    heading(
        "Part 2 · Current state",
        "Walk through what happens today.",
        "Include the real workarounds, manual checks, handoffs, and existing controls. Hidden manual work is often where the best standardization opportunities appear.",
    )
    voice_textarea('Current workflow', 'current_workflow', placeholder='Describe what happens from the start of the task to the end. Include manual checks and handoffs.', height=130)
    voice_textarea('Existing tools and controls', 'existing_tools', placeholder='What spreadsheets, templates, SOPs, systems, scripts, reviews, checklists, or informal workarounds already exist?', height=100)
    st.markdown("#### What is driving the problem?")
    st.multiselect('Root cause categories', ROOT_CAUSE_CATEGORIES, key='root_causes', placeholder='Choose all that materially contribute', label_visibility='collapsed')
    nav(next_disabled=not (st.session_state.current_workflow.strip() and st.session_state.root_causes))

elif page == 3:
    heading(
        "Part 3 · Practicalities",
        "How big is the problem in practice?",
        "Scope, frequency, users, and time help distinguish a one-off annoyance from something worth standardizing heavily.",
    )
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox('Scope of the issue', SCOPE_OPTIONS, key='scope', index=None, placeholder='Choose the scope')
        st.selectbox('How often does it occur?', FREQUENCY_OPTIONS, key='frequency', index=None, placeholder='Choose the frequency')
    with c2:
        st.selectbox('How many people execute the current workflow?', USER_OPTIONS, key='user_count', index=None, placeholder='Choose the user group')
        st.number_input('Approximate time spent each time the workflow occurs (hours)', min_value=0.0, max_value=1000.0, step=0.5, value=None, key='time_hours', placeholder='Enter the hours')
    nav(next_disabled=any(st.session_state[k] is None for k in ("scope", "frequency", "user_count", "time_hours")))

elif page == 4:
    heading(
        "Part 4 · Daydream",
        "Ignore constraints for a minute.",
        "If you had unlimited time, resources, and technical capability, what would the best version of this process look like?",
    )
    st.markdown(
        """
        <div class="prompt-card">
            <b>This answer matters.</b> Describe the experience you actually want. If the ideal
            future state is a clean Excel workbook with controlled inputs and comparison outputs,
            Pathfinder treats that as evidence for an Excel solution rather than escalating to an app.
        </div>
        """,
        unsafe_allow_html=True,
    )

    voice_textarea('Your ideal future state', 'daydream', placeholder='Describe what users would do, what the tool or process would do automatically, and what they would see at the end.', height=160)
    voice_textarea('What would success look like?', 'desired_outcome', placeholder='Describe the practical outcome you want after standardization is implemented.', height=100)
    nav(next_disabled=not (st.session_state.daydream.strip() and st.session_state.desired_outcome.strip()))

elif page == 5:
    heading(
        "Part 5 · Solution fit",
        "What does the solution actually need to do?",
        "These characteristics distinguish an SOP from a workbook, a workbook from code, and code from an app.",
    )

    c1, c2 = st.columns(2)
    with c1:
        st.selectbox('What kind of information dominates the work?', DATA_SHAPE_OPTIONS, key='data_shape', index=None, placeholder='Choose the information type')
        st.selectbox('How variable is the logic or workflow?', VARIABILITY_OPTIONS, key='variability', index=None, placeholder='Choose the variability')
    with c2:
        st.checkbox('The work contains repeatable calculations', key='calculation_heavy')
        st.checkbox('Users need to compare independently calculated results', key='comparison_needed')
        st.checkbox('The process is already Excel / spreadsheet native', key='excel_native')
        st.checkbox('The work includes repeated file or data processing', key='file_processing')

    st.markdown("#### Standardization needs")
    a, b, c = st.columns(3)
    with a:
        st.checkbox('Standard inputs', key='standard_inputs')
        st.checkbox('Standard outputs', key='standard_outputs')
    with b:
        st.checkbox('Repeatable decision logic', key='repeatable_decisions')
        st.checkbox('Strong QA/QC or traceability', key='qa_important')
    with c:
        st.checkbox('Shared centralized multi-user state', key='central_multiuser')
        st.checkbox('Real-time cross-user updates', key='real_time')

    st.markdown("#### Practical constraints")
    d, e = st.columns(2)
    with d:
        st.checkbox('Should work offline', key='offline')
    with e:
        st.checkbox('Primary users are nontechnical', key='nontechnical')

    nav(next_disabled=st.session_state.data_shape is None or st.session_state.variability is None)

elif page == 6:
    heading(
        "Review",
        "Does this describe the problem accurately?",
        "Review the full story before Pathfinder recommends a solution. Go back if anything important is missing.",
    )

    sections = [
        ("Problem", [("Title", st.session_state.problem_title),
                     ("Pain point", st.session_state.pain_point),
                     ("Why it matters", st.session_state.why_matter)]),
        ("Current state", [("Workflow", st.session_state.current_workflow),
                           ("Tools", st.session_state.existing_tools or "Not provided"),
                           ("Root causes", ", ".join(st.session_state.root_causes))]),
        ("Practicalities", [("Scope", st.session_state.scope), ("Frequency", st.session_state.frequency),
                           ("People", st.session_state.user_count),
                           ("Time per occurrence", f"{st.session_state.time_hours:g} hours")]),
        ("Future state", [("Ideal future state", st.session_state.daydream),
                          ("Success", st.session_state.desired_outcome)]),
    ]
    for row in (sections[:2], sections[2:]):
        for col, (title, items) in zip(st.columns(2), row):
            with col:
                with st.container(border=True):
                    st.markdown(f"#### {title}")
                    for k, v in items:
                        st.markdown(f"**{k}:** {html.escape(str(v))}")

    nav(next_label="Find my solution")

elif page == 7:
    ranked, why = recommendation_engine()
    top_name, top_score = ranked[0]

    st.markdown(
        f"""
        <div class="result-hero">
            <div class="label">Best-fit standardization</div>
            <h2>{top_name}</h2>
            <p>{solution_description(top_name)}</p>
            <div class="badge-row">
                <span class="badge">{category_for(top_name)}</span>
                <span class="badge">Fit score {top_score}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if why[top_name]:
        st.markdown("### Why this fits")
        for reason in why[top_name][:5]:
            st.markdown(f"- {reason}")

    st.markdown("### Strong alternatives")
    cols = st.columns(3)
    alternatives = ranked[1:4]
    highest = max(max(v for _, v in ranked), 1)

    for col, (name, score) in zip(cols, alternatives):
        with col:
            pct = max(0, min(100, round(score / highest * 100)))
            st.markdown(
                f"""
                <div class="fit-card">
                    <div class="review-k">{category_for(name)}</div>
                    <h4>{name}</h4>
                    <div class="score">{pct}%</div>
                    <div class="why">{solution_description(name)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    with st.expander("See the full comparison"):
        for name, score in ranked:
            pct = max(0, min(100, round(score / highest * 100)))
            st.markdown(f"**{name}** · {category_for(name)}")
            st.progress(pct)
            if why[name]:
                st.caption(why[name][0])
            else:
                st.caption(solution_description(name))

    if top_name == "Excel calculation workbook":
        with st.expander("Build your workbook · Next steps"):
            st.markdown("## Build your workbook")
            st.write(
                "Pathfinder identified a calculation workbook as the best fit. "
                "Use this sequence to move from the idea to a functional, reviewable workbook."
            )
    
            for i, (title, detail) in enumerate(EXCEL_BUILD_FRAMEWORK, start=1):
                st.markdown(
                    f"""
                    <div class="framework-step">
                        <span class="n">{i}</span><b>{title}</b><br>
                        <span class="why">{detail}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    
            st.info(
                "A useful default workbook structure is: Instructions · Inputs · Parameters · "
                "Calculations · QA/QC · Results · Change Log. Not every workbook needs every sheet."
            )
    

    st.markdown("### What the result means")
    st.write(
        "This is a fit recommendation, not a mandate. The scoring intentionally favors the "
        "simplest solution that addresses the root cause. An app only receives a major advantage "
        "when the problem genuinely requires centralized multi-user interaction, real-time shared "
        "state, or an app-style guided experience."
    )

    left, middle, right = st.columns([1.1, 4.8, 1.6])
    with left:
        if st.button("Back", width="stretch"):
            goto(6)
    with right:
        if st.button("Start over", width="stretch"):
            reset_app()
