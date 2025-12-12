import streamlit as st
from app.services.analyticalQueries import get_large_datasets, get_datasets_by_uploader, get_dataset_upload_trends_monthly
import plotly.express as px
import pandas as pd
from datetime import datetime
import time

from google import genai
from google.genai import types
# Use of gemini API
client_dataset= genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


from app.advanced_services.database_manager import DatabaseManager
from models.dataset_class import Dataset



st.set_page_config(
    page_title="Data Science",
    layout="wide",
)

st.title("DATA SCIENCE ANALYTICS DASHBOARD")

if st.session_state.get("logged_in") != True:
    st.error("Please Log in to access the DataScience Page !")

    if st.button("Return to Home Page"):
     st.switch_page("Home.py")
    st.stop()


db = DatabaseManager("DATA/intelligence_platform.db")
db.connect()

def load_datasets() -> list[Dataset]:
    rows = db.fetch_all(
        "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata"
    )
    datasets_list = []
    for row in rows:
        dataset = Dataset(
            dataset_id=row[0],
            name=row[1],
            rows=row[2],
            columns=row[3],
            uploaded_by=row[4],
            upload_date=row[5] if row[5] else datetime.now()
        )
        datasets_list.append(dataset)
    return datasets_list


datasets = load_datasets()

df_datasets = pd.DataFrame([{
    "dataset_id": d.get_id(),
    "name": d.get_name(),
    "rows": d.get_rows(),
    "columns": d.get_columns(),
    "uploaded_by": d.get_uploaded_by(),
    "upload_date": d.get_upload_date()
} for d in datasets])


total_datasets= len(df_datasets)

# get all large datasets
df_large_datasets = get_large_datasets(db, min_rows=1000)
large_datasets= len(df_large_datasets)

# Insights for datasets
st.subheader("Datasets Insights")
left,middle,right = st.columns([1,1,1])
with left:
    st.metric(
        label="Total Datasets",
        value=f"{total_datasets:,}", 
    ) 
with middle:
    st.metric(
        label="Total large datasets",
        value=f"{large_datasets:,}",
    ) 




col1,col2= st.columns([0.9,0.1])
with col1:
    st.markdown("### Datasets Resource Consumption Analysis")


    fig = px.bar (
        df_large_datasets,    
        x= "rows",
        y="name",
        orientation='h',
        color="rows",
        color_continuous_scale=px.colors.sequential.Plotly3,
        hover_data=["uploaded_by", "columns"],
        text="rows"
        )

    fig.update_layout(
        xaxis_title="Number of Rows",
        yaxis_title="Dataset Name",
        yaxis=dict(autorange="reversed"), # Reverse y-axis to have largest on top
        height=600
    )

    st.plotly_chart(fig, width="stretch")

df_datasets_by_uploader= get_datasets_by_uploader(db)
df_dataset_upload_trends= get_dataset_upload_trends_monthly(db)
col1,col2= st.columns([0.5,0.5])
with col1:
    st.markdown("### Datasets Uploads by Users")


    fig2= px.bar(
        df_datasets_by_uploader,
        x="uploaded_by",
        y="dataset_count",
        color="dataset_count",
        color_continuous_scale=px.colors.sequential.Plotly3,
        text="dataset_count"
    )

    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("### Datasets Upload Trend Over Time")

    fig3= px.line(
        
    df_dataset_upload_trends,
    x="month",          
    y="upload_count",   
    markers=True,
)

    st.plotly_chart(fig3, width="stretch")



# Get all datsets ids as list for the update form
all_datasets_ids= df_datasets['dataset_id'].tolist()

st.subheader("Manage Datasets")
col1,col2= st.columns([0.8,0.2])
with col1:
    action_choice = st.selectbox("Select Action", ([" Add Dataset", " Update Dataset Name", "Delete Dataset","Upload CSV"]), key="ds_action_choice")

    if action_choice == " Add Dataset":
        # Add Dataset Form
        st.markdown("### Add Dataset ###")
        with st.form("Add new Dataset"):
            name= st.text_input("Dataset Name")
            rows= st.number_input("Number of Rows", min_value=0, step=1)
            columns= st.number_input("Number of Columns", min_value=0, step=1)
            uploaded_by= st.text_input("Uploaded By")
            submitted= st.form_submit_button("Add Dataset")
        if submitted:
            dataset_added_datetime= datetime.now().date()
            try :
                new_dataset = Dataset(
                    dataset_id=None,
                    name=name,
                    rows=rows,
                    columns=columns,
                    uploaded_by=uploaded_by,
                    upload_date=dataset_added_datetime
                )
                new_dataset.insert_dataset(db)
                st.success("Dataset added")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Error adding dataset: {e}")


    elif action_choice == " Update Dataset Name":
        st.markdown("### Update Dataset Name")
        with st.form("Update Dataset name"):
            dataset_id = st.selectbox("Dataset ID", all_datasets_ids)
            new_name = st.text_input("New Dataset Name")
            updated = st.form_submit_button("Update Name")

        if updated:
            try:
                dataset_to_update = Dataset.load_by_id(db, dataset_id)
                if dataset_to_update:
                    dataset_to_update.update_name(db, new_name)
                    st.success("Dataset Name updated")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Dataset ID not found")
            except Exception as e:
                st.error(f"Error updating dataset name: {e}")
                

    elif action_choice == "Delete Dataset":
        st.markdown("### Delete Dataset")
        with st.form("Delete incident"):
            dataset_id= st.selectbox("Dataset ID to Delete", all_datasets_ids, key="delete_dataset_id")
            
            submitted= st.form_submit_button("Delete Dataset")

            if submitted:
                if st.checkbox("Confirm deletion of dataset"):                
                    dataset_to_delete = Dataset.load_by_id(db, dataset_id)
                    if dataset_to_delete:
                            dataset_to_delete.delete(db)
                            st.success("Dataset deleted")
                            time.sleep(2)
                            st.rerun()
                    else:
                            st.error("Dataset ID not found")
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

            required_columns= {"dataset_id","name,rows","columns","uploaded_by","upload_date"}
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
                        dataset = Dataset(
                            dataset_id=None,
                            name=row["name"],
                            rows=row["rows"],
                            columns=row["columns"],
                            uploaded_by=row["uploaded_by"],
                            upload_date=row.get("upload_date", datetime.now())
                        )
                        dataset.insert_dataset(db)
                        
                st.success("CSV data added successfully!")
                time.sleep(2)
                st.rerun()
          except Exception as e :
              st.error("Error reading the CSV file !")


st.markdown("---")
col1,col2= st.columns([0.8,0.2])
with col1:
    # AI Analyser for the Big Data
    st.subheader("🔎 AI Datasets Analyser")

    if not df_datasets.empty :
        dataset_options = [
            f"{row['dataset_id']}: {row['name']}"
            for index, row in df_datasets.iterrows()
        ]

        # Let the user pick a dataset from the readable options list
        selected_id = st.selectbox(
            "Select Dataset to analyse",
            range(len(df_datasets)),
            format_func=lambda i : dataset_options[i]
        )
        

        dataset= df_datasets.iloc[selected_id]

        # Display incident details

        st.subheader("ℹ️ Dataset Details")
        st.write(f"**Name:** {dataset['name']}")
        st.write(f"**Rows:** {dataset['rows']}")
        st.write(f"**Columns:** {dataset['columns']}")
        st.write(f"**Uploaded by :** {dataset['uploaded_by']}")


    if st.button("Analyse with AI"):
        with st.spinner("AI analysing dataset..."):
            # Create the analysis prompt
            analysis_prompt= f""" Analyse this dataset :
                                Name : {dataset['name']}
                                Rows : {dataset['rows']}
                                Columns : {dataset['columns']}
                                Uploaded by : {dataset['uploaded_by']}

                                Provide :
                                1. Dataset analysis and insights
                                2. Visualisation recommendations
                                3. Statistical method guidance
                                4. ML model suggestions """
            # Call the Gemini API
            response = client_dataset.models.generate_content_stream(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction="You are a data science expert."),
                contents={"role" : "user", "parts" : [{"text": analysis_prompt}]},
            )


            # Display the AI analysis from Gemini

            st.subheader("🚀 AI Analysis")
            container= st.empty()
            full_reply= ""
            for chunk in response:
                full_reply+= chunk.text
                container.markdown(full_reply)


if st.session_state.get("logged_in", False):
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.show_login = False
        st.session_state.show_register = False
        st.rerun()