import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Any

# MCP API base URL
MCP_BASE_URL = "https://api.merge.dev/api/ticketing/v1"

# MCP endpoints and their display names/icons
MCP_TOOLS = [
    {"name": "Tickets", "endpoint": "/tickets", "icon": "🎫"},
    {"name": "Comments", "endpoint": "/comments", "icon": "💬"},
    {"name": "Attachments", "endpoint": "/attachments", "icon": "📎"},
    {"name": "Collections", "endpoint": "/collections", "icon": "🗂️"},
    {"name": "Users", "endpoint": "/users", "icon": "👤"},
    {"name": "Teams", "endpoint": "/teams", "icon": "👥"},
    {"name": "Roles", "endpoint": "/roles", "icon": "🛡️"},
    {"name": "Tags", "endpoint": "/tags", "icon": "🏷️"},
]

# Helper: API call
def mcp_api_call(endpoint: str, api_key: str, account_token: str, method: str = "GET", data: Dict = None) -> Any:
    url = f"{MCP_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "X-Account-Token": account_token.strip(),
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data)
        else:
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            st.write("Error Response:", e.response.text)
        return None

# Helper: Render a table with optional chart for tickets
def render_table_and_chart(name, data):
    if not data or "results" not in data:
        st.info(f"No {name} found.")
        return
    df = pd.DataFrame(data["results"])
    st.dataframe(df)
    st.metric(f"Total {name}", len(df))
    # For tickets, show a chart by created date
    if name == "Tickets" and not df.empty:
        date_field = None
        for f in ["created_at", "created", "createdAt"]:
            if f in df.columns:
                date_field = f
                break
        if date_field:
            df[date_field] = pd.to_datetime(df[date_field], errors='coerce')
            df = df.dropna(subset=[date_field])
            df["date_only"] = df[date_field].dt.date
            chart = df.groupby("date_only").size().reset_index(name="count")
            st.subheader("Tickets Over Time")
            st.bar_chart(chart.set_index("date_only"))

# Helper: Render a simple POST form for each tool
def render_post_form(tool, api_key, account_token):
    st.subheader(f"Create a new {tool['name']}")
    with st.form(f"create_{tool['name']}"):
        if tool["name"] == "Tickets":
            name = st.text_input("Name", "My Ticket")
            status = st.selectbox("Status", ["OPEN", "CLOSED", "IN_PROGRESS", "ON_HOLD"])
            priority = st.selectbox("Priority", ["URGENT", "HIGH", "NORMAL", "LOW"])
            collections = st.text_area("Collections (comma-separated UUIDs)")
            submit = st.form_submit_button("Create Ticket")
            if submit:
                payload = {
                    "model": {
                        "name": name,
                        "status": status,
                        "priority": priority,
                        "collections": [x.strip() for x in collections.split(",") if x.strip()] if collections else []
                    }
                }
                result = mcp_api_call(tool["endpoint"], api_key, account_token, method="POST", data=payload)
                st.success(f"Created! Response: {result}")
        elif tool["name"] == "Comments":
            body = st.text_area("Comment Body")
            ticket = st.text_input("Ticket UUID")
            submit = st.form_submit_button("Create Comment")
            if submit:
                payload = {"model": {"body": body, "ticket": ticket}}
                result = mcp_api_call(tool["endpoint"], api_key, account_token, method="POST", data=payload)
                st.success(f"Created! Response: {result}")
        elif tool["name"] == "Attachments":
            file_name = st.text_input("File Name")
            file_url = st.text_input("File URL")
            ticket = st.text_input("Ticket UUID")
            content_type = st.text_input("Content Type")
            submit = st.form_submit_button("Create Attachment")
            if submit:
                payload = {"model": {"file_name": file_name, "file_url": file_url, "ticket": ticket, "content_type": content_type}}
                result = mcp_api_call(tool["endpoint"], api_key, account_token, method="POST", data=payload)
                st.success(f"Created! Response: {result}")
        else:
            st.info("POST not implemented for this tool in the demo.")

# --- Streamlit App ---
st.set_page_config(page_title="Merge MCP Explorer", page_icon="🧩", layout="wide")
st.title("🧩 Merge MCP Explorer")
st.caption("A fun, interactive dashboard for Merge MCP APIs. Explore, create, and visualize!")

# Sidebar for credentials
st.sidebar.header("🔑 API Credentials")
api_key = st.sidebar.text_input("API Key", type="password")
account_token = st.sidebar.text_input("Account Token", type="password")

if not api_key or not account_token:
    st.warning("Please enter your API Key and Account Token in the sidebar.")
    st.stop()

# Tabs for each MCP tool
tabs = st.tabs([f"{tool['icon']} {tool['name']}" for tool in MCP_TOOLS])

for tab, tool in zip(tabs, MCP_TOOLS):
    with tab:
        st.header(f"{tool['icon']} {tool['name']}")
        # GET and show data
        data = mcp_api_call(tool["endpoint"], api_key, account_token)
        render_table_and_chart(tool["name"], data)
        # POST form for some tools
        if tool["name"] in ["Tickets", "Comments", "Attachments"]:
            render_post_form(tool, api_key, account_token)
        st.markdown("---")
        st.caption(f"Powered by Merge MCP | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # st.balloons()  # Surprise! (Removed as requested) 