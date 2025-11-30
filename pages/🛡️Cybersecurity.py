import streamlit as st
import pandas as pd
from app.data.incidents import get_all_incidents, insert_incident, update_incident_status, delete_incident
import plotly.express as px
from datetime import datetime
from app.data.db import connect_database
from app.services.analyticalQueries import  get_high_severity_by_status, get_incident_types_with_many_cases

conn = connect_database()

st.set_page_config(
    page_title="Cybersecurity",
    layout="wide",
)

st.title("CYBERSECURITY INTELLIGENCE DASHBOARD")


if st.session_state.get("logged_in") != True:
    st.error("Please Log in")
    st.stop()



df_incidents = get_all_incidents()



# Convert the timestamp column to datetime objects
df_incidents['timestamp'] = pd.to_datetime(df_incidents['timestamp'], errors='coerce')


# T0 display Phishing Incidents from the table in first half of the web page
st.subheader("Phishing Incidents Analysis")

df_phishing = df_incidents[
    df_incidents['category'].str.contains('Phishing', case=False, na=False)
]

phishing_trend = (
    df_phishing
    .set_index('timestamp') # Use 'timestamp' for the index
    .resample('W')['category'] # Resample by Week ('W') and count
    .count()
    .rename('Incidents Count')
)
 # To display metric for the incidents
current_total_incidents = len(df_incidents)
total_phishing = len(df_phishing)
current_phishing_percentage = (total_phishing / current_total_incidents * 100) if current_total_incidents > 0 else 0
 # Initialize previous values in session state if not present
if "previous_total_incidents" not in st.session_state:
    st.session_state.previous_total_incidents = current_total_incidents
if "previous_phishing_percentage" not in st.session_state:
    st.session_state.previous_phishing_percentage = current_phishing_percentage

# Calculate deltas using current and previous values
total_incidents_delta = current_total_incidents - st.session_state.previous_total_incidents
phishing_percent_delta = current_phishing_percentage - st.session_state.previous_phishing_percentage
phishing_percent_delta_str = f"{phishing_percent_delta:.1f}%"

# Display the final layout
col1,col2= st.columns([0.6,0.4])
with col1:
    st.line_chart(phishing_trend)

with col2:
    st.metric(
        label="Total Incidents",
        value=f"{current_total_incidents:,}",
        delta=total_incidents_delta, 
        delta_color="normal" 
    ) 
    
    st.metric(
        label="Phishing % of Total",
        value=f"{current_phishing_percentage:.1f}%",
        delta=phishing_percent_delta_str,
        delta_color="inverse" 
    )
 # Save current values for next comparison
st.session_state.previous_total_incidents = current_total_incidents
st.session_state.previous_phishing_percentage = current_phishing_percentage

status_counts = df_incidents["status"].value_counts().reset_index()
status_counts.columns = ["status", "count"]

col1,col2= st.columns([0.6,0.4])
# Display Cyber Incidents Status using Bar Chart
with col1:
   st.markdown("### Cyber Incidents Status Distribution")
   st.bar_chart(status_counts.set_index("status"))
   


with col2:


    # Display Cyber Incidents Status Summary In Pie Chart 
    # assign resolved and active statuses
    resolved_statuses = ['Closed', 'Resolved']
    active_statuses = ['Open', 'In Progress']
    # calculate counts for pie chart
    resolved_count = status_counts[status_counts['status'].isin(resolved_statuses)]['count'].sum()
    active_count = status_counts[status_counts['status'].isin(active_statuses)]['count'].sum()

    df_pie = pd.DataFrame({
    'Category': ['Resolved/Closed', 'Active/Open'],
    'Count': [resolved_count, active_count]
        })
    st.markdown("### Cyber Incidents Status Summary")   

    fig = px.pie(
                df_pie, 
                values='Count', 
                names='Category', 
                color_discrete_sequence=['#4c7ad3', '#ff8c42'],
                hole = 0.45 
            )
    
    fig.update_layout(
        width=325,
        height=325,
        margin=dict(t=30)
    )
    fig.update_traces(
        textinfo='percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}',
        marker=dict(line=dict(color='white', width=2))
    )

    st.plotly_chart(fig, use_container_width=True)




df_many_cases = get_incident_types_with_many_cases(conn, min_count=5)
col1,col2= st.columns([0.9,0.1])
with col1:
    st.markdown("### Top Incident Categories by Volume")
    if not df_many_cases.empty:
            # Use of Plotly Express to create horizontal bar chart
            fig_bar = px.bar(
                df_many_cases, 
                x='count',         
                y='category',      
                orientation='h',   # Makes it a horizontal bar chart
                color='count',     # Color the bars based on the count magnitude
                color_continuous_scale=px.colors.sequential.Plotly3,
                height=400
            )
            

            fig_bar.update_layout(
                xaxis_title="Number of Cases",
                yaxis_title="Incident Category",
                yaxis={'categoryorder':'total ascending'} # Ensures categories are ordered top-to-bottom
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
            st.info(f"No incident types found with more than minimum number of cases.")




    
# Get all incident ids as list for the update form
all_incident_ids= df_incidents['incident_id'].tolist()

col1,col2,col3= st.columns(3)
with col1:

    # Add Incidents Form
    st.markdown("### Add Cyber Incidents ###")
    with st.form("Add new incident"):
        severity = st.selectbox("Severity", ["Low", "Medium", "High","Critical"])
        category = st.selectbox("Incident Type", ["Malware", "Phishing", "DDoS","Unauthorized Access","Misconfiguration"])
        status = st.selectbox("Status", ["Open", "Closed", "In Progress","Resolved"])
        reported_by = st.text_input("Reported By")
        description = st.text_input("Description")
        submitted = st.form_submit_button("Submit")

    if submitted:
        incident_datetime= datetime.now()
        try :
            insert_incident(severity,category,status,description,reported_by,incident_datetime)
            st.success("Incident added")
            st.rerun()
        except Exception as e:
            st.error(f"Error adding incident: {e}")
with col2:
    st.markdown("### Update Incident Status")
    with st.form("Update incident status"):
        incident_id = st.selectbox("Incident ID", all_incident_ids)
        new_status = st.selectbox("New Status", ["Open", "Closed", "In Progress","Resolved"])
        updated = st.form_submit_button("Update Status")
    if updated:
        try:
            success = update_incident_status(incident_id, new_status)
            if success:
                st.success("Incident status updated")
                st.rerun()
            else:
                st.error("Incident ID not found")
        except Exception as e:
            st.error(f"Error updating incident: {e}")
with col3:
    st.markdown("### Delete Cyber Incident")
    with st.form("Delete incident"):
        incident_id= st.selectbox("Incident ID to Delete", all_incident_ids, key="delete_incident_id")
        
        submitted= st.form_submit_button("Delete Incident")

        if submitted:
            if st.checkbox("Confirm deletion of incident #{incident_id}?"):                
                deleted = delete_incident(incident_id)
                if deleted:
                        st.success("Incident deleted")
                        st.rerun()
                else:
                        st.error("Incident ID not found")
            else:
                st.warning("Please confirm deletion by checking the box.")


df_high_sev_status = get_high_severity_by_status(conn)

# Display Cyber Incidents Bar Chart by Severity
col1,col2= st.columns([0.6,0.4])
with col1:
    st.markdown("### High Severity Incidents by Status")

    
    fig = px.bar(
        df_high_sev_status,
        x="status",
        y="count",
        text="count",
        color="status",
        color_discrete_sequence=["#0078FF", "#00C4B4", "#2E86DE"],  # neon aqua shades
    )

    fig.update_traces(
        textposition="outside",
        marker=dict(
            line=dict(width=1.2, color="#003F88"),  # neon outline
        )
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",  
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0078FF"),  
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(title="Status"),
        yaxis=dict(title="Count"),
        bargap=0.25,
    )

    st.plotly_chart(fig, use_container_width=True)