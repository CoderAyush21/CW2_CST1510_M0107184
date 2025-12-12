import streamlit as st
import sys
import os
import time



ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)



from app.advanced_services.database_manager import DatabaseManager
from app.advanced_services.auth_manager import AuthManager  


db = DatabaseManager("DATA/intelligence_platform.db")
db.connect()
auth = AuthManager(db)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if "show_login" not in st.session_state:
    st.session_state.show_login = False

if "show_register" not in st.session_state:
    st.session_state.show_register = False



if not st.session_state.logged_in:
    
    st.markdown(
            """
          <h1 style="text-align:center; 
                    font-size:43px; 
                    font-weight:bold; 
                    color:#1E90FF; 
                    margin-top:5px;">
                Multi-Domain Intelligence Platform
           </h1>
           <p style="text-align:center; 
              font-size:22px; 
              font-family:'Segoe UI', 'Helvetica Neue', sans-serif; 
              font-weight:bold; 
              background: linear-gradient(90deg, #00C9FF, #92FE9D); 
              -webkit-background-clip: text; 
              -webkit-text-fill-color: transparent; 
              margin-top:10px; 
              text-shadow: 1px 1px 2px rgba(0,0,0,0.15);
              opacity : 0.95;">
        Unlock insights across multiple domains with ease
            </p>

            """,
            unsafe_allow_html=True
        )



    st.markdown(
            """
            <div style="width:100%; text-align:center; margin-top:px;">
                <h1 style="color:#1E90FF; font-size: 38px; opacity : 0.95; text-align:center;">Access Your Dashboards</h1>
            </div>
            """,
            unsafe_allow_html=True
        )


    # Button for login/registration
      
    col1,col2,col3= st.columns([3.8,2,4])
        
    with col2:
                login_btn = st.button("Login", key="login_button", use_container_width=True)
                register_btn = st.button("Register", key="register_button", use_container_width=True)

                if login_btn:
                    st.session_state.show_login = True
                    st.session_state.show_register = False

                if register_btn:
                    st.session_state.show_register = True
                    st.session_state.show_login = False


    left,middle,right= st.columns([1,13,1])
    if st.session_state.show_login and not st.session_state.logged_in:
           with middle: 
            st.subheader("User Login")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
        
            if st.button("Login", key="login_submit"):
                sucess, msg= auth.login_user(username, password)
                if sucess: 
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(msg)
                    st.session_state.show_login = False
                    st.rerun()
                else:
                    st.error(msg)

    
    

    if st.session_state.show_register and not st.session_state.logged_in:
           with middle: 
            st.subheader("User Register")
            new_user = st.text_input("New Username", key="reg_user")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            user_role = st.selectbox("Select Role", options=["user", "admin","analyst"], key="reg_role")
        
            if st.button("Register", key="reg_submit"):
                sucess, msg= auth.register_user(new_user, new_pass, user_role)
                if sucess: 
                    st.success(msg)
                    st.session_state.show_register = False
                else:
                    st.error(msg)
elif st.session_state.logged_in: 
    time.sleep(1)
    st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        margin-top: 10px;
    ">
        <h1 style="
            font-size: 45px;
            font-weight: 700;
            color: #1E90FF;
            margin-bottom: 10px;
        ">
            Welcome, {st.session_state.username}
        </h1>
        <p style="
            font-size: 20px;
            color: #87CEEB;
            font_weight : bold;
            line-height: 1.5;
        ">
            You are now logged in. Select a dashboard from the sidebar to explore one of the below listed domains.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
  
    
    # Use columns to present the domains side-by-side
    col1,col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💻 IT Operations")
        st.info("Monitor performance and application stability to ensure maximum service reliability.")
        

        
    with col2:
        st.markdown("### 🧠 Data Science")
        st.success("Govern data resource consumption and ensure the accuracy and quality of production models.")


    with col3:
        st.markdown("### 🛡️ Cybersecurity")
        st.warning("Monitor the active threat landscape and analyze security team response bottlenecks.")
        




      
if st.session_state.logged_in:
    st.sidebar.title(f"Welcome, {st.session_state.username} 👋")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.show_login = False
        st.session_state.show_register = False
        st.rerun()  




            

