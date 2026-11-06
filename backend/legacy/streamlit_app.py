from __future__ import annotations

import os
import textwrap
import time
from datetime import date, datetime, timedelta
from html import escape
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from wedplanner import PlannerSettings, WeddingPlanner
from wedplanner.config import DEFAULT_MODEL

APP_TITLE = "Multi-Agent Wedding Planner"
MODEL_NAME = DEFAULT_MODEL
REQUIRED_KEYS = ("GROQ_API_KEY", "TAVILY_API_KEY")

STYLE_OPTIONS = [
    "Modern",
    "Romantic",
    "Classic",
    "Garden",
    "Minimal",
    "Luxury",
    "Cultural fusion",
    "Destination",
    "Eco-conscious",
    "Black tie",
]

PRIORITY_OPTIONS = [
    "Venue shortlist",
    "Vendor research",
    "Budget allocation",
    "Guest experience",
    "Timeline",
    "Design direction",
    "Risk management",
    "Travel logistics",
]


load_dotenv()
st.set_page_config(page_title=APP_TITLE, page_icon=None, layout="wide", initial_sidebar_state="expanded")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #17202a;
            --ink-soft: #253241;
            --muted: #5d6b7a;
            --line: #dce4ea;
            --line-strong: #c9d4dc;
            --panel: #ffffff;
            --surface: #f6f8fb;
            --surface-strong: #eef4f6;
            --sidebar: #20232d;
            --sidebar-field: #10131b;
            --teal: #1f7a7a;
            --coral: #bd5a4d;
            --gold: #a87922;
            --success: #22735f;
            --danger: #b94e49;
            --shadow: 0 14px 36px rgba(23, 32, 42, 0.08);
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 12% -10%, rgba(31, 122, 122, 0.09), transparent 28rem),
                linear-gradient(180deg, #fbfcfd 0%, var(--surface) 24rem, var(--surface) 100%);
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, p, div, span, label {
            letter-spacing: 0;
        }

        .app-header {
            align-items: end;
            background: linear-gradient(135deg, #ffffff 0%, #f8fcfb 52%, #fff6f3 100%);
            border: 1px solid var(--line);
            border-top: 4px solid var(--teal);
            border-radius: 8px;
            box-shadow: var(--shadow);
            display: grid;
            gap: 1.25rem;
            grid-template-columns: minmax(0, 1fr) auto;
            padding: 1.35rem 1.45rem 1.25rem;
            margin-bottom: 1.25rem;
        }

        .app-kicker {
            color: var(--gold);
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }

        .app-title {
            color: var(--ink);
            font-size: 2.35rem;
            font-weight: 800;
            line-height: 1.08;
            margin: 0 0 0.45rem;
        }

        .app-subtitle {
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.5;
            max-width: 780px;
            margin: 0;
        }

        .header-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            justify-content: flex-end;
            max-width: 300px;
        }

        .header-chip {
            background: rgba(31, 122, 122, 0.1);
            border: 1px solid rgba(31, 122, 122, 0.18);
            border-radius: 999px;
            color: var(--teal);
            font-size: 0.78rem;
            font-weight: 750;
            padding: 0.25rem 0.65rem;
            white-space: nowrap;
        }

        .summary-grid {
            display: grid;
            gap: 0.85rem;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            margin: 0 0 1.05rem;
        }

        .summary-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 10px 28px rgba(23, 32, 42, 0.05);
            min-height: 5.9rem;
            padding: 0.9rem 0.95rem;
        }

        .summary-card .label {
            color: var(--muted);
            display: block;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
            text-transform: uppercase;
        }

        .summary-card .value {
            color: var(--ink);
            display: block;
            font-size: 1.35rem;
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 0.2rem;
        }

        .summary-card .note {
            color: var(--muted);
            display: block;
            font-size: 0.83rem;
            line-height: 1.3;
        }

        .section-label {
            color: var(--ink);
            font-weight: 780;
            font-size: 1rem;
            margin: 0 0 0.6rem;
        }

        .field-group-title {
            color: var(--ink-soft);
            font-size: 0.82rem;
            font-weight: 800;
            margin: 0.2rem 0 0.55rem;
            text-transform: uppercase;
        }

        [data-testid="stForm"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: var(--shadow);
            padding: 1.05rem 1.1rem 1.15rem;
        }

        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stForm"] label,
        [data-testid="stForm"] p {
            color: var(--ink) !important;
            font-weight: 650;
        }

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTextArea textarea {
            background: #ffffff !important;
            border: 1px solid var(--line-strong) !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            color: var(--ink) !important;
        }

        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stDateInput input:focus,
        .stTextArea textarea:focus {
            border-color: var(--teal) !important;
            box-shadow: 0 0 0 3px rgba(31, 122, 122, 0.12) !important;
        }

        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            border-color: var(--line-strong) !important;
            border-radius: 8px !important;
            color: var(--ink) !important;
            min-height: 2.65rem;
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] svg {
            color: var(--ink) !important;
            fill: var(--ink) !important;
        }

        div[data-baseweb="tag"] {
            background: rgba(31, 122, 122, 0.11) !important;
            border: 1px solid rgba(31, 122, 122, 0.2) !important;
            border-radius: 6px !important;
        }

        div[data-baseweb="tag"] span {
            color: var(--ink) !important;
            font-weight: 700 !important;
        }

        .stSlider [data-baseweb="slider"] [role="slider"] {
            background: var(--coral) !important;
            border-color: #ffffff !important;
        }

        .stSlider [data-baseweb="slider"] > div {
            color: var(--coral) !important;
        }

        [data-testid="stSidebar"] {
            background: var(--sidebar);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: #f7f9fc !important;
        }

        [data-testid="stSidebar"] .stTextInput input {
            background: var(--sidebar-field) !important;
            border-color: rgba(255, 255, 255, 0.18) !important;
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.16);
        }

        .side-panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 10px 28px rgba(23, 32, 42, 0.05);
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }

        .side-panel h3 {
            color: var(--ink);
            font-size: 1rem;
            margin: 0 0 0.75rem;
        }

        .side-panel p {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.45;
            margin: 0 0 0.75rem;
        }

        .lens-grid {
            display: grid;
            gap: 0.65rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            margin-bottom: 0.75rem;
        }

        .lens-item {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.6rem 0.65rem;
        }

        .lens-item span {
            color: var(--muted);
            display: block;
            font-size: 0.73rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .lens-item strong {
            color: var(--ink);
            display: block;
            font-size: 0.96rem;
            line-height: 1.25;
            margin-top: 0.15rem;
        }

        .chip-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }

        .soft-chip {
            background: rgba(168, 121, 34, 0.12);
            border: 1px solid rgba(168, 121, 34, 0.22);
            border-radius: 999px;
            color: #6e4f17;
            font-size: 0.76rem;
            font-weight: 750;
            padding: 0.2rem 0.55rem;
        }

        .flow-row {
            border-top: 1px solid var(--line);
            padding: 0.68rem 0;
        }

        .flow-row:first-of-type {
            border-top: 0;
            padding-top: 0;
        }

        .flow-row strong {
            color: var(--ink);
            display: block;
            font-size: 0.92rem;
            margin-bottom: 0.15rem;
        }

        .flow-row span {
            color: var(--muted);
            display: block;
            font-size: 0.84rem;
            line-height: 1.35;
        }

        .key-row {
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.14);
            display: flex;
            justify-content: space-between;
            padding: 0.45rem 0;
        }

        .key-row span:first-child {
            color: rgba(255, 255, 255, 0.72) !important;
            font-size: 0.9rem;
        }

        .badge {
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            padding: 0.14rem 0.55rem;
        }

        .badge-ready {
            background: rgba(48, 188, 154, 0.16);
            color: #70dfc6 !important;
        }

        .badge-missing {
            background: rgba(255, 144, 130, 0.16);
            color: #ffb6ad !important;
        }

        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.85rem 0.95rem;
        }

        div[data-testid="stMetric"] label {
            color: var(--muted);
        }

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] p {
            color: var(--ink) !important;
            font-weight: 650;
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] div {
            color: var(--ink) !important;
        }

        div[data-testid="stMetricDelta"] {
            color: var(--muted) !important;
        }

        .result-shell {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: var(--shadow);
            padding: 1rem 1.1rem;
            margin-top: 0.75rem;
        }

        .result-title-row {
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: space-between;
            margin: 0.3rem 0 0.75rem;
        }

        .result-title-row h3 {
            color: var(--ink);
            font-size: 1.05rem;
            margin: 0;
        }

        .result-title-row span {
            color: var(--muted);
            font-size: 0.84rem;
            font-weight: 650;
        }

        .empty-result {
            background: var(--panel);
            border: 1px dashed #b9c5cf;
            border-radius: 8px;
            box-shadow: 0 10px 28px rgba(23, 32, 42, 0.04);
            color: var(--muted);
            padding: 1.4rem;
            text-align: center;
        }

        .empty-result strong {
            color: var(--ink);
            display: block;
            font-size: 1rem;
            margin-bottom: 0.3rem;
        }

        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] button {
            background: #ffffff;
            border: 1px solid var(--line-strong);
            border-radius: 8px;
            color: var(--ink);
            font-weight: 700;
            min-height: 2.7rem;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: var(--teal);
            color: var(--teal);
        }

        div[data-testid="stFormSubmitButton"] button {
            background: var(--coral) !important;
            border-color: var(--coral) !important;
            color: #ffffff !important;
        }

        div[data-testid="stFormSubmitButton"] button:disabled {
            background: #cbd5dd !important;
            border-color: #cbd5dd !important;
            color: #62717f !important;
        }

        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(255, 255, 255, 0.22);
            color: #ffffff;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.4);
            color: #ffffff;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 0.8rem;
            }

            .app-header {
                grid-template-columns: 1fr;
                padding: 1.05rem;
            }

            .app-title {
                font-size: 1.85rem;
            }

            .header-chips {
                justify-content: flex-start;
                max-width: none;
            }

            .summary-grid,
            .lens-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_default_form_values() -> dict[str, Any]:
    return {
        "couple_name": "Amira and Noah",
        "wedding_location": "Chicago, Illinois",
        "wedding_date": date.today() + timedelta(days=240),
        "guest_count": 120,
        "currency": "USD",
        "budget_range": (35000, 65000),
        "ceremony_type": "Ceremony and reception",
        "wedding_styles": ["Modern", "Romantic", "Cultural fusion"],
        "planning_priorities": ["Venue shortlist", "Vendor research", "Budget allocation", "Timeline"],
        "tone": "Elegant and practical",
        "must_haves": (
            "Indoor-outdoor venue, strong vegetarian menu, live acoustic music, "
            "smooth guest transportation, and a photography-forward schedule."
        ),
        "constraints": (
            "Avoid venues more than 45 minutes from downtown. Keep the design elevated "
            "without relying on heavy floral spend."
        ),
        "traditions": (
            "Blend a short western ceremony with a family tea ceremony. Include space "
            "for speeches from both families."
        ),
    }


def load_sample_values() -> None:
    for key, value in get_default_form_values().items():
        st.session_state[key] = value


def initialize_state() -> None:
    st.session_state.setdefault("plans", [])
    for key, value in get_default_form_values().items():
        st.session_state.setdefault(key, value)


def read_streamlit_secret(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
    except Exception:
        return None
    return str(value) if value else None


def hydrate_env_from_secrets() -> None:
    for key in REQUIRED_KEYS:
        if os.getenv(key):
            continue
        secret_value = read_streamlit_secret(key)
        if secret_value:
            os.environ[key] = secret_value


def apply_key_overrides(groq_key: str, tavily_key: str) -> None:
    if groq_key.strip():
        os.environ["GROQ_API_KEY"] = groq_key.strip()
    if tavily_key.strip():
        os.environ["TAVILY_API_KEY"] = tavily_key.strip()


def key_is_ready(name: str) -> bool:
    return bool(os.getenv(name))


def format_budget_range(budget_range: tuple[int, int], currency: str) -> str:
    low, high = budget_range
    return f"{currency} {low // 1000}k - {high // 1000}k"


def format_budget_per_guest(budget_range: tuple[int, int], guest_count: int) -> str:
    if guest_count <= 0:
        return "Not set"
    low, high = budget_range
    average_budget = (low + high) / 2
    return f"{average_budget / guest_count:,.0f} per guest"


def format_days_until(target_date: date) -> str:
    days = (target_date - date.today()).days
    if days == 0:
        return "Today"
    if days == 1:
        return "Tomorrow"
    if days < 0:
        return f"{abs(days)} days ago"
    return f"{days} days out"


def format_list_preview(items: list[str], fallback: str = "Flexible") -> str:
    if not items:
        return fallback
    preview = items[:2]
    suffix = f" +{len(items) - len(preview)}" if len(items) > len(preview) else ""
    return f"{', '.join(preview)}{suffix}"


def render_key_badge(label: str, ready: bool) -> None:
    status_class = "badge-ready" if ready else "badge-missing"
    status_text = "Ready" if ready else "Missing"
    st.markdown(
        f"""
        <div class="key-row">
            <span>{label}</span>
            <span class="badge {status_class}">{status_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="app-header">
            <div>
                <div class="app-kicker">LangChain portfolio project</div>
                <h1 class="app-title">Multi-Agent Wedding Planner</h1>
                <p class="app-subtitle">
                    Build a client-ready planning brief from preferences, constraints,
                    market research, and agent-synthesized recommendations.
                </p>
            </div>
            <div class="header-chips">
                <span class="header-chip">3-agent flow</span>
                <span class="header-chip">Live vendor research</span>
                <span class="header-chip">Markdown export</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_summary(runtime_ready: bool) -> None:
    payload = get_form_payload()
    status_value = "Ready" if runtime_ready else "Keys needed"
    status_note = "Planner can run live" if runtime_ready else "Add Groq and Tavily keys"
    guest_note = f"{payload['guest_count']:,} guests"

    st.markdown(
        f"""
        <div class="summary-grid">
            <div class="summary-card">
                <span class="label">Runtime</span>
                <span class="value">{status_value}</span>
                <span class="note">{status_note}</span>
            </div>
            <div class="summary-card">
                <span class="label">Event Date</span>
                <span class="value">{format_days_until(payload["wedding_date"])}</span>
                <span class="note">{payload["wedding_date"].strftime("%b %d, %Y")}</span>
            </div>
            <div class="summary-card">
                <span class="label">Budget</span>
                <span class="value">{format_budget_range(payload["budget_range"], payload["currency"])}</span>
                <span class="note">{format_budget_per_guest(payload["budget_range"], payload["guest_count"])}</span>
            </div>
            <div class="summary-card">
                <span class="label">Planning Focus</span>
                <span class="value">{escape(format_list_preview(payload["planning_priorities"], "Balanced"))}</span>
                <span class="note">{guest_note}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> bool:
    hydrate_env_from_secrets()

    with st.sidebar:
        st.markdown("### Runtime")
        groq_override = st.text_input("Groq API key", type="password", key="groq_key_override")
        tavily_override = st.text_input("Tavily API key", type="password", key="tavily_key_override")
        apply_key_overrides(groq_override, tavily_override)

        groq_ready = key_is_ready("GROQ_API_KEY")
        tavily_ready = key_is_ready("TAVILY_API_KEY")
        render_key_badge("Groq", groq_ready)
        render_key_badge("Tavily", tavily_ready)

        st.divider()
        st.markdown("### Demo Controls")
        st.button("Load sample brief", use_container_width=True, on_click=load_sample_values)

        if st.button("Refresh agent clients", use_container_width=True):
            load_agent_dependencies.clear()
            st.toast("Agent clients refreshed.")

        st.divider()
        st.markdown("### Saved Runs")
        if st.session_state.plans:
            for plan in st.session_state.plans[:4]:
                st.caption(f"{plan['title']} | {plan['created_at']}")
        else:
            st.caption("No runs yet.")

    return groq_ready and tavily_ready


@st.cache_resource(show_spinner=False)
def load_agent_dependencies():
    return WeddingPlanner(PlannerSettings.from_environment())


def build_requirements(payload: dict[str, Any]) -> str:
    budget_low, budget_high = payload["budget_range"]
    styles = ", ".join(payload["wedding_styles"]) or "Flexible"
    priorities = ", ".join(payload["planning_priorities"]) or "Balanced planning support"

    return textwrap.dedent(
        f"""
        Couple or event name: {payload["couple_name"]}
        Wedding location: {payload["wedding_location"]}
        Target date: {payload["wedding_date"].strftime("%B %d, %Y")}
        Guest count: {payload["guest_count"]}
        Budget range: {payload["currency"]} {budget_low:,} to {budget_high:,}
        Event scope: {payload["ceremony_type"]}
        Preferred style: {styles}
        Planning priorities: {priorities}
        Planner tone: {payload["tone"]}

        Must-haves:
        {payload["must_haves"].strip() or "None specified."}

        Constraints and sensitivities:
        {payload["constraints"].strip() or "None specified."}

        Cultural, family, or ceremonial details:
        {payload["traditions"].strip() or "None specified."}

        Requested final plan:
        - Executive summary with the planning concept.
        - Venue and vendor research recommendations with clear rationale.
        - Budget allocation by category.
        - Timeline from now through wedding day.
        - Risks, tradeoffs, and open questions for the couple.
        """
    ).strip()


def get_form_payload() -> dict[str, Any]:
    keys = [
        "couple_name",
        "wedding_location",
        "wedding_date",
        "guest_count",
        "currency",
        "budget_range",
        "ceremony_type",
        "wedding_styles",
        "planning_priorities",
        "tone",
        "must_haves",
        "constraints",
        "traditions",
    ]
    return {key: st.session_state[key] for key in keys}


def render_brief_form(runtime_ready: bool) -> bool:
    st.markdown('<div class="section-label">Wedding Brief</div>', unsafe_allow_html=True)

    with st.form("wedding_brief_form"):
        st.markdown('<div class="field-group-title">Basics</div>', unsafe_allow_html=True)
        st.text_input("Couple or project name", key="couple_name")

        col_a, col_b = st.columns(2)
        with col_a:
            st.text_input("Location", key="wedding_location")
            st.number_input("Guest count", min_value=10, max_value=1000, step=10, key="guest_count")
        with col_b:
            st.date_input("Target date", min_value=date.today(), key="wedding_date")
            st.selectbox(
                "Event scope",
                [
                    "Ceremony and reception",
                    "Reception only",
                    "Destination wedding",
                    "Multi-day wedding",
                    "Elopement plus celebration",
                ],
                key="ceremony_type",
            )

        st.markdown('<div class="field-group-title">Budget and Direction</div>', unsafe_allow_html=True)
        budget_col, tone_col = st.columns([1.1, 1])
        with budget_col:
            st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD", "AUD"], key="currency")
            st.slider(
                "Budget range",
                min_value=5000,
                max_value=250000,
                step=5000,
                key="budget_range",
            )
        with tone_col:
            st.selectbox(
                "Planner tone",
                ["Elegant and practical", "Luxury editorial", "Budget-conscious", "Warm and family-centered"],
                key="tone",
            )
            st.multiselect("Style direction", STYLE_OPTIONS, key="wedding_styles")

        st.markdown('<div class="field-group-title">Priorities and Guardrails</div>', unsafe_allow_html=True)
        st.multiselect("Planning priorities", PRIORITY_OPTIONS, key="planning_priorities")

        notes_a, notes_b = st.columns(2)
        with notes_a:
            st.text_area("Must-haves", height=124, key="must_haves")
            st.text_area("Traditions and family details", height=104, key="traditions")
        with notes_b:
            st.text_area("Constraints", height=244, key="constraints")

        return st.form_submit_button(
            "Generate wedding plan",
            type="primary",
            use_container_width=True,
            disabled=not runtime_ready,
        )


def invoke_planner(requirements: str) -> tuple[str, float]:
    started = time.perf_counter()
    content = load_agent_dependencies().generate(requirements)
    return content, time.perf_counter() - started


def create_download_name(title: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in title)
    slug = "-".join(part for part in slug.split("-") if part)
    return f"{slug[:44] or 'wedding-plan'}.md"


def save_plan(title: str, requirements: str, content: str, duration: float) -> None:
    st.session_state.plans.insert(
        0,
        {
            "title": title,
            "requirements": requirements,
            "content": content,
            "duration": duration,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
    )


def render_project_snapshot() -> None:
    st.markdown(
        f"""
        <div class="side-panel">
            <h3>Agent Flow</h3>
            <div class="flow-row">
                <strong>MainWeddingPlannerAgent</strong>
                <span>Builds the final strategy from the structured wedding brief.</span>
            </div>
            <div class="flow-row">
                <strong>SubAgent1 and SubAgent2</strong>
                <span>Split research tasks for venues, vendors, logistics, and market context.</span>
            </div>
            <div class="flow-row">
                <strong>Tavily Search Tool</strong>
                <span>Retrieves current planning data before synthesis.</span>
            </div>
            <div class="flow-row">
                <strong>{MODEL_NAME}</strong>
                <span>Coordinates reasoning and client-ready recommendations.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_planning_lens() -> None:
    payload = get_form_payload()
    style_chips = "".join(
        f'<span class="soft-chip">{escape(style)}</span>' for style in payload["wedding_styles"]
    ) or '<span class="soft-chip">Flexible style</span>'
    priority_chips = "".join(
        f'<span class="soft-chip">{escape(priority)}</span>' for priority in payload["planning_priorities"]
    ) or '<span class="soft-chip">Balanced plan</span>'

    st.markdown(
        f"""
        <div class="side-panel">
            <h3>Planning Lens</h3>
            <div class="lens-grid">
                <div class="lens-item">
                    <span>Couple</span>
                    <strong>{escape(payload["couple_name"] or "Untitled")}</strong>
                </div>
                <div class="lens-item">
                    <span>Location</span>
                    <strong>{escape(payload["wedding_location"] or "Not set")}</strong>
                </div>
                <div class="lens-item">
                    <span>Scope</span>
                    <strong>{escape(payload["ceremony_type"])}</strong>
                </div>
                <div class="lens-item">
                    <span>Pace</span>
                    <strong>{format_days_until(payload["wedding_date"])}</strong>
                </div>
            </div>
            <p>Style direction</p>
            <div class="chip-list">{style_chips}</div>
            <p style="margin-top:0.8rem;">Planning priorities</p>
            <div class="chip-list">{priority_chips}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_results() -> None:
    if not st.session_state.plans:
        st.markdown(
            """
            <div class="empty-result">
                <strong>No plan generated yet</strong>
                Complete the brief and run the planner to create a client-ready wedding plan.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    latest = st.session_state.plans[0]

    st.markdown(
        f"""
        <div class="result-title-row">
            <h3>{escape(latest["title"])}</h3>
            <span>Created {escape(latest["created_at"])}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Runtime", f"{latest['duration']:.1f}s")
    metric_b.metric("Brief Words", f"{len(latest['requirements'].split()):,}")
    metric_c.metric("Saved Runs", str(len(st.session_state.plans)))

    plan_tab, requirements_tab, architecture_tab = st.tabs(["Plan", "Input Brief", "Architecture"])

    with plan_tab:
        st.markdown('<div class="result-shell">', unsafe_allow_html=True)
        st.markdown(latest["content"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            "Download plan",
            data=latest["content"],
            file_name=create_download_name(latest["title"]),
            mime="text/markdown",
            use_container_width=True,
        )

    with requirements_tab:
        st.code(latest["requirements"], language="markdown")

    with architecture_tab:
        st.markdown(
            """
            ```text
            Streamlit UI
                -> structured wedding requirements
                -> WEDDING_PLANNER_AGENT_PROMPT
                -> MainWeddingPlannerAgent
                    -> delegate_to_subagent1(query)
                        -> SubAgent1 -> Tavily search_web
                    -> delegate_to_subagent2(query)
                        -> SubAgent2 -> Tavily search_web
                -> synthesized wedding plan
            ```
            """
        )


def handle_submission() -> None:
    payload = get_form_payload()
    requirements = build_requirements(payload)
    title = payload["couple_name"].strip() or "Wedding plan"

    with st.status("Running planner agents", expanded=True) as status:
        st.write("Preparing the main planner prompt.")
        st.write("Loading agent dependencies.")
        try:
            st.write("Delegating research and synthesizing the plan.")
            content, duration = invoke_planner(requirements)
        except Exception as exc:
            status.update(label="Planner run failed", state="error")
            st.error("The planner could not complete the run. Check API keys, quotas, and Tavily access.")
            with st.expander("Technical details"):
                st.code(str(exc))
            return

        save_plan(title=title, requirements=requirements, content=content, duration=duration)
        status.update(label="Plan ready", state="complete")


def main() -> None:
    inject_css()
    initialize_state()
    render_header()

    runtime_ready = render_sidebar()

    if not runtime_ready:
        st.warning("Add Groq and Tavily API keys in `.env`, Streamlit secrets, or the sidebar to run the live agents.")

    render_dashboard_summary(runtime_ready=runtime_ready)

    left_col, right_col = st.columns([1.35, 0.8], gap="large")

    with left_col:
        submitted = render_brief_form(runtime_ready=runtime_ready)

    with right_col:
        render_planning_lens()
        render_project_snapshot()

    if submitted:
        handle_submission()

    st.markdown('<div class="section-label">Latest Output</div>', unsafe_allow_html=True)
    render_results()


if __name__ == "__main__":
    main()
