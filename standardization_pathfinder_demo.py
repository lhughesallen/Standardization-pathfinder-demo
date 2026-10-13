

Pasted text.txt
Document
I want to create a short demo version of this streamlit app for a presenation: 


Created a  for a 2–3 minute walkthrough.

Four screens with your forest styling.

Editable, prefilled example and reset controls.

Original recommendation scoring preserved.

Navigation and input persistence tested.

Run it with:

python -m pip install "streamlit>=1.54,<2"
python -m streamlit run standardization_pathfinder_demo.py

Library
/
standardization_pathfinder_demo.py



1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
"""Standardization Pathfinder — presentation demo.

Run locally:
    python -m pip install "streamlit>=1.54,<2"
    python -m streamlit run standardization_pathfinder_demo.py

Suggested 2–3 minute walkthrough:
1. Begin the demo (the example is fictional and prefilled).
2. Show the recurring problem, root causes, and desired outcome.
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
