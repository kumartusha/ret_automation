"""
Challan Data Fetcher — clean, cloud-compatible single-file app.
"""
import os, time, json, requests
import pandas as pd
import streamlit as st
from io import BytesIO
from dotenv import load_dotenv

# Load centralized .env from project root
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(_ROOT, '.env'))

# ── Config (secrets-first for cloud, env fallback for local) ─────────────
def _secret(key, default=""):
    try: return st.secrets[key]
    except: return os.getenv(key, default)

API_KEY        = _secret("CUVORA_API_KEY")
SHEET_ID       = _secret("GOOGLE_SHEET_ID")
WORKSHEET_NAME = _secret("GOOGLE_SHEET_WORKSHEET", "challan_data")
SA_PATH        = os.getenv("SERVICE_ACCOUNT_PATH", os.path.join(_ROOT, 'service_account.json'))
REQUEST_DELAY  = float(os.getenv("REQUEST_DELAY", "0.3"))
MAX_RETRIES    = int(os.getenv("MAX_RETRIES", "3"))
REQUEST_TIMEOUT= int(os.getenv("REQUEST_TIMEOUT", "15"))
BASE_URL       = "https://api.cuvora.com/car/partner/vehicle/challan/v4/pro"

# ════════════════════════════════════════════════════════════════════════
# CSS (page config is handled by hub app.py)
# ════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f8faff; }
.hero  { background: linear-gradient(135deg,#6366f1,#8b5cf6,#a855f7); border-radius:14px; padding:1.75rem 2rem; margin-bottom:1.5rem; }
.hero-title { font-size:1.7rem; font-weight:800; color:#fff; margin:0; }
.hero-sub   { font-size:.9rem; color:rgba(255,255,255,.85); margin:.3rem 0 0; }
.stat-grid  { display:flex; gap:.75rem; flex-wrap:wrap; margin:.75rem 0; }
.stat-box   { flex:1; min-width:100px; background:#fff; border:1px solid #e0e7ff; border-radius:10px; padding:.9rem; text-align:center; box-shadow:0 1px 6px rgba(99,102,241,.06); }
.stat-number{ font-size:1.6rem; font-weight:700; color:#6366f1; }
.stat-label { font-size:.7rem; color:#94a3b8; text-transform:uppercase; letter-spacing:.5px; }
.step-hd    { font-size:1rem; font-weight:700; color:#1e1b4b; margin:1.25rem 0 .5rem; display:flex; align-items:center; gap:.5rem; }
.step-num   { background:linear-gradient(135deg,#6366f1,#8b5cf6); color:#fff; border-radius:50%; width:26px; height:26px; display:inline-flex; align-items:center; justify-content:center; font-size:.8rem; font-weight:700; flex-shrink:0; }
.warn-box   { background:#fff7ed; border-left:3px solid #f59e0b; border-radius:6px; padding:.6rem .9rem; color:#92400e; font-size:.85rem; margin:.4rem 0; }
.err-box    { background:#fef2f2; border-left:3px solid #ef4444; border-radius:6px; padding:.6rem .9rem; color:#991b1b; font-size:.85rem; margin:.4rem 0; }
.ok-box     { background:#f0fdf4; border-left:3px solid #22c55e; border-radius:6px; padding:.6rem .9rem; color:#15803d; font-size:.85rem; margin:.4rem 0; }
.stProgress > div > div { background:linear-gradient(90deg,#6366f1,#a855f7) !important; border-radius:999px !important; }
.stDownloadButton button { background:linear-gradient(135deg,#6366f1,#8b5cf6) !important; color:#fff !important; border:none !important; border-radius:8px !important; font-weight:600 !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════
def fetch_challan(vehicle_num: str) -> dict:
    headers = {"x-api-key": API_KEY}
    params  = {"apiTag": "CHALLAN_PRO", "vehicle_num": vehicle_num.strip().upper()}
    last_err, http_status = "Unknown error", None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(BASE_URL, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
            http_status = r.status_code
            if r.status_code == 429:
                time.sleep(2 ** attempt); continue
            r.raise_for_status()
            return {"vehicle_num": vehicle_num, "success": True, "data": r.json(), "error": None}
        except requests.exceptions.Timeout:
            last_err = f"Timed out after {REQUEST_TIMEOUT}s"
            if attempt < MAX_RETRIES: time.sleep(1.5 * attempt)
        except requests.exceptions.HTTPError as e:
            return {"vehicle_num": vehicle_num, "success": False, "data": None, "error": f"HTTP {http_status}: {e}"}
        except Exception as e:
            last_err = str(e); break
    return {"vehicle_num": vehicle_num, "success": False, "data": None, "error": last_err}


def parse_csv(f):
    try:
        df = pd.read_csv(f, dtype=str)
        if df.empty: return [], "CSV is empty."
        regs = df.iloc[:, 0].dropna().str.strip().str.upper().replace("", pd.NA).dropna().unique().tolist()
        if not regs: return [], "No valid reg numbers in first column."
        if len(regs) > 250: return [], f"Limit exceeded: CSV contains {len(regs)} vehicles (Max 250 allowed)."
        return regs, None
    except Exception as e:
        return [], f"Failed to read CSV: {e}"


def to_rows(vehicle_num, result):
    base = {"reg_number": vehicle_num, "fetch_status": "SUCCESS" if result["success"] else "ERROR"}
    if not result["success"]:
        return [{**base, "error_message": result.get("error", "")}]
    
    raw = result.get("data") or {}
    # The API returns the challans list inside a nested "data" object
    inner_data = raw.get("data", {})
    challans = inner_data.get("challans", [])
    
    if not challans:
        msg = inner_data.get("message") or raw.get("message") or "No challans found"
        return [{**base, "message": msg}]
        
    rows = []
    for c in challans:
        row = {**base}
        for k, v in c.items():
            if k == "offence" and isinstance(v, list):
                # Extract offence names and join them with commas
                names = [str(o.get("offenceName", "")) for o in v if isinstance(o, dict) and o.get("offenceName")]
                row[k] = ", ".join(names)
            else:
                row[k] = v
        rows.append(row)
        
    return rows


def build_df(rows):
    if not rows: return pd.DataFrame()
    df = pd.DataFrame(rows)
    front = [c for c in ["reg_number","fetch_status","challan_index","error_message"] if c in df.columns]
    return df[front + [c for c in df.columns if c not in front]].reset_index(drop=True)


def to_csv(df):   return df.to_csv(index=False).encode("utf-8")
def to_excel(df):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w: df.to_excel(w, index=False, sheet_name="Challan Data")
    return buf.getvalue()


def get_gspread_client():
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
    except Exception:
        if not os.path.exists(SA_PATH): return None, "❌ Google Sheets connection is not configured."
        with open(SA_PATH) as f: creds_dict = json.load(f)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds), None

def load_cached_data():
    if not SHEET_ID: return pd.DataFrame()
    gc, err = get_gspread_client()
    if not gc: return pd.DataFrame()
    try:
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet(WORKSHEET_NAME)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        if not df.empty and "reg_number" in df.columns:
            df["reg_number"] = df["reg_number"].astype(str).str.strip().str.upper()
        return df
    except Exception:
        return pd.DataFrame()

def log_api_usage(total_fetched, success_count, error_count):
    if not SHEET_ID: return
    gc, err = get_gspread_client()
    if not gc: return
    try:
        sh = gc.open_by_key(SHEET_ID)
        try:    ws = sh.worksheet("API_Logs")
        except Exception: ws = sh.add_worksheet(title="API_Logs", rows=1000, cols=7)
        
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # st.context.headers is available in Streamlit >= 1.37
            headers = st.context.headers
            # Get IP - local development may not have X-Forwarded-For, but deployed apps will
            ip_addr = headers.get("X-Forwarded-For", headers.get("X-Real-IP", "Unknown IP (Local/Direct)"))
            user_agent = headers.get("User-Agent", "Unknown Device")
        except Exception:
            ip_addr = "Unknown IP"
            user_agent = "Unknown Device"
        
        # If empty, add headers first
        if not ws.get_all_values():
            ws.append_row(["Timestamp", "User", "IP_Address", "Device_Info", "Total_Requested", "Successful_Fetches", "Errors"])
            
        ws.append_row([now_str, "Anonymous", ip_addr, user_agent, total_fetched, success_count, error_count])
    except Exception:
        pass

def push_to_sheets(df):
    if not SHEET_ID: return False, "❌ GOOGLE_SHEET_ID not configured."
    gc, err = get_gspread_client()
    if not gc: return False, err
    try:
        sh = gc.open_by_key(SHEET_ID)
        try:    ws = sh.worksheet(WORKSHEET_NAME)
        except Exception: ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=5000, cols=50)
        clean = df.fillna("").astype(str)
        ws.clear()
        ws.update([clean.columns.tolist()] + clean.values.tolist(), value_input_option="USER_ENTERED")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        return True, f"✅ {len(df)} rows pushed to **{WORKSHEET_NAME}** → [Open Sheet]({url})"
    except Exception as e:
        return False, f"❌ {e}"


# ════════════════════════════════════════════════════════════════════════
# UI
# ════════════════════════════════════════════════════════════════════════
def main():
    key_ok = bool(API_KEY and not API_KEY.startswith("your_api"))

    st.markdown('<div class="hero"><div class="hero-title">🚔 Challan Data Fetcher</div><div class="hero-sub">Upload vehicle reg numbers → fetch live challan data → export to CSV / Google Sheets</div></div>', unsafe_allow_html=True)

    if not key_ok:
        st.markdown('<div class="warn-box">⚠️ Challan lookup service is not configured. Please contact your admin.</div>', unsafe_allow_html=True)

    # ── Step 1: Upload ─────────────────────────────────────────────────
    st.markdown('<div class="step-hd"><div class="step-num">1</div> Upload Registration Numbers CSV</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("CSV with reg numbers in column 1", type=["csv"], label_visibility="collapsed", key="challan_upload")

    reg_numbers = []

    if uploaded:
        reg_numbers, err = parse_csv(uploaded)
        if err:
            st.markdown(f'<div class="err-box">❌ {err}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="stat-grid"><div class="stat-box"><div class="stat-number">{len(reg_numbers)}</div><div class="stat-label">Vehicles Found</div></div></div>', unsafe_allow_html=True)
            with st.expander("Preview registration numbers"):
                st.dataframe(pd.DataFrame({"reg_number": reg_numbers}), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Step 2: Fetch ──────────────────────────────────────────────────
    st.markdown('<div class="step-hd"><div class="step-num">2</div> Fetch Challan Data</div>', unsafe_allow_html=True)
    
    start = st.button("🚀 Start Fetching", disabled=(not reg_numbers or not key_ok), use_container_width=True)

    if start and reg_numbers and key_ok:
        total = len(reg_numbers)
        all_rows, ok_ct, err_ct = [], 0, 0
        prog  = st.progress(0)
        stat  = st.empty()
        cards = st.empty()
        
        stat.info("⏳ Checking Google Sheets for cached vehicles...")
        cached_df = load_cached_data()
        cached_regs = []
        if not cached_df.empty and "reg_number" in cached_df.columns:
            cached_regs = cached_df["reg_number"].unique().tolist()
            
        for idx, reg in enumerate(reg_numbers, 1):
            if reg in cached_regs:
                stat.info(f"⚡ Loading **{reg}** from cache ({idx}/{total})")
                vehicle_rows = cached_df[cached_df["reg_number"] == reg].to_dict('records')
                all_rows.extend(vehicle_rows)
                ok_ct += 1
            else:
                stat.info(f"🔍 Fetching API for **{reg}** ({idx}/{total})")
                result = fetch_challan(reg)
                all_rows.extend(to_rows(reg, result))
                if result["success"]: ok_ct += 1
                else: err_ct += 1
                if idx < total and (reg not in cached_regs): time.sleep(REQUEST_DELAY)
                
            prog.progress(idx / total)
            cards.markdown(f'<div class="stat-grid"><div class="stat-box"><div class="stat-number">{idx}</div><div class="stat-label">Processed</div></div><div class="stat-box"><div class="stat-number" style="color:#16a34a">{ok_ct}</div><div class="stat-label">Success</div></div><div class="stat-box"><div class="stat-number" style="color:#dc2626">{err_ct}</div><div class="stat-label">Failed</div></div><div class="stat-box"><div class="stat-number">{total-idx}</div><div class="stat-label">Remaining</div></div></div>', unsafe_allow_html=True)

        stat.success("✅ All vehicles processed!")
        log_api_usage(total, ok_ct, err_ct)
        
        st.session_state["challan_df"]    = build_df(all_rows)
        st.session_state["challan_stats"] = {"total": total, "success": ok_ct, "errors": err_ct, "rows": len(all_rows)}

    # ── Step 3: Results ────────────────────────────────────────────────
    if "challan_df" in st.session_state and not st.session_state["challan_df"].empty:
        df    = st.session_state["challan_df"]
        stats = st.session_state.get("challan_stats", {})

        st.markdown("---")
        st.markdown('<div class="step-hd"><div class="step-num">3</div> Results & Export</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="stat-grid"><div class="stat-box"><div class="stat-number">{stats.get("total","–")}</div><div class="stat-label">Vehicles</div></div><div class="stat-box"><div class="stat-number" style="color:#16a34a">{stats.get("success","–")}</div><div class="stat-label">Success</div></div><div class="stat-box"><div class="stat-number" style="color:#dc2626">{stats.get("errors","–")}</div><div class="stat-label">Failed</div></div><div class="stat-box"><div class="stat-number" style="color:#6366f1">{stats.get("rows","–")}</div><div class="stat-label">Total Rows</div></div></div>', unsafe_allow_html=True)

        with st.expander("📊 Preview Results", expanded=True):
            st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("#### ⬇️ Download")
        c1, c2, _ = st.columns([1, 1, 2])
        with c1:
            st.download_button("📥 CSV", data=to_csv(df), file_name="challan_data.csv", mime="text/csv", use_container_width=True)
        with c2:
            st.download_button("📊 Excel", data=to_excel(df), file_name="challan_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        st.markdown("#### 📄 Push to Google Sheets")
        if not SHEET_ID:
            st.markdown('<div class="warn-box">⚠️ Google Sheets export is not configured. Please contact your admin.</div>', unsafe_allow_html=True)
        else:
            if st.button("📊 Push to Google Sheets", key="push_btn"):
                with st.spinner(f"Writing {len(df)} rows…"):
                    ok, msg = push_to_sheets(df)
                if ok: st.success(msg)
                else:  st.error(msg)

        if "error_message" in df.columns:
            errs = df[df["fetch_status"] == "ERROR"][["reg_number","error_message"]]
            if not errs.empty:
                with st.expander(f"⚠️ {len(errs)} Failed Vehicles"):
                    st.dataframe(errs, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
else:
    main()
