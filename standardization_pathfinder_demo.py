"""Standardization Pathfinder — presentation demo.

Run locally:
    python -m pip install "streamlit>=1.54,<2"
    python -m streamlit run standardization_pathfinder_demo.py

Suggested 2–3 minute walkthrough:
1. Begin the demo with blank fields and enter your example live.
2. Enter the recurring problem, root causes, and desired outcome.
3. Show the solution characteristics, then select Find my solution.
4. Explain the recommendation and expand the workbook build sequence.

The recommendation engine, categories, descriptions, and workbook build
framework are preserved from the supplied app. Scores are heuristic points,
not probabilities. No microphone, external service, or file persistence is
required. Inputs live only in the current Streamlit session.
"""
import copy
import html
import re
import streamlit as st

st.set_page_config(page_title="Standardization Pathfinder · Demo", page_icon="🧭", layout="wide", initial_sidebar_state="collapsed")


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

# Compact presentation layout, using the original visual design.
st.markdown("""<style>
.block-container {max-width:1120px;padding-top:1rem;padding-bottom:1.5rem;}
.landing-shell,.landing-overlay {min-height:380px;}
.landing-overlay {padding:2.6rem 3rem;}
.landing-copy h1 {font-size:3.6rem;max-width:600px;}
.landing-copy p {font-size:1.04rem;line-height:1.5;}
.page-heading {margin:.2rem 0 .8rem;}
.page-heading h2 {font-size:1.85rem;}
.result-hero {padding:1.4rem 1.7rem;margin-bottom:.8rem;}
.fit-card {min-height:175px;}
.demo-tag {font-size:.75rem;letter-spacing:.08em;color:#69766f;text-transform:uppercase;}
@media(max-width:800px){.landing-overlay{padding:1.8rem;}.landing-copy h1{font-size:2.8rem;}}
</style>""", unsafe_allow_html=True)

# No answers are supplied in advance for the live walkthrough.
DEFAULTS.update(data_shape=None, variability=None, user_count=None, nontechnical=False)

if "demo_initialized" not in st.session_state:
    st.session_state.update(copy.deepcopy(DEFAULTS))
    st.session_state.demo_initialized = True


def set_page(page):
    st.session_state.page = page


def reset_demo():
    # Callbacks run before widgets are recreated, so resetting is safe.
    for key in list(st.session_state):
        if key.startswith("_input_"):
            del st.session_state[key]
    st.session_state.update(copy.deepcopy(DEFAULTS))
    st.session_state.demo_initialized = True


def remember(key):
    st.session_state[key] = st.session_state[f"_input_{key}"]


def widget(method, label, key, **kwargs):
    # Permanent values survive when a widget disappears on another page.
    temporary = f"_input_{key}"
    if temporary not in st.session_state:
        st.session_state[temporary] = copy.deepcopy(st.session_state[key])
    return method(label, key=temporary, on_change=remember, args=(key,), **kwargs)


def navigation(page, label="Continue", disabled=False):
    left, _, right = st.columns([1.2, 4.2, 1.8])
    with left:
        st.button("Back", on_click=set_page, args=(page - 1,), width="stretch")
    with right:
        st.button(label, type="primary", on_click=set_page, args=(page + 1,), disabled=disabled, width="stretch")


def escaped(value):
    return html.escape(str(value))


brand, restart = st.columns([6, 1.5])
with brand:
    st.markdown('<div class="brand">🧭 Standardization Pathfinder</div><div class="demo-tag">Presentation demo · session only</div>', unsafe_allow_html=True)
with restart:
    st.button("Start over", on_click=reset_demo, width="stretch")

page = st.session_state.page
if page:
    names = ["Problem & better way", "Solution fit", "Recommendation"]
    st.progress(page / 3)
    st.caption(f"{page} of 3 · {names[page - 1]}")

if page == 0:
    st.markdown("""<div class="landing-shell">
<div class="landing-sky"></div><div class="mist"></div>
<div class="mountains-back"></div><div class="mountains-front"></div>
<div class="forest-floor"></div><div class="path"></div>
<div class="tree t1"></div><div class="tree t2"></div><div class="tree t3"></div>
<div class="tree t4"></div><div class="tree t5"></div><div class="tree t6"></div>
<div class="landing-overlay"><div class="landing-copy">
<div class="landing-eyebrow">A short guided demo</div>
<h1>Find the clearest path forward.</h1>
<p>Start with a recurring problem. Understand its cause. Match the better way to a document, workbook, process, code, or app.</p>
</div></div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="journey-strip">
<div class="journey-stop"><div class="num">1</div><b>Define the problem</b><span>Capture the friction, root causes, and better way.</span></div>
<div class="journey-stop"><div class="num">2</div><b>Describe the needs</b><span>Identify the characteristics a solution must support.</span></div>
<div class="journey-stop"><div class="num">3</div><b>Choose a practical fit</b><span>See the recommendation, reasons, and alternatives.</span></div>
</div>""", unsafe_allow_html=True)
    st.button("Begin the demo →", type="primary", on_click=set_page, args=(1,), width="stretch")
    st.caption("Live walkthrough · Enter your own example · Original rule-based scoring")

elif page == 1:
    heading("Step 1 · The problem", "What are you trying to fix?", "Describe the recurring friction, its root causes, and the better way.")
    widget(st.text_input, "Problem title", "problem_title")
    left, right = st.columns(2)
    with left:
        widget(st.text_area, "What is the pain point?", "pain_point", height=130)
        widget(st.multiselect, "What is causing it?", "root_causes", options=ROOT_CAUSE_CATEGORIES)
    with right:
        widget(st.text_area, "Imagine the better way", "daydream", height=130)
        widget(st.text_area, "What would success look like?", "desired_outcome", height=100)
    with st.expander("Current workflow and context"):
        widget(st.text_area, "Current workflow", "current_workflow", height=100)
        widget(st.text_input, "Existing tools and controls", "existing_tools")
        widget(st.text_input, "Why it matters", "why_matter")
    complete = bool(st.session_state.problem_title.strip() and st.session_state.pain_point.strip()
                    and st.session_state.root_causes and st.session_state.daydream.strip())
    if not complete:
        st.caption("Add a title, pain point, at least one root cause, and a better way to continue.")
    navigation(1, disabled=not complete)

elif page == 2:
    heading("Step 2 · Solution fit", "What does the solution need to do?", "These characteristics guide the same recommendation engine used in the full app.")
    left, right = st.columns(2)
    with left:
        widget(st.selectbox, "What kind of information dominates?", "data_shape", options=DATA_SHAPE_OPTIONS, index=None, placeholder="Choose the information type")
        widget(st.selectbox, "How variable is the workflow?", "variability", options=VARIABILITY_OPTIONS, index=None, placeholder="Choose the variability")
        widget(st.selectbox, "How many people will use it?", "user_count", options=USER_OPTIONS, index=None, placeholder="Choose the user group")
    with right:
        widget(st.checkbox, "Repeatable calculations", "calculation_heavy")
        widget(st.checkbox, "Compare independently calculated results", "comparison_needed")
        widget(st.checkbox, "Already Excel / spreadsheet native", "excel_native")
        widget(st.checkbox, "Standard inputs", "standard_inputs")
        widget(st.checkbox, "Standard outputs", "standard_outputs")
        widget(st.checkbox, "Strong QA/QC or traceability", "qa_important")
    with st.expander("Other solution needs and constraints"):
        a, b = st.columns(2)
        with a:
            widget(st.checkbox, "Repeated file or data processing", "file_processing")
            widget(st.checkbox, "Repeatable decision logic", "repeatable_decisions")
            widget(st.checkbox, "Shared centralized multi-user state", "central_multiuser")
        with b:
            widget(st.checkbox, "Real-time cross-user updates", "real_time")
            widget(st.checkbox, "Should work offline", "offline")
            widget(st.checkbox, "Primary users are nontechnical", "nontechnical")
    with st.expander("Review the problem"):
        st.write(f"**{st.session_state.problem_title}**")
        st.write(st.session_state.pain_point)
        st.write("**Root causes:** " + ", ".join(st.session_state.root_causes))
        st.write("**Better way:** " + st.session_state.daydream)
    fit_complete = all(st.session_state[key] is not None for key in ("data_shape", "variability", "user_count"))
    if not fit_complete:
        st.caption("Choose the information type, workflow variability, and user group to continue.")
    navigation(2, label="Find my solution →", disabled=not fit_complete)

elif page == 3:
    ranked, why = recommendation_engine()
    top_name, top_score = ranked[0]
    st.markdown(f"""<div class="result-hero">
<div class="label">Best-fit standardization</div>
<h2>{escaped(top_name)}</h2><p>{escaped(solution_description(top_name))}</p>
<div class="badge-row"><span class="badge">{escaped(category_for(top_name))}</span>
<span class="badge">Fit score: {top_score} points</span></div></div>""", unsafe_allow_html=True)
    left, right = st.columns([1.05, 1])
    with left:
        st.subheader("Why this fits")
        if why[top_name]:
            for reason in why[top_name][:4]:
                st.markdown(f"- {reason}")
        else:
            st.write("This option has the highest total under the current scoring rules. Review the inputs and alternatives before choosing.")
    with right:
        with st.container(border=True):
            st.markdown("**The outcome you want**")
            st.write(st.session_state.desired_outcome or st.session_state.daydream)
    st.markdown("#### Alternatives")
    for col, (name, score) in zip(st.columns(3), ranked[1:4]):
        with col:
            st.markdown(f"""<div class="fit-card"><div class="review-k">{escaped(category_for(name))}</div>
<h4>{escaped(name)}</h4><div class="why">{escaped(solution_description(name))}</div>
<div class="review-k" style="margin-top:.7rem">{score} fit points</div></div>""", unsafe_allow_html=True)
    st.caption("Rule-based fit scores are relative points, not probabilities or validated confidence levels. This is a recommendation, not a mandate.")
    if top_name == "Excel calculation workbook":
        with st.expander("Next: build your workbook"):
            for i, (title, detail) in enumerate(EXCEL_BUILD_FRAMEWORK, 1):
                st.markdown(f"**{i}. {title}** — {detail}")
            st.info("Suggested structure: Instructions · Inputs · Parameters · Calculations · QA/QC · Results · Change Log. Not every workbook needs every sheet.")
    with st.expander("See the full comparison"):
        st.dataframe([{"Solution": name, "Category": category_for(name), "Fit points": score} for name, score in ranked], hide_index=True, width="stretch")
    back, _, again = st.columns([1.2, 4, 1.8])
    with back:
        st.button("Back", on_click=set_page, args=(2,), width="stretch")
    with again:
        st.button("Run demo again", type="primary", on_click=reset_demo, width="stretch")
