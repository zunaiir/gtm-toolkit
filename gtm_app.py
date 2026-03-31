"""
Tiger Data — GTM Toolkit
Internal AI tools for the go-to-market team.

SETUP (one time):
  pip install -r requirements.txt

RUN:
  python3 -m streamlit run gtm_app.py

Then open http://localhost:8501 in your browser.
"""

import os
import base64
import tempfile
from urllib.parse import quote
import streamlit as st

# ─── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Tiger Data · GTM Toolkit",
    page_icon="🐯",
    layout="centered"
)

# ─── Brand styles ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Tiger Data: black, white, orange accent */

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #1A1A1A;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #A3A3A3 !important;
        font-size: 0.95rem;
    }
    [data-testid="stSidebar"] hr {
        border-color: #2A2A2A !important;
    }

    /* Main background */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Primary / submit button → orange */
    .stFormSubmitButton > button,
    .stButton > button[kind="primary"] {
        background-color: #F97316 !important;
        border: none !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        letter-spacing: 0.02em;
    }
    .stFormSubmitButton > button:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: #EA6C0A !important;
    }

    /* Download button → black outlined */
    .stDownloadButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1A1A1A !important;
    }

    /* Brief output card */
    .brief-output {
        background-color: #FAFAFA;
        border-left: 4px solid #F97316;
        border-radius: 6px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
        color: #111111;
    }

    /* Page title */
    h1 { color: #0A0A0A !important; font-weight: 700 !important; }
    h2 { color: #0A0A0A !important; }

    /* Tagline */
    .tagline {
        color: #737373;
        font-size: 0.95rem;
        margin-top: -0.5rem;
        margin-bottom: 1.75rem;
    }

    /* Input fields */
    .stTextInput input {
        border-radius: 6px !important;
        border-color: #D4D4D4 !important;
    }
    .stTextInput input:focus {
        border-color: #F97316 !important;
        box-shadow: 0 0 0 1px #F97316 !important;
    }

    /* Coming soon info box */
    .stAlert {
        border-radius: 6px !important;
    }

    /* Force main content text to black */
    .main * { color: #0A0A0A !important; }
    .stMarkdown, .stMarkdown p, .stMarkdown li { color: #0A0A0A !important; }

    /* Input field labels */
    label, [data-baseweb="form-control-label"],
    .stTextInput label, .stTextArea label,
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label {
        color: #0A0A0A !important;
        font-weight: 500 !important;
    }

    /* Expander label — white text on dark background */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {
        color: #FFFFFF !important;
        background-color: #1A1A1A !important;
        border-radius: 6px !important;
        padding: 0.4rem 0.75rem !important;
    }

    /* Hide Streamlit footer */
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Check API key ────────────────────────────────────────────────────────────

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.error(
        "**ANTHROPIC_API_KEY not set.**\n\n"
        "In your terminal run:\n"
        "```\nexport ANTHROPIC_API_KEY=your_key_here\n```\n"
        "Then relaunch with `python3 -m streamlit run gtm_app.py`"
    )
    st.stop()

# ─── Sidebar ──────────────────────────────────────────────────────────────────

# Logo — encode as base64 and inject via HTML (works regardless of Streamlit version)
search_dirs = [os.path.dirname(os.path.abspath(__file__)), os.getcwd()]
logo_file = None
for d in search_dirs:
    for name in ["tigerdata_logo.jpeg", "logo.png", "logo.jpg", "logo.jpeg"]:
        candidate = os.path.join(d, name)
        if os.path.exists(candidate):
            logo_file = candidate
            break
    if logo_file:
        break

if logo_file:
    ext = logo_file.rsplit(".", 1)[-1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    with open(logo_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.sidebar.markdown(
        f'<img src="data:{mime};base64,{encoded}" width="60" style="margin-bottom:8px;">',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown("## 🐯")

st.sidebar.markdown("### Tiger Data")
st.sidebar.markdown("<span style='color:#A3A3A3; font-size:0.8rem;'>GTM Toolkit · Internal use only</span>", unsafe_allow_html=True)
st.sidebar.divider()

tool = st.sidebar.radio(
    "Tools",
    options=[
        "📋  Pre-Call Research Brief",
        "✉️  Cold Email Writer",
        "📝  Call Notes → CRM Summary",
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.markdown("<span style='color:#525252; font-size:0.75rem;'>Powered by Claude AI</span>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='color:#525252; font-size:0.75rem;'>© Tiger Data · Confidential</span>", unsafe_allow_html=True)

# ─── Tool: Pre-Call Research Brief ───────────────────────────────────────────

if "Pre-Call" in tool:

    st.title("Pre-Call Research Brief")
    st.markdown('<p class="tagline">Get an AI-generated research brief before any discovery call.</p>', unsafe_allow_html=True)

    with st.form("brief_form"):
        company_name = st.text_input("Company name *", placeholder="e.g. Stripe")
        website_url  = st.text_input("Website URL",    placeholder="e.g. https://stripe.com")

        col1, col2 = st.columns(2)
        with col1:
            contact_name  = st.text_input("Contact name",  placeholder="e.g. Jane Smith")
        with col2:
            contact_title = st.text_input("Contact title", placeholder="e.g. VP of Engineering")

        submitted = st.form_submit_button("Generate Brief →", use_container_width=True, type="primary")

    if submitted:
        if not company_name.strip():
            st.error("Company name is required.")
        else:
            try:
                from brief_generator import generate_brief, save_as_docx
            except ImportError:
                st.error("Could not find brief_generator.py — make sure it's in the same folder.")
                st.stop()

            with st.spinner(f"Researching {company_name}..."):
                try:
                    brief = generate_brief(company_name, website_url, contact_name, contact_title)
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                    st.stop()

            st.divider()
            st.markdown(f'<div class="brief-output">{brief}</div>', unsafe_allow_html=True)
            st.divider()

            # Generate downloadable .docx
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                save_as_docx(brief, tmp.name)
                with open(tmp.name, "rb") as f:
                    docx_bytes = f.read()

            safe_name = company_name.lower().replace(" ", "_").replace("/", "")
            st.download_button(
                label="⬇️  Download as Word Doc",
                data=docx_bytes,
                file_name=f"brief_{safe_name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

# ─── Tool: Cold Email Writer ──────────────────────────────────────────────────

elif "Cold Email" in tool:
    st.title("✉️ Cold Email Writer")
    st.markdown('<p class="tagline">Generate 3 personalized cold email variations for any prospect.</p>', unsafe_allow_html=True)

    with st.form("email_form"):
        company_name   = st.text_input("Company name *",   placeholder="e.g. Samsara")
        website_url    = st.text_input("Website URL",       placeholder="e.g. https://samsara.com")

        col1, col2 = st.columns(2)
        with col1:
            contact_name  = st.text_input("Contact name",  placeholder="e.g. Jane Smith")
        with col2:
            contact_title = st.text_input("Contact title", placeholder="e.g. VP of Engineering")

        recipient_email = st.text_input("Recipient email (optional)", placeholder="e.g. jane@samsara.com")

        custom_notes = st.text_area(
            "Additional context (optional)",
            placeholder="e.g. They just raised a Series C, recently posted about scaling their data infrastructure, or we share a mutual connection...",
            height=100
        )

        submitted = st.form_submit_button("Generate Emails →", use_container_width=True, type="primary")

    if submitted:
        if not company_name.strip():
            st.error("Company name is required.")
        else:
            try:
                from brief_generator import generate_cold_emails, parse_email_variations
            except ImportError:
                st.error("Could not find brief_generator.py — make sure it's in the same folder.")
                st.stop()

            with st.spinner(f"Writing emails for {company_name}..."):
                try:
                    emails_raw = generate_cold_emails(company_name, website_url, contact_name, contact_title, custom_notes)
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                    st.stop()

            variations = parse_email_variations(emails_raw)

            if not variations:
                # Fallback: just render raw if parsing fails
                st.markdown(emails_raw)
            else:
                to = quote(recipient_email.strip()) if recipient_email.strip() else ""

                for title, subject, body in variations:
                    st.divider()
                    st.markdown(f"### {title}")
                    st.markdown(f"**Subject:** {subject}")
                    st.code(body, language=None)

                    gmail_url   = f"https://mail.google.com/mail/?view=cm&fs=1&to={to}&su={quote(subject)}&body={quote(body)}"
                    outlook_url = f"https://outlook.live.com/mail/0/deeplink/compose?to={to}&subject={quote(subject)}&body={quote(body)}"

                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button("Open in Gmail →", gmail_url, use_container_width=True)
                    with col2:
                        st.link_button("Open in Outlook →", outlook_url, use_container_width=True)

                st.divider()

# ─── Tool: Call Notes → CRM Summary ──────────────────────────────────────────

elif "CRM" in tool:
    st.title("📝 Call Notes → CRM Summary")
    st.markdown('<p class="tagline">Paste your call notes and get a CRM-ready summary plus a MEDDIC scorecard.</p>', unsafe_allow_html=True)

    with st.form("crm_form"):
        call_notes = st.text_area(
            "Call notes *",
            placeholder="Paste your raw call notes or transcript here...",
            height=200
        )

        col1, col2 = st.columns(2)
        with col1:
            company_name  = st.text_input("Company name",  placeholder="e.g. Samsara")
            contact_name  = st.text_input("Contact name",  placeholder="e.g. Jane Smith")
        with col2:
            call_date     = st.text_input("Call date",     placeholder="e.g. March 30, 2026")
            contact_title = st.text_input("Contact title", placeholder="e.g. VP of Engineering")

        submitted = st.form_submit_button("Generate CRM Summary →", use_container_width=True, type="primary")

    if submitted:
        if not call_notes.strip():
            st.error("Call notes are required.")
        else:
            try:
                from brief_generator import generate_crm_summary
            except ImportError:
                st.error("Could not find brief_generator.py — make sure it's in the same folder.")
                st.stop()

            with st.spinner("Generating CRM summary..."):
                try:
                    summary = generate_crm_summary(call_notes, company_name, contact_name, contact_title, call_date)
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                    st.stop()

            st.divider()

            # Split into Part 1 and Part 2 and strip all stray artifacts
            import re as _re
            parts = summary.split("PART 2")
            part1 = parts[0]
            part1 = _re.sub(r'\*{0,2}PART 1[^\n]*\*{0,2}\n?', '', part1)  # any PART 1 header line
            part1 = part1.strip()
            part1 = _re.sub(r'[\*\-\s]+$', '', part1)                      # strip trailing **, ---, spaces
            part1 = part1.strip()

            part2 = ""
            if len(parts) > 1:
                part2 = "PART 2" + parts[1]
                part2 = _re.sub(r'\*{0,2}PART 2\s*[—-]\s*MEDDIC SCORECARD\*{0,2}:?', '', part2)
                part2 = _re.sub(r'^[\-\s]+', '', part2.strip())  # remove leading dashes/spaces only, not *
                part2 = part2.strip()

            st.markdown("#### 📋 Call Summary")
            st.markdown(part1)

            if part2:
                st.markdown("#### 🎯 MEDDIC Scorecard")
                st.markdown(part2)

            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                st.link_button("Open in HubSpot →", "https://app.hubspot.com", use_container_width=True)
            with col2:
                st.link_button("Open in Salesforce →", "https://login.salesforce.com", use_container_width=True)

            st.divider()
