# import streamlit as st
# import pandas as pd
# import gspread

# st.set_page_config(page_title="Ticket Search Dashboard", layout="centered")

# @st.cache_data(ttl=60)
# def load_data():
#     """Load and preprocess the data dynamically from Google Sheets using Service Account."""
#     try:
#         # Secure Authentication Logic
#         # 1. Check if we are running on Streamlit Cloud (using secrets)
#         if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
#             # Convert AttrDict to a standard dict
#             creds_dict = dict(st.secrets["gcp_service_account"])
#             gc = gspread.service_account_from_dict(creds_dict)
#         else:
#             # 2. Fallback to local file if running locally
#             import os
#             if os.path.exists('service_account.json'):
#                 gc = gspread.service_account(filename='../service_account.json')
#             else:
#                 st.error("Authentication Error: Google Sheets credentials not found.")
#                 st.info("☁️ **If deploying on Streamlit Cloud:** You need to add your credentials to Streamlit Secrets. (Settings -> Secrets).")
#                 st.info("💻 **If running locally:** Ensure 'service_account.json' exists in the project root folder.")
#                 return pd.DataFrame()
        
#         # Open the Google Sheet by its ID (extracted from your link)
#         sheet_id = os.getenv("CS_SHEET_ID")
#         spreadsheet = gc.open_by_key(sheet_id)
        
#         # Fetch the specific sheet named 'Dump'
#         sheet = spreadsheet.worksheet("Dump")
        
#         # Convert sheet records to a Pandas DataFrame
#         data = sheet.get_all_records()
#         df = pd.DataFrame(data)

#         # Standardize formatting for searching (handle float conversion artifacts)
#         df['Ticket Id'] = df['Ticket Id'].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('nan', '', case=False).str.strip()
#         df['Registration Number'] = df['Registration Number'].astype(str).str.replace('nan', '', case=False).str.strip().str.upper()
#         return df
#     except Exception as e:
#         st.error(f"Error loading data from Google Sheets: {e}")
#         st.info("💡 Hint: Open your service_account.json, find the 'client_email', and share the Google Sheet with that email address!")
#         return pd.DataFrame()

# def main():
#     st.title("🎫 Ticket Search Dashboard")
#     st.markdown("Search for ticket details using **Ticket ID** or both **Ticket ID & Registration Number**.")

#     df = load_data()
    
#     if df.empty:
#         return

#     # User Inputs
#     with st.form("search_form"):
#         st.subheader("Search Parameters")
#         ticket_id = st.text_input("Ticket ID (Required)", placeholder="e.g., 256, 332")
#         reg_number = st.text_input("Registration Number (Optional)", placeholder="e.g., DL1LAH0922")
        
#         submitted = st.form_submit_button("Search Tickets")

#     # Defined columns for output mapping
#     display_columns = {
#         'Status (Ticket)': 'Ticket Status',
#         'Customer Name': 'Customer Name',
#         'Phone (Ticket)': 'Phone Number',
#         'Created Time (Ticket)': 'Ticket Created Time',
#         # 'Last Customer Connect Date': 'Last Customer Connect Date',
#         'Due Date': 'Due Date',
#         'Type of Escalation': 'Type of Escalation',
#         'Registration Number': 'Registration Number',
#         'Store Name': 'Store Name',
#         'Vehicle Delivery Date': 'Vehicle Delivery Date'
#     }

#     if submitted:
#         search_ticket_id = ticket_id.strip()
#         search_reg_number = reg_number.strip().upper()

#         # Validate logic: Only Ticket ID, or Both Ticket ID and Registration Number
#         if not search_ticket_id:
#             st.warning("⚠️ Ticket ID is required to perform a search.")
#         else:
#             # Filter the dataframe
#             filtered_df = df.copy()
            
#             # Apply conditions
#             if search_reg_number:
#                 # Search by BOTH
#                 filtered_df = filtered_df[
#                     (filtered_df['Ticket Id'] == search_ticket_id) & 
#                     (filtered_df['Registration Number'] == search_reg_number)
#                 ]
#             else:
#                 # Search by ONLY Ticket ID
#                 filtered_df = filtered_df[filtered_df['Ticket Id'] == search_ticket_id]

#             # Output results
#             if filtered_df.empty:
#                 st.error("❌ No tickets found matching the provided criteria.")
#             else:
#                 st.success(f"✅ Found {len(filtered_df)} matching record(s)!")
                
#                 # Filter down to the required columns
#                 result_df = filtered_df[list(display_columns.keys())].rename(columns=display_columns)
                
#                 # Display Results
#                 st.markdown("### Search Results")
                
#                 # Loop through and display each matched record clearly
#                 for idx, row in result_df.iterrows():
#                     with st.container(border=True):
#                         col1, col2 = st.columns(2)
#                         with col1:
#                             st.markdown(f"**🏷️ Registration Number:** {row['Registration Number']}")
#                             st.markdown(f"**🏷️ Ticket Status:** {row['Ticket Status']}")
#                             st.markdown(f"**👤 Customer Name:** {row['Customer Name']}")
#                             st.markdown(f"**📞 Phone Number:** {row['Phone Number']}")
#                             st.markdown(f"**📞 Vehicle Delivery Date:** {row['Vehicle Delivery Date']}")

#                         with col2:
#                             st.markdown(f"**🕒 Ticket Created Time:** {row['Ticket Created Time']}")
#                             st.markdown(f"**📅 Due Date:** {row['Due Date']}")
#                             st.markdown(f"** Type of Escalation:** {row['Type of Escalation']}")
#                             st.markdown(f"** Store Name:** {row['Store Name']}")

# if __name__ == "__main__":
#     main()


import os
import streamlit as st
import pandas as pd
import gspread
from dotenv import load_dotenv

# Load centralized .env from project root
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(_ROOT, '.env'))

# Page config is handled by hub app.py
st.markdown("""
<style>
/* Center the main container */
.block-container {
    max-width: 800px !important;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    """Load and preprocess the data dynamically from Google Sheets using Service Account."""
    try:
        # Secure Authentication Logic
        # 1. Check if we are running on Streamlit Cloud (using secrets)
        has_secrets = False
        try:
            if "gcp_service_account" in st.secrets:
                has_secrets = True
        except FileNotFoundError:
            pass # No secrets file locally, which is completely fine
            
        if has_secrets:
            gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        else:
            # 2. Fallback to local file if running locally
            _sa = os.path.join(_ROOT, 'service_account.json')
            if not os.path.exists(_sa):
                st.error("Authentication Error: Google Sheets credentials not found in st.secrets or service_account.json")
                return pd.DataFrame()
            gc = gspread.service_account(filename=_sa)
        
        # Open the Google Sheet by its ID from centralized .env
        sheet_id = ""
        try:
            if "CS_SHEET_ID" in st.secrets:
                sheet_id = st.secrets["CS_SHEET_ID"]
        except Exception:
            pass
        if not sheet_id:
            sheet_id = os.getenv("CS_SHEET_ID")
            
        if not sheet_id:
            st.error("Authentication Error: CS_SHEET_ID not found in environment variables or secrets.")
            return pd.DataFrame()
        spreadsheet = gc.open_by_key(sheet_id)
        
        # Fetch the specific sheet named 'Dump'
        sheet = spreadsheet.worksheet("Dump")
        
        # Convert sheet records to a Pandas DataFrame
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Standardize formatting for searching (handle float conversion artifacts)
        df['Ticket Id'] = df['Ticket Id'].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('nan', '', case=False).str.strip()
        df['Registration Number'] = df['Registration Number'].astype(str).str.replace('nan', '', case=False).str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        st.info("💡 If this issue persists, please contact your admin to verify the Google Sheets connection.")
        return pd.DataFrame()

def main():
    st.title("Ticket Search Dashboard")
    st.markdown("Search for ticket details using **Ticket ID**, **Registration Number**, or **both**.")

    df = load_data()
    
    if df.empty:
        return

    # User Inputs
    with st.form("search_form"):
        st.subheader("Search Parameters")
        ticket_id = st.text_input("Ticket ID", placeholder="e.g., 256, 332")
        reg_number = st.text_input("Registration Number", placeholder="e.g., DL1LAH0922")
        
        submitted = st.form_submit_button("Search Tickets")

    # Defined columns for output mapping
    # display_columns = {
    #     'Status (Ticket)': 'Ticket Status',
    #     'Customer Name': 'Customer Name',
    #     'Phone (Ticket)': 'Phone Number',
    #     'Created Time (Ticket)': 'Ticket Created Time',
    #     'Last Customer Connect Date': 'Last Customer Connect Date',
    #     'Due Date': 'Due Date'
    # }
    display_columns = {
        'Ticket Id': 'Ticket ID',
        'Status (Ticket)': 'Ticket Status',
        'Customer Name': 'Customer Name',
        'Phone (Ticket)': 'Phone Number',
        'Created Time (Ticket)': 'Ticket Created Time',
        # 'Last Customer Connect Date': 'Last Customer Connect Date',
        'Due Date': 'Due Date',
        'Revised Due Date': 'Revised Due Date',
        'Type of Escalation': 'Type of Escalation',
        'Registration Number': 'Registration Number',
        'Store Name': 'Store Name',
        'Vehicle Delivery Date': 'Vehicle Delivery Date'
    }

    if submitted:
        search_ticket_id = ticket_id.strip()
        search_reg_number = reg_number.strip().upper()

        # Validate logic: Ticket ID only, Registration Number only, or Both
        if not search_ticket_id and not search_reg_number:
            st.warning("⚠️ Please enter either Ticket ID or Registration Number to perform a search.")
        else:
            # Filter the dataframe
            filtered_df = df.copy()
            
            # Apply conditions
            if search_ticket_id and search_reg_number:
                # Search by BOTH
                filtered_df = filtered_df[
                    (filtered_df['Ticket Id'] == search_ticket_id) & 
                    (filtered_df['Registration Number'] == search_reg_number)
                ]
            elif search_ticket_id:
                # Search by ONLY Ticket ID
                filtered_df = filtered_df[filtered_df['Ticket Id'] == search_ticket_id]
            elif search_reg_number:
                # Search by ONLY Registration Number
                filtered_df = filtered_df[filtered_df['Registration Number'] == search_reg_number]

            # Output results
            if filtered_df.empty:
                st.error("❌ No tickets found matching the provided criteria.")
            else:
                st.success(f"✅ Found {len(filtered_df)} matching record(s)!")
                
                # Filter down to the required columns
                result_df = filtered_df[list(display_columns.keys())].rename(columns=display_columns)
                
                # Display Results
                st.markdown("### Search Results")
                
                # Add some spacing
                st.markdown("---")
                
                # Display tickets in a grid layout for better visual organization
                if len(result_df) == 1:
                    # Single ticket - display full width
                    row = result_df.iloc[0]
                    with st.container(border=True):
                        st.markdown(f"**🎫 Ticket ID: {row['Ticket ID']}**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**🏷️ Registration Number:** {row['Registration Number']}")
                            st.markdown(f"**🏷️ Ticket Status:** {row['Ticket Status']}")
                            st.markdown(f"**👤 Customer Name:** {row['Customer Name']}")
                            st.markdown(f"**📞 Phone Number:** {row['Phone Number']}")
                            st.markdown(f"**📅 Vehicle Delivery Date:** {row['Vehicle Delivery Date']}")

                        with col2:
                            st.markdown(f"**🕒 Ticket Created Time:** {row['Ticket Created Time']}")
                            st.markdown(f"**📅 Due Date:** {row['Due Date']}")
                            st.markdown(f"**📅 Revised Due Date:** {row['Revised Due Date']}")
                            st.markdown(f"**⚡ Type of Escalation:** {row['Type of Escalation']}")
                            st.markdown(f"**🏬 Store Name:** {row['Store Name']}")
                else:
                    # Multiple tickets - display in expanders for better UI
                    st.info(f"🎫 Found **{len(result_df)}** tickets matching your search")
                    st.markdown("---")
                    
                    for i, row in result_df.iterrows():
                        with st.expander(f"🎫 **Ticket ID:**  {row['Ticket ID']}", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**🏷️ Registration Number:** {row['Registration Number']}")
                                st.markdown(f"**🏷️ Ticket Status:** {row['Ticket Status']}")
                                st.markdown(f"**👤 Customer Name:** {row['Customer Name']}")
                                st.markdown(f"**📞 Phone Number:** {row['Phone Number']}")
                                st.markdown(f"**📅 Vehicle Delivery Date:** {row['Vehicle Delivery Date']}")

                            with col2:
                                st.markdown(f"**� Ticket Created Time:** {row['Ticket Created Time']}")
                                st.markdown(f"**📅 Due Date:** {row['Due Date']}")
                                st.markdown(f"**📅 Revised Due Date:** {row['Revised Due Date']}")
                                st.markdown(f"**⚡ Type of Escalation:** {row['Type of Escalation']}")
                                st.markdown(f"**🏬 Store Name:** {row['Store Name']}")
                        
                        st.markdown("")

if __name__ == "__main__":
    main()