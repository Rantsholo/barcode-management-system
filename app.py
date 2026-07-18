import streamlit as st
import pandas as pd
from datetime import date

#configure the page
st.set_page_config(
    page_title="Barcode Replacement Dashboard",
    page_icon="🏷️",
    layout="wide",
)

from supabase import create_client, Client

def can_access_tab(tab):
    return True

def can_use_feature(feature):
    return True

# customize css
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background-color: #ffffff;
    color: #1a1a1a;
}

h1, h2, h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #007a63 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background-color: #f4f4f4;
    border-bottom: 2px solid #00d4aa;
    gap: 0;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    color: #555555;
    padding: 12px 28px;
    border: none;
    border-radius: 0;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-size: 12px;
}

.stTabs [aria-selected="true"] {
    background-color: #00d4aa !important;
    color: #ffffff !important;
}

.stTabs [data-baseweb="tab-panel"][hidden] {
    display: none !important;
}

.stButton > button {
    font-family: 'IBM Plex Mono', monospace;
    background-color: #00d4aa;
    color: #ffffff;
    font-weight: 600;
    border: none;
    padding: 10px 28px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 12px;
    transition: all 0.2s;
}

.stButton > button:hover {
    background-color: #00b894;
    transform: translateY(-1px);
}

label, .stSelectbox label, .stTextInput label, .stDateInput label, .stNumberInput label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #555555 !important;
}

.stDataFrame {
    border: 1px solid #dddddd;
}

.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #007a63;
    border-bottom: 1px solid #dddddd;
    padding-bottom: 6px;
    margin-bottom: 16px;
    margin-top: 24px;
}

div[data-testid="stNotificationContentSuccess"] {
    background-color: #e6f9f5;
    border-left: 3px solid #00d4aa;
    color: #007a63;
}

.stAlert {
    background-color: #f9f9f9;
    border: 1px solid #dddddd;
}

.metric-box {
    background: #f4f4f4;
    border: 1px solid #dddddd;
    border-left: 3px solid #00d4aa;
    padding: 12px 16px;
    border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 8px;
}

.metric-box .val {
    font-size: 24px;
    font-weight: 600;
    color: #007a63;
}

.metric-box .lbl {
    font-size: 10px;
    color: #777777;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.item-card {
    background: #f9f9f9;
    border: 1px solid #dddddd;
    padding: 16px;
    margin-bottom: 8px;
    border-radius: 2px;
    border-left: 3px solid #00d4aa;
}
</style>
""", unsafe_allow_html=True)

Active_Items = [
    ("1Z", "Sample Mesh Cage Type 1Z", "Aluminium", "140 x 100 x 0.5", "Yes"),
    ("1A", "Sample Mesh Cage Type 1A", "Aluminium", "140 x 100 x 0.5", "Yes"),
    ("BA", "Sample Solid Sided Type BA", "Aluminium", "140 x 100 x 0.5", "Yes"),
    ("AD", "Sample Solid Sided Type AD", "Aluminium", "140 x 100 x 0.5", "Yes"),
    ("PP1", "Sample Plastic Pallet PP1", "Polyester", "", "No"),
    ("PP2", "Sample Plastic Pallet PP2", "Polyester", "", "No"),
    ("1P", "Sample Plastic Bin Type 1P", "Polyester", "", "No"),
    ("2P", "Sample Plastic Bin Type 2P", "Polyester", "", "No"),
    ("SKLB", "Sample Skid Labels", "Skid Labels", "", "No"),
    ("PIK", "Sample Employee Tag", "N/A", "", "No"),
    ("DT50", "Sample Handheld Scanner Label", "Polyester", "", "No"),
    ("PM450", "Sample Printer Label", "Polyester", "", "No"),
    ("RF 008", "Cage tag", "Cage tags", "", "No"),
    ("Cage Tag", "Cage Tag", "Cage Tag", "", "No"),
    ("KLT Bins Tag", "KLT Bins Tag", "KLT Bins Tag", "", "No"),
    ("Omega Agri Bins Tag", "Omega Agri Bins Tag", "Agri Bins Tag", "", "No"),
    ("Crimp Clips", "Crimp Clips", "Crimp Clips", "", "No"),
    ("Metal Plate", "Metal Plate", "Metal Plate", "", "No"),
    ("Stika Type", "Stika Type", "Stika Type", "", "No"),
    ("Zip Lock Bag", "Zip Lock Bag", "Zip Lock Bag", "", "No"),
    ("RFID Tag Inlay", "RFID Tag Inlay", "RFID Tag", "", "No"),
    ("Interlayer", "Interlayer Tag", "Interlayer Tag", "", "No"),
    ("RFID", "Sample RFID Tags", "RFID", "", "No"),
    ("BOC", "Back Order", "N/A", "", "No"),
    ("SSO", "Short Order", "N/A", "", "No"),
]

item_lookup = {row[0]: {"item_desc": row[1], "barcode_type": row[2],
                         "nameplate_size": row[3], "require_nameplate": row[4]}
               for row in Active_Items}

STOCK_TYPES = [row[0] for row in Active_Items]

Tag_Item_Types = {"Interlayer", "Cage Tag", "KLT Bins Tag", "Omega Agri Bins Tag", "Crimp Clips", "Metal Plate", "Stika Type", "Zip Lock Bag", "RFID Tag Inlay"}

MULTIPLIER_ONE_BARCODE_TYPES = {
    "Skid Labels", "Paper", "Bolts", "Nuts",
    "Cage tag", "Cage Tag", "KLT Bins Tag", "Agri Bins Tag", "OMNI ID Tags",
    "Pallet Tag", "Label - KLT tags", "Bins Tag",
    "Brackets", "Interlayer Tag"
}
MULTIPLIER_ONE_STOCK_TYPES = {"DT50", "PM450"}

STOCK_OUT_TAGS_BARCODE_TYPES = {
    "Cage Tag", "KLT Bins Tag", "Agri Bins Tag",
    "OMNI ID Tags", "Pallet Tag", "Label - KLT tags", "Bins Tag",
    "Interlayer Tag", "RF 008"
}
STOCK_OUT_TAGS_STOCK_TYPES = {"RF 008"}

DEPOTS = [
    "Depot 1",
    "Depot 2",
    "Depot 3",
    "Depot 4",
    "Depot 5",
    "Depot 6",
    "Other",
]

ACTIVITIES = ["Barcode Replacement", "Tag Replacement",]

@st.cache_resource
def get_supabase() -> Client:
    """
    Build the Supabase client. Wrapped so a missing/misconfigured
    st.secrets["supabase"] doesn't crash the whole app with an
    unhandled exception before any widget renders.
    """
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except Exception:
        st.error(
            "⚠️ Supabase is not configured. Add a `[supabase]` section with "
            "`url` and `key` to your `secrets.toml` (or Streamlit Cloud "
            "secrets) and reload the app."
        )
        st.stop()

    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"⚠️ Failed to connect to Supabase: {e}")
        st.stop()

supabase = get_supabase()

def load_submissions():
    """Load all rows from Supabase into session state."""
    try:
        response = supabase.table("submissions").select("*").order("id").execute()
        rows = response.data or []
        clean = [{k: v for k, v in r.items() if k != "id"} for r in rows]
        st.session_state.submissions = clean
    except Exception as e:
        st.error(f"Failed to load data from Supabase: {e}")
        st.session_state.submissions = []

def save_rows(rows: list):
    try:
        supabase.table("submissions").insert(rows).execute()
    except Exception as e:
        st.error(f"Failed to save to Supabase: {e}")

def delete_ticket_from_db(ticket_number: str):
    try:
        supabase.table("submissions").delete().eq("Ticket Number", ticket_number).execute()
    except Exception as e:
        st.error(f"Failed to delete from Supabase: {e}")

def clear_all_submissions_db():
    try:
        supabase.table("submissions").delete().neq("id", 0).execute()
    except Exception as e:
        st.error(f"Failed to clear Supabase: {e}")

if "submissions" not in st.session_state:
    load_submissions()

if "item_rows" not in st.session_state:
    st.session_state.item_rows = [{}]

if "form_key" not in st.session_state:
    st.session_state.form_key = 0

def get_item_info(stock_type):
    return item_lookup.get(stock_type, {"item_desc": "", "barcode_type": "",
                                         "nameplate_size": "", "require_nameplate": "No"})

def is_tag_based(stock_type, barcode_type):
    return stock_type in Tag_Item_Types or barcode_type in Tag_Item_Types

def compute_multiplier(stock_type, barcode_type):
    if barcode_type in MULTIPLIER_ONE_BARCODE_TYPES or stock_type in MULTIPLIER_ONE_STOCK_TYPES:
        return 1
    return 2

def compute_stock_out(stock_type, barcode_type, tags, total_barcodes, total_nameplates):
    if stock_type in STOCK_OUT_TAGS_STOCK_TYPES or barcode_type in STOCK_OUT_TAGS_BARCODE_TYPES:
        return tags if tags else 0
    return (total_barcodes or 0) + (total_nameplates or 0)

def na_if_empty(val):
    if val is None or str(val).strip() == "":
        return "N/A"
    return val

def compute_item_type_qty(item_desc, barcode_type, stock_type, tags, total_barcodes,
                           barcodes_requested, nameplate_val, multiplier):
    m = str(multiplier)
    if is_tag_based(stock_type, barcode_type):
        t = tags if tags else 0
        return f"{item_desc}({t}x{m})"
    if nameplate_val == "Yes":
        tb = total_barcodes if total_barcodes else 0
        return f"{item_desc}({tb}x{m})"
    br = barcodes_requested if barcodes_requested else 0
    return f"{item_desc}({br}x{m})"

# Main User Interface
st.markdown("# 🏷️ BARCODE REPLACEMENT DASHBOARD")

st.caption("Open Access")
st.markdown("---")

TAB_LABELS = {"capture": "CAPTURE FORM", "submissions": "SUBMISSIONS TABLE", "delivery": "DELIVERY NOTE"}
accessible_tabs = [t for t in ["capture", "submissions", "delivery"] if can_access_tab(t)]
tab_objects = st.tabs([TAB_LABELS[t] for t in accessible_tabs])
tab_map = {key: tab_objects[i] for i, key in enumerate(accessible_tabs)}


def get_tab(name):
    return tab_map.get(name, None)


if get_tab('capture'):
  with get_tab('capture'):
    st.markdown("### REQUEST DETAILS")

    col1, col2, col3 = st.columns(3)
    with col1:
        date_sent = st.date_input("Date Sent", value=date.today(), key=f"date_sent_{st.session_state.form_key}")
    with col2:
        activity = st.selectbox("Activity", ["— Select Activity —"] + ACTIVITIES, key=f"activity_{st.session_state.form_key}")
    with col3:
        ticket_number = st.text_input("Ticket Number *", key=f"ticket_number_{st.session_state.form_key}")

    po_number = ""
    capex_number = ""
    if activity == "Outright Sale":
        po_number = st.text_input("Purchase Order Number *", placeholder="Required for Outright Sale", key=f"po_number_{st.session_state.form_key}")
    elif activity == "Capex":
        capex_number = st.text_input("Capex Number *", placeholder="Required for Capex", key=f"capex_number_{st.session_state.form_key}")

    col4, col5 = st.columns(2)
    with col4:
        requested_by = st.text_input("Requested By *", key=f"requested_by_{st.session_state.form_key}")
    with col5:
        depot_choice = st.selectbox("Issued To *", ["— Select Depot —"] + DEPOTS, key=f"depot_choice_{st.session_state.form_key}")
        issued_to = depot_choice
        if depot_choice == "Other":
            issued_to = st.text_input("Enter Depot Name", key=f"issued_to_{st.session_state.form_key}")

    col6, col7 = st.columns(2)
    with col6:
        waybill = st.text_input("Waybill", key=f"waybill_{st.session_state.form_key}")
    with col7:
        take_on_scan = st.selectbox("Take-On Scan", ["No", "Yes"], key=f"take_on_scan_{st.session_state.form_key}")

    comment = st.text_input("Comment", key=f"comment_{st.session_state.form_key}")

    st.markdown("---")
    st.markdown("### ITEM TYPES")
    st.caption("Add one row per item type. Fields auto-populate from the Active Item Types table.")

    def add_row():
        st.session_state.item_rows.append({})

    def remove_row(idx):
        if len(st.session_state.item_rows) > 1:
            st.session_state.item_rows.pop(idx)

    for i, _ in enumerate(st.session_state.item_rows):
        with st.container():
            st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
            st.markdown(f"**ITEM {i+1}**")

            c1, c2, c3 = st.columns([2, 3, 1])
            with c1:
                stock_type = st.selectbox(
                    "Stock Type",
                    [""] + STOCK_TYPES,
                    key=f"st_{i}_{st.session_state.form_key}",
                )

            info = get_item_info(stock_type) if stock_type else {"item_desc": "", "barcode_type": "", "nameplate_size": "", "require_nameplate": "No"}
            item_desc = info["item_desc"]
            require_nameplate = info["require_nameplate"]
            barcode_type = info["barcode_type"]
            nameplate_size = info["nameplate_size"]

            with c2:
                st.text_input(
                    "Item Description (auto-populated)",
                    value=item_desc,
                    key=f"id_{i}_{stock_type}_{st.session_state.form_key}",
                    disabled=True,
                )
            with c3:
                if st.button("✕", key=f"del_{i}_{st.session_state.form_key}", help="Remove this row"):
                    remove_row(i)
                    st.rerun()

            if barcode_type == "Aluminium" and require_nameplate == "Yes":
                col_np1, col_np2 = st.columns(2)
                with col_np1:
                    st.text_input(
                        "Nameplate (auto-populated)",
                        value=require_nameplate,
                        key=f"np_{i}_{stock_type}_{st.session_state.form_key}",
                        disabled=True,
                    )
                with col_np2:
                    if nameplate_size:
                        st.text_input(
                            "Nameplate Size",
                            value=nameplate_size,
                            key=f"nps_{i}_{stock_type}_{st.session_state.form_key}",
                            disabled=True,
                        )

            tag_based = is_tag_based(stock_type, barcode_type)

            if not tag_based:
                c4, c5 = st.columns(2)
                with c4:
                    barcodes_requested = st.number_input(
                        "Barcodes Requested",
                        min_value=0,
                        value=0,
                        step=1,
                        key=f"br_{i}_{st.session_state.form_key}",
                    )
            else:
                barcodes_requested = 0

            if tag_based:
                c6, _ = st.columns(2)
                with c6:
                    tags = st.number_input(
                        "Tags",
                        min_value=0,
                        value=0,
                        step=1,
                        key=f"tg_{i}_{st.session_state.form_key}",
                    )
            else:
                tags = 0

            multiplier = compute_multiplier(stock_type, barcode_type)
            total_barcodes = barcodes_requested * multiplier if not tag_based else 0

            total_nameplates = 0
            if require_nameplate == "Yes" and not tag_based:
                total_nameplates = total_barcodes

            stock_out = compute_stock_out(stock_type, barcode_type, tags,
                                          total_barcodes, total_nameplates)

            if require_nameplate == "Yes" and not tag_based:
                st.info(f"**Total Nameplates:** {total_nameplates}  |  **Total Barcodes:** {total_barcodes}  |  **Stock Out:** {stock_out}")
            elif not tag_based:
                st.info(f"**Total Barcodes:** {total_barcodes}  |  **Stock Out:** {stock_out}")
            else:
                st.info(f"**Stock Out (Tags):** {stock_out}")

            st.session_state.item_rows[i] = {
                "stock_type": stock_type,
                "item_desc": item_desc,
                "barcode_type": barcode_type,
                "require_nameplate": require_nameplate,
                "nameplate_size": nameplate_size,
                "barcodes_requested": barcodes_requested,
                "tags": tags,
                "multiplier": multiplier,
                "total_barcodes": total_barcodes,
                "total_nameplates": total_nameplates,
                "stock_out": stock_out,
            }

            st.markdown('</div>', unsafe_allow_html=True)

    st.button("➕  Add Another Item Type", on_click=add_row)

    st.markdown("---")

    if st.button("  SUBMIT REQUEST"):
        errors = []
        if activity == "— Select Activity —":
            errors.append("Activity is required.")
        if not ticket_number.strip():
            errors.append("Ticket Number is required.")
        if not requested_by.strip():
            errors.append("Requested By is required.")
        if depot_choice == "— Select Depot —":
            errors.append("Issued To is required.")
        if activity == "Outright Sale" and not po_number.strip():
            errors.append("Purchase Order Number is required for Outright Sale.")
        if activity == "Capex" and not capex_number.strip():
            errors.append("Capex Number is required for Capex.")
        if depot_choice == "Other" and not issued_to.strip():
            errors.append("Please enter a depot name when 'Other' is selected.")
        if not any(r.get("stock_type") for r in st.session_state.item_rows):
            errors.append("Please select at least one Stock Type.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            new_rows = []
            for r in st.session_state.item_rows:
                if not r.get("stock_type"):
                    continue
                item_type = r["stock_type"]
                multiplier = r["multiplier"]
                item_type_qty = compute_item_type_qty(
                    r["item_desc"], r["barcode_type"], r["stock_type"],
                    r["tags"], r["total_barcodes"],
                    r["barcodes_requested"], r["require_nameplate"], multiplier
                )

                new_rows.append({
                    "Date Sent": str(date_sent),
                    "Stock Type": na_if_empty(r["stock_type"]),
                    "Activity": na_if_empty(activity),
                    "Item Description": na_if_empty(r["barcode_type"]),
                    "Barcodes Requested": na_if_empty(r["barcodes_requested"] if not is_tag_based(r["stock_type"], r["barcode_type"]) else ""),
                    "Total Barcodes": na_if_empty(r["total_barcodes"] if r["total_barcodes"] else ""),
                    "Total Nameplates": na_if_empty(r["total_nameplates"] if r["total_nameplates"] else ""),
                    "Tags": na_if_empty(r["tags"] if is_tag_based(r["stock_type"], r["barcode_type"]) else ""),
                    "Stock Out": na_if_empty(r["stock_out"]),
                    "Take-On": na_if_empty(take_on_scan),
                    "Nameplate": na_if_empty(r["require_nameplate"]),
                    "Requested By": na_if_empty(requested_by),
                    "Issued To": na_if_empty(issued_to),
                    "Ticket Number": na_if_empty(ticket_number),
                    "Waybill": na_if_empty(waybill),
                    "Comment": na_if_empty(comment),
                    "Item Type": na_if_empty(r["item_desc"]),
                    "Multiplier": multiplier,
                    "Item Type (Quantity)": item_type_qty,
                    "PO Number": na_if_empty(po_number) if activity == "Outright Sale" else "N/A",
                    "Capex Number": na_if_empty(capex_number) if activity == "Capex" else "N/A",
                })

            st.session_state.submissions.extend(new_rows)
            save_rows(new_rows)
            st.session_state.item_rows = [{}]
            st.session_state.form_key += 1
            st.success(f"✅ {len(new_rows)} item(s) submitted successfully!")
            st.rerun()


if get_tab('submissions'):
  with get_tab('submissions'):
    st.markdown("### ALL SUBMISSIONS")

    if not st.session_state.submissions:
        st.info("No submissions yet. Use the Capture Form tab to submit requests.")
    else:
        df_all = pd.DataFrame(st.session_state.submissions)

        numeric_cols = ["Barcodes Requested", "Total Barcodes", "Total Nameplates",
                        "Tags", "Stock Out", "Multiplier"]
        for col in numeric_cols:
            if col in df_all.columns:
                df_all[col] = pd.to_numeric(df_all[col], errors="coerce").fillna(0).astype(int)

        str_cols = ["Date Sent", "Stock Type", "Activity", "Item Description",
                    "Requested By", "Issued To", "Ticket Number", "Waybill",
                    "Capex Number", "PO Number", "Comment", "Item Type", "Nameplate",
                    "Take-On", "Item Type (Quantity)"]
        for col in str_cols:
            if col in df_all.columns:
                df_all[col] = df_all[col].astype(str).str.strip().replace({"nan": "N/A", "None": "N/A", "none": "N/A"})

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-box"><div class="val">{len(df_all)}</div><div class="lbl">Total Rows</div></div>', unsafe_allow_html=True)
        with m2:
            total_stock_out = sum(
                float(v) for v in df_all["Stock Out"].tolist()
                if str(v).replace(".", "").isdigit()
            )
            st.markdown(f'<div class="metric-box"><div class="val">{int(total_stock_out)}</div><div class="lbl">Total Stock Out</div></div>', unsafe_allow_html=True)
        with m3:
            unique_depots = df_all["Issued To"].nunique()
            st.markdown(f'<div class="metric-box"><div class="val">{unique_depots}</div><div class="lbl">Depots</div></div>', unsafe_allow_html=True)
        with m4:
            unique_tickets = df_all["Ticket Number"].replace("N/A", pd.NA).dropna().nunique()
            st.markdown(f'<div class="metric-box"><div class="val">{unique_tickets}</div><div class="lbl">Tickets</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        st.markdown('<div class="section-header">FILTERS</div>', unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)

        with fc1:
            all_dates = sorted([str(v) for v in df_all["Date Sent"].unique() if v is not None and str(v) not in ("nan", "N/A", "")])
            sel_dates = st.multiselect("Date Sent", options=all_dates, default=[])
        with fc2:
            all_tickets = [t for t in sorted([str(v) for v in df_all["Ticket Number"].unique() if v is not None and str(v) not in ("nan", "N/A", "")])]
            sel_tickets = st.multiselect("Ticket Number", options=all_tickets, default=[])
        with fc3:
            all_activities = sorted([str(v) for v in df_all["Activity"].unique() if v is not None and str(v) not in ("nan", "N/A", "")])
            sel_activities = st.multiselect("Activity", options=all_activities, default=[])
        with fc4:
            all_requestors = sorted([str(v) for v in df_all["Requested By"].unique() if v is not None and str(v) not in ("nan", "N/A", "")])
            sel_requestors = st.multiselect("Requested By", options=all_requestors, default=[])

        mask = pd.Series([True] * len(df_all))
        if sel_dates:
            mask &= df_all["Date Sent"].isin(sel_dates)
        if sel_tickets:
            mask &= df_all["Ticket Number"].isin(sel_tickets)
        if sel_activities:
            mask &= df_all["Activity"].isin(sel_activities)
        if sel_requestors:
            mask &= df_all["Requested By"].isin(sel_requestors)

        filtered_indices = df_all[mask].index.tolist()
        df = df_all.loc[filtered_indices].reset_index(drop=True)

        st.caption(f"Showing {len(df)} of {len(df_all)} rows")
        st.markdown("---")

        display_cols = [
            "Date Sent", "Stock Type", "Activity", "Item Description",
            "Barcodes Requested", "Total Barcodes", "Total Nameplates",
            "Tags", "Stock Out", "Take-On", "Nameplate",
            "Requested By", "Issued To", "Ticket Number", "Waybill", "Capex Number", "PO Number",
            "Comment", "Item Type", "Multiplier", "Item Type (Quantity)",
        ]
        display_cols = [c for c in display_cols if c in df.columns]

        display_df = df[display_cols].copy().reset_index(drop=True)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        if can_use_feature("delete_ticket"):
            st.markdown("#### 🗑️ Delete by Ticket Number")
            all_tickets = sorted([t for t in df_all["Ticket Number"].unique() if t != "N/A"])
            if all_tickets:
                del_col1, del_col2 = st.columns([2, 1])
                with del_col1:
                    ticket_to_delete = st.selectbox("Select Ticket to Delete", options=all_tickets, key="del_ticket")
                with del_col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️  DELETE TICKET"):
                        st.session_state["pending_delete_ticket"] = ticket_to_delete

                if st.session_state.get("pending_delete_ticket") == ticket_to_delete:
                    row_count = sum(
                        1 for r in st.session_state.submissions
                        if str(r.get("Ticket Number", "")) == str(ticket_to_delete)
                    )
                    st.warning(f"⚠️ Are you sure you want to delete ticket **'{ticket_to_delete}'**? This will remove **{row_count} row(s)** and cannot be undone.")
                    conf_col1, conf_col2, _ = st.columns([1, 1, 4])
                    with conf_col1:
                        if st.button("✅ Yes, delete", key="confirm_delete_yes"):
                            st.session_state.submissions = [
                                r for r in st.session_state.submissions
                                if str(r.get("Ticket Number", "")) != str(ticket_to_delete)
                            ]
                            delete_ticket_from_db(ticket_to_delete)
                            st.session_state.pop("pending_delete_ticket", None)
                            st.success(f"Ticket '{ticket_to_delete}' deleted.")
                            st.rerun()
                    with conf_col2:
                        if st.button("✕ Cancel", key="confirm_delete_no"):
                            st.session_state.pop("pending_delete_ticket", None)
                            st.rerun()
            else:
                st.info("No tickets with Ticket Numbers found.")

            st.markdown("---")

        st.markdown("Import Data")
        uploaded_file = st.file_uploader(
            "Upload a previously exported CSV or Excel file to restore data",
            type=["csv", "xlsx"],
            key="import_uploader"
        )
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    import_df = pd.read_csv(uploaded_file, dtype=str).fillna("N/A")
                else:
                    import_df = pd.read_excel(uploaded_file, dtype=str).fillna("N/A")

                required_cols = {"Ticket Number", "Date Sent", "Stock Type",
                                  "Activity", "Requested By", "Issued To"}
                missing_cols = required_cols - set(import_df.columns)

                if missing_cols:
                    st.error(
                        f"❌ This file can't be imported — it's missing required "
                        f"column(s): {', '.join(sorted(missing_cols))}. "
                        f"Please upload a file exported from this app."
                    )
                else:
                    numeric_cols = ["Barcodes Requested", "Total Barcodes", "Total Nameplates",
                                    "Tags", "Stock Out", "Multiplier"]
                    for col in numeric_cols:
                        if col in import_df.columns:
                            import_df[col] = pd.to_numeric(import_df[col], errors="coerce").fillna(0).astype(int)

                    str_cols = ["Date Sent", "Stock Type", "Activity", "Item Description",
                                "Requested By", "Issued To", "Ticket Number", "Waybill",
                                "Capex Number", "PO Number", "Comment", "Item Type",
                                "Nameplate", "Take-On", "Item Type (Quantity)"]
                    for col in str_cols:
                        if col in import_df.columns:
                            import_df[col] = import_df[col].astype(str).str.strip().replace({"nan": "N/A", "None": "N/A", "none": "N/A"})

                    imp_col1, imp_col2 = st.columns([2, 1])
                    with imp_col1:
                        st.success(f"File loaded: **{len(import_df)} rows** detected. Choose how to import:")
                    with imp_col2:
                        import_mode = st.radio(
                            "Import mode",
                            ["Append to existing", "Replace all data"],
                            key="import_mode"
                        )

                    if st.button("✅ CONFIRM IMPORT"):
                        imported_records = import_df.to_dict(orient="records")
                        if import_mode == "Replace all data":
                            clear_all_submissions_db()
                            save_rows(imported_records)
                            st.session_state.submissions = imported_records
                            st.success(f"All data replaced with {len(imported_records)} imported rows.")
                        else:
                            save_rows(imported_records)
                            st.session_state.submissions.extend(imported_records)
                            st.success(f"{len(imported_records)} rows appended to existing data.")
                        st.rerun()

            except Exception as e:
                st.error(f"Failed to read file: {e}")

        st.markdown("---")

        import io
        dl1, dl2, dl3 = st.columns([1, 1, 4])
        export_df = df_all[display_cols]

        with dl1:
            csv_data = export_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️  CSV",
                data=csv_data,
                file_name="barcode_requests.csv",
                mime="text/csv",
            )
        with dl2:
            xlsx_buf = io.BytesIO()
            with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Submissions")
            xlsx_buf.seek(0)
            st.download_button(
                label="⬇️  EXCEL",
                data=xlsx_buf.read(),
                file_name="barcode_requests.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

DEPOT_INFO = {
    "Depot 1":   {"full_name": "Sample Depot 1", "street": "1 Example Street",   "city": "Sample City",   "postal": "0001", "contact": "Jane Doe",   "tel": "000 000 0001"},
    "Depot 2":   {"full_name": "Sample Depot 2", "street": "2 Example Street",   "city": "Sample City",   "postal": "0002", "contact": "John Smith", "tel": "000 000 0002"},
    "Depot 3":   {"full_name": "Sample Depot 3", "street": "3 Example Street",   "city": "Sample City",   "postal": "0003", "contact": "Alex Brown", "tel": "000 000 0003"},
    "Depot 4":   {"full_name": "Sample Depot 4", "street": "4 Example Street",   "city": "Sample City",   "postal": "0004", "contact": "Sam Jones",  "tel": "000 000 0004"},
    "Depot 5":    {"full_name": "Sample Depot 5", "street": "5 Example Street",   "city": "Sample City",   "postal": "0005", "contact": "Chris Lee",  "tel": "000 000 0005"},
    "Depot 6":   {"full_name": "Sample Depot 6", "street": "6 Example Street",   "city": "Sample City",   "postal": "0006", "contact": "Pat Taylor", "tel": "000 000 0006"},
    "Sample Site A": {"full_name": "Sample Site A", "street": "7 Example Street",  "city": "Sample City",   "postal": "0007", "contact": "",           "tel": ""},
    "Sample Site B": {"full_name": "Sample Site B", "street": "8 Example Street",  "city": "Sample City",   "postal": "0008", "contact": "",           "tel": ""},
    "Sample Site C": {"full_name": "Sample Site C", "street": "9 Example Street",  "city": "Sample City",   "postal": "0009", "contact": "",           "tel": ""},
    "Sample Site D": {"full_name": "Sample Site D", "street": "10 Example Street", "city": "Sample City",   "postal": "0010", "contact": "Morgan Diaz","tel": "000 000 0010"},
    "Sample Site E": {"full_name": "Sample Site E", "street": "11 Example Street", "city": "Sample City",   "postal": "0011", "contact": "",           "tel": ""},
}

if get_tab('delivery'):
  with get_tab('delivery'):
    st.markdown("### DELIVERY NOTE")

    if not st.session_state.submissions:
        st.info("No submissions yet. Use the Capture Form tab to submit requests.")
    else:
        df_dn = pd.DataFrame(st.session_state.submissions)
        if "Ticket Number" not in df_dn.columns:
            df_dn["Ticket Number"] = "N/A"
        available_tickets = sorted([t for t in df_dn["Ticket Number"].unique() if t != "N/A"])

        if not available_tickets:
            st.info("No submissions with Ticket Numbers found.")
        else:
            selected_ticket = st.selectbox(
                "Select Ticket Number",
                options=available_tickets,
                key="dn_ticket_select"
            )

            ticket_rows = df_dn[df_dn["Ticket Number"] == selected_ticket].reset_index(drop=True)
            first = ticket_rows.iloc[0]
            issued_to_val = str(first.get("Issued To", ""))
            depot_data = DEPOT_INFO.get(issued_to_val, {
                "full_name": issued_to_val, "street": "", "city": "", "postal": "",
                "contact": "", "tel": ""
            })

            st.markdown("---")
            st.markdown('<div class="section-header">EDITABLE FIELDS</div>', unsafe_allow_html=True)

            ec1, ec2 = st.columns(2)
            with ec1:
                doc_number     = st.text_input("Document #", value="", key=f"dn_doc_number_{selected_ticket}")
                invoice_number = st.text_input("Per Invoice Number", value="", key=f"dn_invoice_{selected_ticket}")
            with ec2:
                st.markdown(f"**Our Contact Person:** {depot_data['contact']}")
                st.markdown(f"**Telephone:** {depot_data['tel']}")

            st.markdown("##### Delivery Address")
            if can_use_feature("delete_ticket"):
                addr1, addr2 = st.columns(2)
                with addr1:
                    addr_name   = st.text_input("Company / Depot Name", value=depot_data['full_name'], key=f"dn_addr_name_{selected_ticket}")
                    addr_street = st.text_input("Street", value=depot_data['street'], key=f"dn_addr_street_{selected_ticket}")
                with addr2:
                    addr_city   = st.text_input("City / Town", value=depot_data['city'], key=f"dn_addr_city_{selected_ticket}")
                    addr_postal = st.text_input("Postal Code", value=depot_data['postal'], key=f"dn_addr_postal_{selected_ticket}")
            else:
                addr_name   = depot_data['full_name']
                addr_street = depot_data['street']
                addr_city   = depot_data['city']
                addr_postal = depot_data['postal']
                st.markdown(f"**{addr_name}**  \n{addr_street}  \n{addr_city}  \n{addr_postal}")

            st.markdown("---")

            line_items_html = ""
            for _, row in ticket_rows.iterrows():
                stock_out_val = row.get("Stock Out", "")
                item_qty_val  = row.get("Item Type (Quantity)", "")
                line_items_html += f"""
                <tr>
                    <td style="padding:8px 12px;border:1px solid #ccc;text-align:center;">{stock_out_val}</td>
                    <td style="padding:8px 12px;border:1px solid #ccc;">{item_qty_val}</td>
                </tr>"""

            for _ in range(max(0, 16 - len(ticket_rows))):
                line_items_html += """
                <tr>
                    <td style="padding:8px 12px;border:1px solid #ccc;height:28px;">&nbsp;</td>
                    <td style="padding:8px 12px;border:1px solid #ccc;">&nbsp;</td>
                </tr>"""

            date_val      = str(first.get("Date Sent", ""))
            attention_val = str(first.get("Requested By", ""))

            delivery_note_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 10mm 10mm 10mm 10mm; }}
  @media print {{ .no-print {{ display:none !important; }} html, body {{ width:100%; }} body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; font-size: 10px; }} }}
  * {{ box-sizing: border-box; }}
  html {{
    background: #ffffff !important;
  }}
  body {{
    font-family: Arial, sans-serif;
    font-size: 11px;
    color: #000;
    background: #ffffff !important;
    padding: 20px 28px;
    max-width: 794px;
    margin: 0 auto;
  }}

  .print-btn {{
    display: block; margin: 0 auto 16px auto;
    padding: 9px 36px; background: #1a1a1a; color: #fff;
    font-size: 12px; font-weight: bold; letter-spacing: 0.1em;
    text-transform: uppercase; border: none; cursor: pointer; border-radius: 2px;
  }}
  .print-btn:hover {{ background: #333; }}

  .logo-row {{
    display: flex; justify-content: flex-end; margin-bottom: 4px;
  }}
  .logo-placeholder {{
    font-family: Arial, sans-serif;
    font-weight: bold;
    font-size: 18px;
    letter-spacing: 0.08em;
    color: #1a1a1a;
    border: 2px solid #1a1a1a;
    padding: 6px 14px;
    display: inline-block;
  }}

  .dn-title {{
    text-align: center; font-size: 18px; font-weight: bold;
    letter-spacing: 0.08em; text-transform: uppercase;
    margin-bottom: 14px;
  }}

  .header-section {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 24px;
    margin-bottom: 14px;
    border-top: 1.5px solid #000;
    padding-top: 6px;
  }}
  .hrow {{
    display: flex; align-items: flex-end;
    margin-bottom: 5px;
    border-bottom: 1px solid #bbb;
    padding-bottom: 3px;
  }}
  .hrow.no-line {{ border-bottom: none; }}
  .hlabel {{
    font-weight: bold; font-size: 10px; white-space: nowrap;
    min-width: 110px; padding-right: 6px; padding-bottom: 1px;
  }}
  .hvalue {{
    font-size: 11px; flex: 1; padding-bottom: 1px;
  }}

  table.items {{
    width: 100%; border-collapse: collapse; margin-bottom: 14px;
  }}
  table.items th {{
    background: #000; color: #fff;
    padding: 6px 10px; font-size: 10px;
    text-align: left; font-weight: bold;
  }}
  table.items th:first-child {{ width: 26%; }}
  table.items td {{
    padding: 5px 10px; border: 1px solid #999; font-size: 11px;
  }}
  table.items td:first-child {{ text-align: center; border-right: 2px solid #555; }}
  table.items tr.empty-row td {{ height: 22px; }}

  .sig-box {{
    border: 1px solid #000; padding: 10px 12px; margin-bottom: 10px;
  }}
  .sig-box-title {{
    font-weight: bold; font-size: 10px; margin-bottom: 10px;
  }}
  .sig-row {{
    display: flex; align-items: flex-end; gap: 16px; margin-top: 8px;
  }}
  .sig-field {{
    display: flex; align-items: flex-end; flex: 1;
  }}
  .sig-field-label {{
    font-size: 10px; white-space: nowrap; margin-right: 6px; font-weight: bold;
  }}
  .sig-field-line {{
    border-bottom: 1px solid #000; flex: 1; min-width: 80px; height: 16px;
  }}
  .waybill-row {{
    display: flex; align-items: flex-end; margin-bottom: 8px;
  }}
  .waybill-label {{
    font-size: 10px; margin-right: 6px; white-space: nowrap;
  }}
  .waybill-line {{
    border-bottom: 1px solid #000; flex: 1;
  }}

  .footer {{
    border-top: 1.5px solid #000; margin-top: 14px;
    padding-top: 8px;
    display: flex; align-items: center; gap: 0;
  }}
  .footer-left {{ font-size: 7.5px; color: #333; line-height: 1.6; flex: 1; }}
  .footer-divider {{ width: 1.5px; background: #000; align-self: stretch; margin: 0 12px; }}
  .footer-company-block {{ text-align: right; white-space: nowrap; margin-right: 10px; }}
  .footer-company-name {{ font-size: 10px; font-weight: bold; color: #000; }}
  .footer-company-reg {{ font-size: 8px; color: #333; }}
  .footer-logo-placeholder {{
    font-family: Arial, sans-serif;
    font-weight: bold;
    font-size: 10px;
    letter-spacing: 0.05em;
    color: #1a1a1a;
    border: 1px solid #1a1a1a;
    border-radius: 50%;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    margin-left: 10px;
  }}
</style>
</head>
<body>

<button class="print-btn no-print" onclick="window.print()">🖨&nbsp; PRINT / SAVE AS PDF</button>

<div class="logo-row">
  <span class="logo-placeholder">ACME LOGISTICS</span>
</div>

<div class="dn-title">DELIVERY NOTE</div>

<div class="header-section">
  <div>
    <div class="hrow">
      <div class="hlabel">To :</div>
      <div class="hvalue">{addr_name}</div>
    </div>
    <div class="hrow">
      <div class="hlabel">Address :</div>
      <div class="hvalue">{addr_street}</div>
    </div>
    <div class="hrow no-line">
      <div class="hlabel"></div>
      <div class="hvalue">{addr_city}</div>
    </div>
    <div class="hrow">
      <div class="hlabel"></div>
      <div class="hvalue">{addr_postal}</div>
    </div>
    <div class="hrow">
      <div class="hlabel">Attention :</div>
      <div class="hvalue">{attention_val}</div>
    </div>
  </div>

  <div>
    <div class="hrow">
      <div class="hlabel">Your Order Number :</div>
      <div class="hvalue">{selected_ticket}</div>
    </div>
    <div class="hrow">
      <div class="hlabel">Date Sent :</div>
      <div class="hvalue">{date_val}</div>
    </div>
    <div class="hrow">
      <div class="hlabel">Per Invoice Number :</div>
      <div class="hvalue">{invoice_number}</div>
    </div>
    <div class="hrow">
      <div class="hlabel">Our Contact Person :</div>
      <div class="hvalue">{depot_data['contact']}</div>
    </div>
    <div class="hrow">
      <div class="hlabel">Telephone :</div>
      <div class="hvalue">{depot_data['tel']}</div>
    </div>
    <div class="hrow">
      <div class="hlabel">Document # :</div>
      <div class="hvalue">{doc_number}</div>
    </div>
  </div>
</div>

<table class="items">
  <thead>
    <tr>
      <th>Quantity Delivered</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    {line_items_html}
  </tbody>
</table>

<div class="sig-box">
  <div class="sig-box-title">Transporter &#8211; Collection Note - Goods received in good order</div>
  <div class="waybill-row">
    <span class="waybill-label">Waybill Number:</span>
    <span class="waybill-line"></span>
  </div>
  <div class="sig-row">
    <div class="sig-field">
      <span class="sig-field-label">Name :</span>
      <span class="sig-field-line"></span>
    </div>
    <div class="sig-field">
      <span class="sig-field-label">Signature :</span>
      <span class="sig-field-line"></span>
    </div>
    <div class="sig-field" style="flex:0.5;">
      <span class="sig-field-label">Date :</span>
      <span class="sig-field-line"></span>
    </div>
  </div>
</div>

<div class="sig-box">
  <div class="sig-box-title">Goods received in good order</div>
  <div class="sig-row">
    <div class="sig-field">
      <span class="sig-field-label">Name :</span>
      <span class="sig-field-line"></span>
    </div>
    <div class="sig-field">
      <span class="sig-field-label">Signature :</span>
      <span class="sig-field-line"></span>
    </div>
    <div class="sig-field" style="flex:0.5;">
      <span class="sig-field-label">Date :</span>
      <span class="sig-field-line"></span>
    </div>
  </div>
</div>

<div class="footer">
  <div class="footer-left">
    123 Example Street, Sample Business Park, Sample City, 0000<br>
    PO Box 000, Sample City 0000, Sample Country<br>
    Tel: +00 (00) 000-0000 | Fax: +00 (00) 000-0000 | Email: info@example.com | www.example.com<br>
    Directors: J Doe (Chairman) | A Smith (CEO) | B Jones | C Brown | D White
  </div>
  <div class="footer-divider"></div>
  <div class="footer-company-block">
    <div class="footer-company-name">ACME LOGISTICS (PTY) LTD</div>
    <div class="footer-company-reg">REG. NO. 0000/000000/00</div>
  </div>
  <span class="footer-logo-placeholder">LOGO</span>
</div>

</body>
</html>"""

            import streamlit.components.v1 as components
            components.html(delivery_note_html, height=1100, scrolling=True)
