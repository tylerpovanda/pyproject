import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import datetime
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

st.set_page_config(
        page_title="Grid Topology Dashboard",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded")

alt.themes.enable("quartz")

# Info for Authentication
names = ["Third Eye"]
usernames = ["thirdeye"]

# Load Passwords
file_path = Path(__file__).parent / "hashed_pw.pk1"
with file_path.open("rb") as file:
   hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
                                    "Grid Topology Dashboard", "abcdef",
                                    cookie_expiry_days=0)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
        st.error("Username or Password is incorrect")

if authentication_status == None:
    st.warning("Please enter your Username and Passowrd")

if authentication_status:
    # Load data
    df = pd.read_csv('data/generated-data.csv')
    list_of_states = pd.read_csv('data/list_of_states.csv')
    all_df = df.copy()

    # Choropleth map
    def make_choropleth(input_df, input_id, input_column):
        choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                                color_discrete_map={0:'white', 1:'red'},
                                scope="usa",
                                labels={'status':'Status'}
                                )
        choropleth.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=350
        )
        return choropleth
    
    def make_lineplot(input_df):
        selected_state = st.selectbox('Select State', list_of_states)
        st.markdown('#### Grid Status over time for ' +  selected_state)
        line_df = input_df.copy()
        line_df = line_df[line_df.state == selected_state].sort_values(by="state", ascending=False)
        line_plot = px.line(line_df, x="date", y="status", title='Status over time')
        return line_plot

    # Sidebar
    with st.sidebar:
        authenticator.logout("Logout", "sidebar")
        st.title('Grid Topology Dashboard')

        # Filtering Data - first choose date
        selected_date = st.date_input(
            "Filter by Date",
            value=datetime.date(2023, 12, 25),
            min_value=datetime.date(2023, 12, 24),
            max_value=datetime.date(2024, 1, 2)
        ).strftime('%Y-%m-%d')

        df_filtered_sorted = df[df.date == selected_date].sort_values(by="state", ascending=False)
        selected_status = st.selectbox('Filter by Status', {"ONLINE", "OFFLINE"}, None)

        # Filter on Status
        if(selected_status == "ONLINE" or selected_status == "OFFLINE"):
            df_filtered_sorted = df_filtered_sorted[df_filtered_sorted.status == selected_status].sort_values(by="state", ascending=False)
            selected_type = st.selectbox('Filter by Type', {"A", "B"}, None)

            # Filter on Type
            if(selected_type == "A" or selected_type == "B"):
                df_filtered_sorted = df_filtered_sorted[df_filtered_sorted.type == selected_type].sort_values(by="state", ascending=False)
                selected_hub = st.selectbox('Filter by Hub', {"Yes", "No"}, None)

                # Filter on Hub
                if(selected_hub == "Yes" or selected_hub == "No"):
                    df_filtered_sorted = df_filtered_sorted[df_filtered_sorted.hub == selected_hub].sort_values(by="state", ascending=False)
                    df = df_filtered_sorted
                else:
                    df = df_filtered_sorted
            else:
                df = df_filtered_sorted
        else:
            df = df_filtered_sorted

    # Main Content
    col1, col2 = st.columns([0.7, 0.3])

    # Column 1 will hold charts
    with col1:
        st.markdown('#### Grid Status across the United States')
        choropleth = make_choropleth(df, 'state-abbreviation', 'status')
        st.plotly_chart(choropleth, use_container_width=True)

        # Sub-columns will hold two pie charts
        col1b, col2b = st.columns([0.5, 0.5])
        with col1b:
            yes_count = 0
            no_count = 0
            for i in df.hub:
                if(i == 'Yes'):
                    yes_count += 1
                elif(i == 'No'):
                    no_count += 1

            hub_fig = px.pie(values=[yes_count, no_count], names=['Yes', 'No'])
            st.plotly_chart(hub_fig, use_container_width=True)

        with col2b:
            a_count = 0
            b_count = 0
            for i in df.type:
                if(i == 'A'):
                    a_count += 1
                elif(i == 'B'):
                    b_count += 1
                    
            type_fig = px.pie(values=[a_count, b_count], names=['A', 'B'])
            st.plotly_chart(type_fig, use_container_width=True)
        
        # Line Plot for each State
        st.markdown("""---""")
        lineplot = make_lineplot(all_df)
        st.plotly_chart(lineplot, use_container_width=True)

    # Column 2 will hold data table
    with col2:
        st.dataframe(df,
                    column_order=("state", "event-id", "status", "type", "hub"),
                    hide_index=True,
                    width=None,
                    height=770,
                    column_config={
                    "state": st.column_config.TextColumn(
                        "State",
                    ),
                    "event-id": st.column_config.TextColumn(
                        "ID",
                    ),
                    "status": st.column_config.TextColumn(
                        "Status",
                    ),
                    "type": st.column_config.TextColumn(
                        "Type",
                    ),
                    "hub": st.column_config.TextColumn(
                        "Hub",
                    )
                    }
                    )
                    