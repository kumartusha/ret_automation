"""
app.py  —  Retail Automation Hub
Run: streamlit run app.py
"""

import streamlit as st

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG — called once at module level for ALL pages
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Retail Automation Hub",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════════
# HUB HOME PAGE
# ════════════════════════════════════════════════════════════════════════
def hub_home():

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    .stApp {
        background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 40%, #fff1f8 70%, #f0f9ff 100%);
        min-height: 100vh;
    }
    .hero-wrap {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 3.5rem 2rem 3rem;
        text-align: center;
        position: relative; overflow: hidden;
    }
    .hero-wrap::before {
        content: ''; position: absolute; inset: 0;
        background: url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.06'%3E%3Ccircle cx='40' cy='40' r='10'/%3E%3C/g%3E%3C/svg%3E");
    }
    .hero-badge {
        display: inline-block; background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.35); color: #fff;
        border-radius: 999px; padding: 5px 18px; font-size: 0.72rem;
        font-weight: 600; letter-spacing: 2px; text-transform: uppercase;
        margin-bottom: 1.2rem; backdrop-filter: blur(8px);
    }
    .hero-title {
        font-size: 2.8rem; font-weight: 800; color: #fff;
        letter-spacing: -1.5px; margin: 0 0 0.8rem;
        text-shadow: 0 2px 20px rgba(0,0,0,0.15);
    }
    .hero-sub { font-size: 1rem; color: rgba(255,255,255,0.85); max-width: 460px; margin: 0 auto; line-height: 1.7; }
    .stats-bar {
        display: flex; justify-content: center; gap: 3rem;
        padding: 1.25rem 2rem;
        background: rgba(255,255,255,0.7);
        border-bottom: 1px solid rgba(102,126,234,0.1);
        backdrop-filter: blur(8px); margin-bottom: 2.5rem;
    }
    .stat-item { text-align: center; }
    .stat-num { font-size: 1.4rem; font-weight: 800; color: #4f46e5; line-height: 1; }
    .stat-lbl { font-size: 0.7rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.2rem; }
    .tool-card {
        background: #fff; border-radius: 20px; padding: 2rem;
        box-shadow: 0 4px 24px rgba(102,126,234,0.08), 0 1px 4px rgba(0,0,0,0.04);
        border: 1px solid rgba(102,126,234,0.1);
        transition: transform 0.22s ease, box-shadow 0.22s ease;
        position: relative; overflow: hidden;
    }
    .tool-card:hover { transform: translateY(-5px); box-shadow: 0 16px 48px rgba(102,126,234,0.18); }
    .card-top-bar { position: absolute; top: 0; left: 0; right: 0; height: 4px; border-radius: 20px 20px 0 0; }
    .bar-challan { background: linear-gradient(90deg,#667eea,#764ba2); }
    .bar-margin  { background: linear-gradient(90deg,#11998e,#38ef7d); }
    .bar-cs      { background: linear-gradient(90deg,#f7971e,#ffd200); }
    .tool-icon { width: 54px; height: 54px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.55rem; margin-bottom: 1.1rem; }
    .icon-challan { background: linear-gradient(135deg,#ede9fe,#ddd6fe); }
    .icon-margin  { background: linear-gradient(135deg,#d1fae5,#a7f3d0); }
    .icon-cs      { background: linear-gradient(135deg,#fef3c7,#fde68a); }
    .tool-tag { display: inline-block; border-radius: 999px; padding: 3px 12px; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 0.75rem; }
    .tag-challan { background: #ede9fe; color: #7c3aed; }
    .tag-margin  { background: #d1fae5; color: #065f46; }
    .tag-cs      { background: #fef3c7; color: #92400e; }
    .tool-name { font-size: 1.15rem; font-weight: 700; color: #1e1b4b; margin-bottom: 0.45rem; letter-spacing: -0.3px; }
    .tool-desc { font-size: 0.845rem; color: #6b7280; line-height: 1.65; margin-bottom: 1.35rem; }
    .tool-features { display: flex; flex-direction: column; gap: 0.38rem; margin-bottom: 1.6rem; }
    .feat { font-size: 0.8rem; display: flex; align-items: center; gap: 0.4rem; }
    .feat-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
    .dot-purple { background: #7c3aed; } .dot-green { background: #059669; } .dot-yellow { background: #d97706; }
    .feat-text { color: #4b5563; }
    div[data-testid="stButton"] button {
        border-radius: 12px !important; font-weight: 600 !important;
        font-size: 0.875rem !important; height: 44px !important;
        width: 100% !important; border: none !important;
        transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
    }
    div[data-testid="stButton"] button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
    .btn-purple button { background: linear-gradient(135deg,#667eea,#764ba2) !important; color: #fff !important; }
    .btn-green  button { background: linear-gradient(135deg,#11998e,#38ef7d) !important; color: #065f46 !important; }
    .btn-yellow button { background: linear-gradient(135deg,#f7971e,#ffd200) !important; color: #78350f !important; }
    .hub-footer { text-align: center; padding: 1.5rem 2rem 2rem; color: #9ca3af; font-size: 0.75rem; }
    .hub-footer code { background: #f3f4f6; color: #6b7280; padding: 1px 6px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-badge">⚙️ &nbsp; Retail Automation</div>
        <div class="hero-title">Automation Hub</div>
        <div class="hero-sub">All your retail operations tools in one place — select a tool below to get started.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats bar ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="stats-bar">
        <div class="stat-item"><div class="stat-num">3</div><div class="stat-lbl">Tools Available</div></div>
        <div class="stat-item"><div class="stat-num">∞</div><div class="stat-lbl">Vehicles Supported</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Cards ─────────────────────────────────────────────────────────
    pad_l, c1, c2, c3, pad_r = st.columns([0.5, 3, 3, 3, 0.5], gap="large")

    with c1:
        st.markdown("""
        <div class="tool-card">
            <div class="card-top-bar bar-challan"></div>
            <div class="tool-icon icon-challan">🚔</div>
            <div class="tool-tag tag-challan">API · Data Fetch</div>
            <div class="tool-name">Challan Data Fetcher</div>
            <div class="tool-desc">Upload vehicle registration numbers, fetch live challan data via the Cuvora API, and export structured results to CSV, Excel, or Google Sheets.</div>
            <div class="tool-features">
                <div class="feat"><div class="feat-dot dot-purple"></div><div class="feat-text">Bulk CSV upload &amp; processing</div></div>
                <div class="feat"><div class="feat-dot dot-purple"></div><div class="feat-text">Live progress tracking</div></div>
                <div class="feat"><div class="feat-dot dot-purple"></div><div class="feat-text">Push results to Google Sheets</div></div>
                <div class="feat"><div class="feat-dot dot-purple"></div><div class="feat-text">Retry &amp; rate-limit handling</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-purple">', unsafe_allow_html=True)
        if st.button("Open Challan Fetcher →", key="btn_challan", use_container_width=True):
            st.switch_page("pages/Challan_Fetcher.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="tool-card">
            <div class="card-top-bar bar-margin"></div>
            <div class="tool-icon icon-margin">📊</div>
            <div class="tool-tag tag-margin">Calculator · Sheets</div>
            <div class="tool-name">Inventory Margin Calculator</div>
            <div class="tool-desc">Search any vehicle by registration number and instantly calculate the expected margin based on landed cost, procurement price, and GST from Google Sheets.</div>
            <div class="tool-features">
                <div class="feat"><div class="feat-dot dot-green"></div><div class="feat-text">Real-time Google Sheets data</div></div>
                <div class="feat"><div class="feat-dot dot-green"></div><div class="feat-text">Margin % with GST calculation</div></div>
                <div class="feat"><div class="feat-dot dot-green"></div><div class="feat-text">ATS &amp; Booked vehicle lookup</div></div>
                <div class="feat"><div class="feat-dot dot-green"></div><div class="feat-text">Interactive price simulator</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("Open Margin Calculator →", key="btn_margin", use_container_width=True):
            st.switch_page("pages/Margin_Calculator.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="tool-card">
            <div class="card-top-bar bar-cs"></div>
            <div class="tool-icon icon-cs">🎫</div>
            <div class="tool-tag tag-cs">Search · Support</div>
            <div class="tool-name">CS Ticket Dashboard</div>
            <div class="tool-desc">Search and review customer support tickets by Ticket ID or registration number — with live escalation status, due dates, and delivery details from Google Sheets.</div>
            <div class="tool-features">
                <div class="feat"><div class="feat-dot dot-yellow"></div><div class="feat-text">Search by Ticket ID or Reg No.</div></div>
                <div class="feat"><div class="feat-dot dot-yellow"></div><div class="feat-text">Live escalation &amp; status data</div></div>
                <div class="feat"><div class="feat-dot dot-yellow"></div><div class="feat-text">Customer &amp; delivery details</div></div>
                <div class="feat"><div class="feat-dot dot-yellow"></div><div class="feat-text">Multi-ticket result view</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-yellow">', unsafe_allow_html=True)
        if st.button("Open CS Dashboard →", key="btn_cs", use_container_width=True):
            st.switch_page("pages/CS_Dashboard.py")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hub-footer">
        Retail Automation Hub
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# NAVIGATION  — module level only, no st commands here
# ════════════════════════════════════════════════════════════════════════
home    = st.Page(hub_home,                     title="Home",              icon="⚙️",  default=True)
challan = st.Page("pages/Challan_Fetcher.py",   title="Challan Fetcher",   icon="🚔")
margin  = st.Page("pages/Margin_Calculator.py", title="Margin Calculator", icon="📊")
cs      = st.Page("pages/CS_Dashboard.py",      title="CS Dashboard",      icon="🎫")

pg = st.navigation([home, challan, margin, cs], position="sidebar")
pg.run()
