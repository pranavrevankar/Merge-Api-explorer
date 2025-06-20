import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any
import json

# Define API categories
API_CATEGORIES = {
    "HRIS": {
        "description": "HR, Payroll, and Directory",
        "endpoints": {}  # To be implemented
    },
    "ATS": {
        "description": "Recruiting",
        "endpoints": {}  # To be implemented
    },
    "Accounting": {
        "description": "Accounting and Finance",
        "endpoints": {}  # To be implemented
    },
    "Ticketing": {
        "description": "Welcome to the Merge Ticketing (TCKT) API explorer! Enter your Merge API key and access token of the linked account to check the response of Merge's unified API endpoints.",
        "endpoints": {
            "accounts": {
                "description": "Retrieve accounts information",
                "methods": ["GET"],
                "endpoints": [
                    "/accounts",
                    "/accounts/{id}"
                ]
            },
            "attachments": {
                "description": "Manage ticket attachments",
                "methods": ["GET", "POST"],
                "endpoints": [
                    "/attachments",
                    "/attachments/{id}",
                    "/attachments/{id}/download",
                    "/attachments/meta/post"
                ],
                "post_fields": {
                    "file_name": "string",
                    "file_url": "string",
                    "ticket": "string (UUID)",
                    "content_type": "string"
                }
            },
            "collections": {
                "description": "Manage collections of tickets",
                "methods": ["GET"],
                "endpoints": [
                    "/collections",
                    "/collections/{id}",
                    "/collections/{collection_id}/viewers"
                ]
            },
            "comments": {
                "description": "Manage ticket comments",
                "methods": ["GET", "POST"],
                "endpoints": [
                    "/comments",
                    "/comments/{id}",
                    "/comments/meta/post"
                ],
                "post_fields": {
                    "body": "string",
                    "html_body": "string",
                    "is_private": "boolean",
                    "ticket": "string (UUID)",
                    "user": "string (UUID)"
                }
            },
            "contacts": {
                "description": "Manage contacts",
                "methods": ["GET", "POST"],
                "endpoints": [
                    "/contacts",
                    "/contacts/{id}",
                    "/contacts/meta/post"
                ],
                "post_fields": {
                    "name": "string",
                    "email_address": "string",
                    "phone_number": "string",
                    "details": "string"
                }
            },
            "roles": {
                "description": "Manage user roles",
                "methods": ["GET"],
                "endpoints": [
                    "/roles",
                    "/roles/{id}"
                ]
            },
            "tags": {
                "description": "Manage tags",
                "methods": ["GET"],
                "endpoints": [
                    "/tags",
                    "/tags/{id}"
                ]
            },
            "teams": {
                "description": "Manage teams",
                "methods": ["GET"],
                "endpoints": [
                    "/teams",
                    "/teams/{id}"
                ]
            },
            "tickets": {
                "description": "Manage tickets",
                "methods": ["GET", "POST", "PATCH"],
                "endpoints": [
                    "/tickets",
                    "/tickets/{id}",
                    "/tickets/{ticket_id}/viewers",
                    "/tickets/meta/patch/{id}",
                    "/tickets/meta/post",
                    "/tickets/remote-field-classes"
                ],
                "post_fields": {
                    "name": "string (Required for most integrations)",
                    "description": "string (Required for Zendesk)",
                    "status": "enum (OPEN, CLOSED, IN_PROGRESS, ON_HOLD)",
                    "priority": "enum (URGENT, HIGH, NORMAL, LOW)",
                    "due_date": "string (ISO 8601 date)",
                    "assignees": "array of UUIDs",
                    "collections": "array of UUIDs (Required for Teamwork, Trello, Wrike, Zoho)",
                    "ticket_type": "string",
                    "account": "UUID",
                    "contact": "UUID (Required for Zoho Desk)",
                    "creator": "UUID",
                    "parent_ticket": "UUID",
                    "remote_id": "string",
                    "remote_created_at": "string (ISO 8601 date)",
                    "remote_updated_at": "string (ISO 8601 date)",
                    "ticket_url": "string",
                    "tags": "array of strings",
                    "integration_params": {
                        "counter_party_email": "string (Required for SpotDraft)",
                        "counter_party_first_name": "string (Required for SpotDraft)",
                        "counter_party_last_name": "string (Required for SpotDraft)",
                        "template_remote_id": "string (Required for SpotDraft)",
                        "department_id": "string (Required for Zoho Desk)"
                    },
                    "remote_fields": {
                        "remote_field_class": "string (Required for all integrations)",
                        "value": "string (Required for most integrations)"
                    }
                }
            },
            "users": {
                "description": "Manage users",
                "methods": ["GET"],
                "endpoints": [
                    "/users",
                    "/users/{id}"
                ]
            }
        }
    },
    "CRM": {
        "description": "Customer Relationship Management",
        "endpoints": {}  # To be implemented
    },
    "File Storage": {
        "description": "File Storage and Management",
        "endpoints": {}  # To be implemented
    }
}

# Define API documentation for common models
API_DOCUMENTATION = {
    "accounts": {
        "title": "API Documentation",
        "parameters": [
            {
                "name": "created_after",
                "type": "DateTime (ISO 8601)",
                "required": "Optional",
                "description": "If provided, will only return objects created after this datetime."
            },
            {
                "name": "created_before",
                "type": "DateTime (ISO 8601)",
                "required": "Optional",
                "description": "If provided, will only return objects created before this datetime."
            },
            {
                "name": "cursor",
                "type": "String",
                "required": "Optional",
                "description": "The pagination cursor value."
            },
            {
                "name": "include_deleted_data",
                "type": "Boolean",
                "required": "Optional",
                "description": "Indicates whether or not this object has been deleted in the third party platform. Full coverage deletion detection is a premium add-on. Native deletion detection is offered for free with limited coverage."
            },
            {
                "name": "include_remote_data",
                "type": "Boolean",
                "required": "Optional",
                "description": "Whether to include the original data Merge fetched from the third-party to produce these models."
            },
            {
                "name": "include_shell_data",
                "type": "Boolean",
                "required": "Optional",
                "description": "Whether to include shell records. Shell records are empty records (they may contain some metadata but all other fields are null)."
            },
            {
                "name": "modified_after",
                "type": "DateTime (ISO 8601)",
                "required": "Optional",
                "description": "If provided, only objects synced by Merge after this date time will be returned."
            },
            {
                "name": "modified_before",
                "type": "DateTime (ISO 8601)",
                "required": "Optional",
                "description": "If provided, only objects synced by Merge before this date time will be returned."
            },
            {
                "name": "page_size",
                "type": "Integer",
                "required": "Optional",
                "description": "Number of results to return per page."
            },
            {
                "name": "remote_id",
                "type": "String",
                "required": "Optional",
                "description": "The API provider's ID for the given object."
            }
        ]
    }
}

# Add the same documentation to all other common models
for model in ["attachments", "collections", "comments", "contacts", "roles", "tags", "teams", "tickets", "users"]:
    API_DOCUMENTATION[model] = API_DOCUMENTATION["accounts"].copy()

def get_query_parameters(endpoint_name: str) -> Dict:
    """Generate a form for query parameters."""
    if endpoint_name not in API_DOCUMENTATION:
        return {}
        
    query_params = {}
    st.subheader("Query Parameters")
    
    # Add a checkbox to enable query parameters
    if st.checkbox("Add Query Parameters", key=f"{endpoint_name}_enable_params"):
        doc = API_DOCUMENTATION[endpoint_name]
        
        for param in doc["parameters"]:
            param_name = param["name"]
            param_type = param["type"]
            
            # Create appropriate input based on parameter type
            if "DateTime" in param_type:
                query_params[param_name] = st.date_input(
                    param_name.replace("_", " ").title(),
                    help=param["description"]
                )
            elif param_type == "Boolean":
                query_params[param_name] = st.checkbox(
                    param_name.replace("_", " ").title(),
                    help=param["description"]
                )
            elif param_type == "Integer":
                query_params[param_name] = st.number_input(
                    param_name.replace("_", " ").title(),
                    min_value=1,
                    help=param["description"]
                )
            else:  # String or other types
                query_params[param_name] = st.text_input(
                    param_name.replace("_", " ").title(),
                    help=param["description"]
                )
    
    return query_params

def fetch_endpoint_data(endpoint: str, access_token: str, api_key: str, method: str = "GET", data: Dict = None, query_params: Dict = None) -> Dict:
    """Fetch data from a specific endpoint."""
    base_url = "https://api.merge.dev/api/ticketing/v1"
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "X-Account-Token": access_token.strip(),
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            # Add query parameters to the request
            if query_params:
                # Convert datetime objects to ISO format
                processed_params = {}
                for key, value in query_params.items():
                    if hasattr(value, 'isoformat'):  # Check if it's a datetime object
                        processed_params[key] = value.isoformat()
                    else:
                        processed_params[key] = value
                response = requests.get(url, headers=headers, params=processed_params)
            else:
                response = requests.get(url, headers=headers)
        else:  # POST
            # Format the data according to Merge API requirements
            formatted_data = {}
            if data:
                # Remove empty values
                data = {k: v for k, v in data.items() if v is not None and v != ""}
                # Remove fields that are empty lists
                data = {k: v for k, v in data.items() if not (isinstance(v, list) and len(v) == 0)}
                # For tickets endpoint, wrap the data in a model object
                if "tickets" in endpoint:
                    # Ensure 'collections' and other array fields are always lists
                    array_fields = [
                        "collections", "assignees", "tags"
                    ]
                    for field in array_fields:
                        if field in data and not isinstance(data[field], list):
                            data[field] = [data[field]]
                    formatted_data = {"model": data}
                else:
                    formatted_data = data
            # Debug print
            st.write("Outgoing POST payload:", formatted_data)
            
            response = requests.post(url, headers=headers, json=formatted_data)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            st.write("Error Response:", e.response.text)
        return None

def display_endpoint_data(endpoint: str, access_token: str, api_key: str, method: str = "GET", data: Dict = None, query_params: Dict = None):
    """Display data for a specific endpoint."""
    data = fetch_endpoint_data(endpoint, access_token, api_key, method, data, query_params)
    
    if data:
        # Display raw JSON
        st.subheader("Raw JSON Response")
        st.json(data)
        
        # If there are results, display as table
        if "results" in data:
            st.subheader("Results Table")
            df = pd.DataFrame(data["results"])
            st.dataframe(df)
            
            # Display count
            st.metric("Total Records", len(data["results"]))

            # Add a graph for the Ticketing page (tickets endpoint)
            if endpoint == "/tickets":
                # Try to find a date field
                date_field = None
                for possible_field in ["created_at", "created", "createdAt", "createdat"]:
                    if possible_field in df.columns:
                        date_field = possible_field
                        break
                if date_field:
                    st.subheader("Tickets Over Time")
                    # Convert to datetime
                    df[date_field] = pd.to_datetime(df[date_field], errors='coerce')
                    # Drop rows with NaT
                    df = df.dropna(subset=[date_field])
                    # Group by date (day)
                    df["date_only"] = df[date_field].dt.date
                    tickets_by_date = df.groupby("date_only").size().reset_index(name="count")
                    st.line_chart(data=tickets_by_date.set_index("date_only"))
                else:
                    st.info("No date field found to plot the graph.")

def get_post_form(endpoint_name: str, endpoint_info: Dict) -> Dict:
    """Generate a form for POST request data."""
    if "post_fields" not in endpoint_info:
        return None
        
    form_data = {}
    st.subheader("POST Request Data")
    
    # Add integration selector for tickets
    if endpoint_name == "tickets":
        integration = st.selectbox(
            "Select Integration",
            ["Teamwork", "Trello", "Wrike", "Zendesk", "Zoho Desk", "Zoho BugTracker", "SpotDraft"],
            help="Select the integration you're using"
        )
        st.write(f"Required fields for {integration} will be marked with *")
    
    for field, field_type in endpoint_info["post_fields"].items():
        if field == "integration_params" or field == "remote_fields":
            continue  # Handle these separately
            
        if field_type == "boolean":
            form_data[field] = st.checkbox(field.replace("_", " ").title())
        elif field_type == "array of UUIDs" or field_type == "array of strings":
            input_text = st.text_area(
                field.replace("_", " ").title(),
                help="Enter UUIDs or values separated by commas"
            )
            # Split, strip, and filter out empty strings
            form_data[field] = [x.strip() for x in input_text.split(",") if x.strip()] if input_text else []
        elif "UUID" in field_type:
            form_data[field] = st.text_input(
                field.replace("_", " ").title(),
                help=f"Enter a valid UUID for {field}"
            )
        elif "enum" in field_type:
            options = field_type.split("(")[1].split(")")[0].split(", ")
            form_data[field] = st.selectbox(
                field.replace("_", " ").title(),
                options,
                help=f"Select {field.replace('_', ' ')}"
            )
        else:
            form_data[field] = st.text_input(
                field.replace("_", " ").title(),
                help=f"Enter {field_type} value"
            )
    
    # Handle integration-specific fields
    if endpoint_name == "tickets":
        st.subheader("Integration Parameters")
        integration_params = {}
        for param, param_type in endpoint_info["post_fields"]["integration_params"].items():
            integration_params[param] = st.text_input(
                param.replace("_", " ").title(),
                help=f"Enter {param_type}"
            )
        if any(integration_params.values()):
            form_data["integration_params"] = integration_params
        
        st.subheader("Remote Fields")
        remote_fields = {}
        for field, field_type in endpoint_info["post_fields"]["remote_fields"].items():
            remote_fields[field] = st.text_input(
                field.replace("_", " ").title(),
                help=f"Enter {field_type}"
            )
        if any(remote_fields.values()):
            form_data["remote_fields"] = remote_fields
    
    return form_data

def display_api_documentation(endpoint_name: str):
    """Display API documentation in a formatted way."""
    if endpoint_name in API_DOCUMENTATION:
        doc = API_DOCUMENTATION[endpoint_name]
        st.subheader(doc["title"])
        
        # Create a table for the parameters
        params_data = []
        for param in doc["parameters"]:
            params_data.append({
                "Parameter": param["name"],
                "Type": param["type"],
                "Required": param["required"],
                "Description": param["description"]
            })
        
        st.table(pd.DataFrame(params_data))

def main():
    st.title("Merge API Explorer")
    
    # Initialize session state for authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Sidebar for category selection - simplified design
    st.sidebar.header("API Categories")
    selected_category = st.sidebar.selectbox(
        "Select Category",
        list(API_CATEGORIES.keys())
    )
    
    # Main content area
    st.header(f"{selected_category} API")
    st.write(API_CATEGORIES[selected_category]["description"])
    
    # Authentication inputs
    col1, col2 = st.columns(2)
    with col1:
        api_key = st.text_input(
            "API Key",
            type="password",
            key="api_key"
        )
    with col2:
        access_token = st.text_input(
            "Access Token",
            type="password",
            key="access_token"
        )
    
    # Add submit button
    if st.button("Submit"):
        if api_key and access_token:
            st.session_state.authenticated = True
        else:
            st.error("Please enter both API Key and Access Token")
    
    if not st.session_state.authenticated:
        st.info("Please enter your API Key and Access Token, then click Submit to explore the API endpoints")
        return
    
    # Display endpoints for selected category
    if selected_category in API_CATEGORIES and API_CATEGORIES[selected_category]["endpoints"]:
        st.subheader("Available Common Models")
        
        # Create tabs for each endpoint type
        endpoint_types = list(API_CATEGORIES[selected_category]["endpoints"].keys())
        tabs = st.tabs(endpoint_types)
        
        for tab, endpoint_name in zip(tabs, endpoint_types):
            with tab:
                endpoint_info = API_CATEGORIES[selected_category]["endpoints"][endpoint_name]
                st.write(endpoint_info["description"])
                
                # Display available methods
                st.write("Available Methods:", ", ".join(endpoint_info["methods"]))
                
                # Create a selectbox for available endpoints
                selected_endpoint = st.selectbox(
                    f"Select {endpoint_name.title()} Endpoint",
                    endpoint_info["endpoints"],
                    key=f"{endpoint_name}_endpoint"
                )
                
                # Method selection
                method = st.radio(
                    "Select Method",
                    endpoint_info["methods"],
                    key=f"{endpoint_name}_method"
                )
                
                # Get query parameters if method is GET
                query_params = None
                if method == "GET":
                    query_params = get_query_parameters(endpoint_name)
                
                # Get POST data if method is POST
                post_data = None
                if method == "POST":
                    post_data = get_post_form(endpoint_name, endpoint_info)
                
                if st.button(f"{method} {selected_endpoint}", key=f"{endpoint_name}_fetch"):
                    with st.spinner(f"Processing {method} request to {selected_endpoint}..."):
                        display_endpoint_data(selected_endpoint, access_token, api_key, method, post_data, query_params)
    else:
        st.info(f"Endpoints for {selected_category} are coming soon!")

if __name__ == "__main__":
    main()

