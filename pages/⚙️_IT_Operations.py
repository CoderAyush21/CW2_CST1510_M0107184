import streamlit as st
from app.data.db import connect_database
import plotly.express as px
import pandas as pd 
from datetime import datetime
from app.data.tickets import insert_ticket, get_all_tickets, update_ticket_status, delete_ticket
from app.services.analyticalQueries import get_avg_resolution_by_staff, get_high_priority_tickets_by_status, get_slow_resolution_tickets_by_status, get_tickets_by_priority, get_high_priority_tickets, get_slow_resolution_tickets_only
import time

from google import genai
from google.genai import types
# Use of gemini API
client_ticket= genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


st.set_page_config(
    page_title="IT Operations",
    layout="wide",
)

st.title("IT OPERATIONS DASHBOARD")

if st.session_state.get("logged_in") != True:
    st.error("Please Log in to access the IT Operations Page !")
    if st.button("Return to Home Page"):
     st.switch_page("Home.py")
    st.stop()

# Connect database
conn=connect_database()

df_ticket= get_all_tickets()

# Find total tickets
total_tickets= len(df_ticket)

high_priority= get_high_priority_tickets(conn)

# calculate % of high priority tickets of total tickets
total_high_priority= len(high_priority)
high_priority_percentage = (total_high_priority / total_tickets * 100) if total_tickets > 0 else 0

##
df_slow_resolution = get_slow_resolution_tickets_by_status(conn, min_resolution_time=24)
##

# Find slow resolution tickets only

slow_tickets= get_slow_resolution_tickets_only(conn, min_resolution_time=24)
# get slow resolution tickets total
total_slow_tickets= len(slow_tickets)


st.subheader("IT Operations Insights")
col1,col2,col3= st.columns([1,1,1])
with col1:
    st.metric(
        label="Total Tickets",
        value=f"{total_tickets}",
    ) 
    
with col2:
    st.metric(
        label="High priority tickets %",
        value=f"{high_priority_percentage:.1f}%",
    )

with col3:
    st.metric(
        label= "Slow Resolution Tickets",
        value=f"{total_slow_tickets}",
    )


    
      

col1,col2= st.columns([0.8,0.2])
with col1:

    st.subheader("Service Desk Performance: Average Resolution Time by Staff Members")
    df_resolution_times = get_avg_resolution_by_staff(conn)

    fig = px.bar(
        df_resolution_times,
        x="assigned_to",
        y="avg_resolution_time",
        color="avg_resolution_time",
        color_continuous_scale=px.colors.sequential.Plotly3_r,
        hover_data=["assigned_to", "avg_resolution_time"],  
    )

    fig.update_layout(
        xaxis_title="Staff Member", 
        yaxis_title="Average Resolution Time (hours)",
    )

    st.plotly_chart(fig, use_container_width=True)

col1,col2= st.columns([0.8,0.2])
with col1:
    st.subheader("High Priority Tickets by Status")
    df_high_priority = get_high_priority_tickets_by_status(conn)

    fig2 = px.bar(
        df_high_priority,
        x="count",
        y="status",
        orientation='h',
        color="count",
        color_continuous_scale=px.colors.sequential.Viridis,
        hover_data=["status", "count"],
    )

    fig2.update_layout(
        xaxis_title="Number of High Priority Tickets",
        yaxis_title="Ticket Status",
        yaxis=dict(autorange="reversed"), 
    )

    st.plotly_chart(fig2, use_container_width=True)



df_priority_level = get_tickets_by_priority(conn)
col1,col2= st.columns([0.5,0.5])
with col2:
    st.markdown("### Tickets Distribution by Priority Level")
    fig = px.pie(
        df_priority_level,
        names="priority",
        values="count",
        color="priority",
        color_discrete_map={
            "Low": "#00CC96",
            "Medium": "#FFA15A",
            "High": "#EF553B"
        }
    )
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}',
        textinfo='percent+label',
        marker=dict(line=dict(color='white', width=2))
    )
    st.plotly_chart(fig, use_container_width=True)

with col1:
    st.markdown("### Tickets with Slow Resolution Times by Status")


    fig = px.bar(
        df_slow_resolution,
        x="status",
        y="avg_resolution",
        color="avg_resolution",
        color_continuous_scale=px.colors.sequential.Plotly3,
        hover_data=["status", "avg_resolution"],
    )

    fig.update_layout(
        xaxis_title="Ticket Status",
        yaxis_title="Average Resolution Time (hours)",
    )
    st.plotly_chart(fig, use_container_width=True)



# Get all incident ids as list for the update form

ticket_all__ids= df_ticket['ticket_id'].tolist()

st.subheader("IT Tickets Management")
col1,col2= st.columns([0.8,0.2])
with col1:
    action_choice = st.selectbox("Select Action", ([" Add Ticket", " Update Ticket Status", "Delete Ticket","Upload CSV"]), key="action_choice_ticket")


    if action_choice == " Add Ticket":
        # Add Incidents Form
        st.markdown("### Add Ticket ###") 
        with st.form("Add new ticket"):
            priority = st.selectbox("Priority", ["Low", "Medium", "High","Critical"])
            status = st.selectbox("Status", ["Open", "Closed", "In Progress","Resolved"])
            assigned_to = st.text_input("Assigned to")
            description = st.text_input("Description")
            resolution_time= st.text_input("Resolution Hours")
            submitted = st.form_submit_button("Submit")

        if submitted:
            ticket_datetime= datetime.now()
            try :
                insert_ticket(priority,description,status, assigned_to,resolution_time,ticket_datetime)
                st.success("Ticket added")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Error adding incident: {e}")

    elif action_choice == " Update Ticket Status":
        st.markdown("### Update Ticket Status")
        with st.form("Update Ticket status"):
            incident_id = st.selectbox("Ticket ID", ticket_all__ids)
            new_status = st.selectbox("New Status", ["Open", "Closed", "In Progress","Resolved"])
            updated = st.form_submit_button("Update Status")
        if updated:
            try:
                success = update_ticket_status(incident_id, new_status)
                if success:
                    st.success("Ticket status updated")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Ticket ID not found")
            except Exception as e:
                st.error(f"Error updating status: {e}")

    elif action_choice == "Delete Ticket":
        st.markdown("### Delete Ticket")
        with st.form("Delete Ticket"):
            ticket_id= st.selectbox("Ticket ID to Delete", ticket_all__ids, key="delete_ticket_id")
            
            submitted= st.form_submit_button("Delete")

            if submitted:
                if st.checkbox("Confirm deletion of ticket"):                
                    deleted = delete_ticket(ticket_id)
                    if deleted:
                            st.success("Ticket deleted")
                            time.sleep(2)
                            st.rerun()
                    else:
                            st.error("Ticket ID not found")
                else:
                    st.warning("Please confirm deletion by checking the box.")

    elif action_choice == "Upload CSV" :
        st.markdown("### Upload CSV")
        uploaded_file= st.file_uploader("Upload CSV file", type= ["csv"])
        if uploaded_file:
          try:
            csv_df= pd.read_csv(uploaded_file)
            # Display the csv file
            st.write("CSV file contents preview")
            st.dataframe(csv_df)

            required_columns= {"ticket_id","priority","description","status","assigned_to","resolution_time_hours","created_at"}
            csv_columns= set(csv_df.columns)

            missing_column= required_columns - csv_columns
            extra_column= csv_columns - required_columns

            if missing_column:
                st.error(f"Missing required column(s) : {', '.join(missing_column)}")
                st.stop()
            if extra_column:
                st.warning(f"⚠️ Extra columns ignored: {', '.join(extra_column)}")
            
            st.success("CSV file validated")

            if st.button("Upload CSV"):
                for _, row in csv_df.iterrows():
                        insert_ticket(
                            row["priority"],
                            row["description"],
                            row["status"],
                            row["assigned_to"],
                            row["resolution_time_hours"],
                            datetime.now()
                        )
                st.success("CSV data added successfully!")
                time.sleep(2)
                st.rerun()
          except Exception as e :
              st.error("Error reading the CSV file !")
              

st.markdown("---")            

col1,col2= st.columns([0.8,0.2])
with col1:
    # AI Analyser for the Big Data
    st.subheader("🔎 AI Tickets Analyser")

    if not df_ticket.empty :
        ticket_options = [
            f"{row['ticket_id']}: {row['priority']}- {row['status']}- {row['assigned_to']}"
            for index, row in df_ticket.iterrows()
        ]

        # Let the user pick a ticket from the readable options list
        selected_id = st.selectbox(
            "Select Dataset to analyse",
            range(len(df_ticket)),
            format_func=lambda i : ticket_options[i]
        )
        

        ticket= df_ticket.iloc[selected_id]

        # Display incident details

        st.subheader("ℹ️ Ticket Details")
        st.write(f"**Priority:** {ticket['priority']}")
        st.write(f"**Status:** {ticket['status']}")
        st.write(f"**Assigned to:** {ticket['assigned_to']}")
        st.write(f"**Created at :** {ticket['created_at']}")
        st.write(f"**Description :** {ticket['description']}")
        st.write(f"**Resolution time :** {ticket['resolution_time_hours']}")


    if st.button("Analyse with AI"):
        with st.spinner("AI analysing dataset..."):
            # Create the analysis prompt
            analysis_prompt= f""" Analyse this dataset :
                                Priority : {ticket['priority']}
                                Status : {ticket['status']}
                                Description: {ticket['description']}
                                Resolution time : {ticket['resolution_time_hours']}

                                Provide :
                                1. Ticket triage & prioritisation
                                2. Troubleshooting guidance
                                3. System Optimisation tips
                                4. Infrastructure best practice """
            # Call the Gemini API
            response = client_ticket.models.generate_content_stream(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction="You are an IT operations expert."),
                contents={"role" : "user", "parts" : [{"text": analysis_prompt}]},
            )


            # Display the AI analysis from Gemini

            st.subheader("🚀 AI Analysis")
            container= st.empty()
            full_reply= ""
            for chunk in response:
                full_reply+= chunk.text
                container.markdown(full_reply)
