import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Define a function to set the page
def set_page(page):
    st.session_state.page = page

# Sidebar navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    set_page("Home")
if st.sidebar.button("About"):
    set_page("About")
if st.sidebar.button("Energy Resources"):
    set_page("Energy Resources")
if st.sidebar.button("Education Center"):
    set_page("Education Center")

# Page content based on selected page
if st.session_state.page == "Home":
    st.title("Home Page")
    data_choice = st.radio("Choose the type of data to explore:", ["State Data", "Metro Data"])

    # Load appropriate data based on the choice
    if data_choice == "State Data":
        df = pd.read_excel("Combined_State.xlsx")  # Load state data
        st.header("State Data from ACS")

        df.columns = df.columns.astype(str)

        st.header("Energy related data from ACS")
        # Extract features and years from column names (skip the 'State' column)
        columns = df.columns[1:]  # Skip the 'State' column
        features_years = {}

        # Create a dictionary of features and years
        for col in columns:
            feature, year = col.rsplit(' ', 1)
            if feature not in features_years:
                features_years[feature] = []
            features_years[feature].append(year)
        years = sorted(set(year for year_list in features_years.values() for year in year_list))
        # Create the tabs
        tab1, tab2 = st.tabs(["Data", "Chart"])

        with tab1:
            # Section for selecting filters and options (widgets are used directly in the tab)
            view_option = st.radio("Select View Option", ["View All Data", "View with Filter"])

            # Only show filter widgets if "View with Filter" is selected
            if view_option == "View with Filter":
                # Filter options
                states = df['State'].unique()
                features = list(features_years.keys())
                years = sorted(set(year for year_list in features_years.values() for year in year_list))

                # Multi-select options for state, year, and feature
                selected_states = st.multiselect("Select States", ['None'] + list(states), default=['None'])
                selected_years = st.multiselect("Select Years", ['None'] + years, default=['None'])
                selected_features = st.multiselect("Select Features", ['None'] + features, default=['None'])
            else:
                # If 'View All Data' is selected, use 'None' values to disable filtering
                selected_states = ['None']
                selected_years = ['None']
                selected_features = ['None']

            # Filter the data based on the selections
            filtered_data = df.copy()

            if view_option == "View with Filter":  # Apply filtering if "View with Filter" is selected
                # Filter by selected states
                if selected_states != ['None']:
                    filtered_data = filtered_data[filtered_data['State'].isin(selected_states)]

                # Filter by selected years and features
                if selected_years != ['None'] and selected_features != ['None']:
                    selected_columns = []
                    for feature in selected_features:
                        for year in selected_years:
                            feature_column_name = f"{feature} {year}"
                            if feature_column_name in df.columns:
                                selected_columns.append(feature_column_name)

                    if selected_columns:
                        filtered_data = filtered_data[['State'] + selected_columns]
                    else:
                        filtered_data = pd.DataFrame()  # No matching columns

                # If only years are selected, show columns for those years
                if selected_years != ['None'] and selected_features == ['None']:
                    year_columns = [col for col in df.columns if any(year in col for year in selected_years)]
                    if year_columns:
                        filtered_data = filtered_data[['State'] + year_columns]
                    else:
                        filtered_data = pd.DataFrame()  # No matching columns

                # If only features are selected, show columns for those features
                if selected_features != ['None'] and selected_years == ['None']:
                    feature_columns = [col for col in df.columns if any(feature in col for feature in selected_features)]
                    if feature_columns:
                        filtered_data = filtered_data[['State'] + feature_columns]
                    else:
                        filtered_data = pd.DataFrame()  # No matching columns

            # Display the filtered data or full data if "View All Data" is selected
            if not filtered_data.empty:
                st.write(f"### Data for your selection:")
                if selected_states != ['None']:
                    st.write(f"States: {', '.join(selected_states)}")
                if selected_years != ['None']:
                    st.write(f"Years: {', '.join(selected_years)}")
                if selected_features != ['None']:
                    st.write(f"Features: {', '.join(selected_features)}")

                # Display the filtered data
                st.write(filtered_data)
            else:
                st.write("No data available for the selected criteria.")

        with tab2:
            # Visualization Tab
            st.write("### Chart")

            # Select up to 5 states for visualization
            selected_states_for_vis = st.multiselect("Select States (up to 5)", df['State'].unique().tolist(),
                                                     default=df['State'].unique().tolist()[:5])

            # Select a feature for visualization
            selected_feature_for_vis = st.selectbox("Select Feature", list(features_years.keys()))

            # Only show the line graph if at least one state and one feature is selected
            if selected_states_for_vis and selected_feature_for_vis:
                # Filter the data for selected states and feature
                df_filtered = df[df['State'].isin(selected_states_for_vis)]

                # Prepare the data for plotting
                plot_data = pd.DataFrame()
                for state in selected_states_for_vis:
                    for year in sorted(years):
                        feature_column_name = f"{selected_feature_for_vis} {year}"
                        if feature_column_name in df.columns:
                            new_data = pd.DataFrame({
                                'State': [state],
                                'Year': [year],
                                'Value': [df.loc[df['State'] == state, feature_column_name].values[0]]
                            })
                            plot_data = pd.concat([plot_data, new_data], ignore_index=True)

                # Plot the line graph
                if not plot_data.empty:
                    fig = px.line(plot_data, x='Year', y='Value', color='State',
                                  title=f'{selected_feature_for_vis} over Years')
                    st.plotly_chart(fig)
                else:
                    st.write("No data available for the selected feature and states.")
    elif data_choice == "Metro Data":
        df = pd.read_excel("Combined_Metro.xlsx")  # Load metro data
        st.header("Metro Data from ACS")
        df.columns = df.columns.astype(str)

        st.header("Energy related data from ACS")
        # Extract features and years from column names (skip the 'State' column)
        columns = df.columns[1:]  # Skip the 'State' column
        features_years = {}

        # Create a dictionary of features and years
        for col in columns:
            feature, year = col.rsplit(' ', 1)
            if feature not in features_years:
                features_years[feature] = []
            features_years[feature].append(year)
        years = sorted(set(year for year_list in features_years.values() for year in year_list))
        # Create the tabs
        tab1, tab2 = st.tabs(["Data", "Chart"])

        with tab1:
            # Section for selecting filters and options (widgets are used directly in the tab)
            view_option = st.radio("Select View Option", ["View All Data", "View with Filter"])

            # Only show filter widgets if "View with Filter" is selected
            if view_option == "View with Filter":
                # Filter options
                states = df['Metro'].unique()
                features = list(features_years.keys())
                years = sorted(set(year for year_list in features_years.values() for year in year_list))

                # Multi-select options for state, year, and feature
                selected_states = st.multiselect("Select Metros", ['None'] + list(states), default=['None'])
                selected_years = st.multiselect("Select Years", ['None'] + years, default=['None'])
                selected_features = st.multiselect("Select Features", ['None'] + features, default=['None'])
            else:
                # If 'View All Data' is selected, use 'None' values to disable filtering
                selected_states = ['None']
                selected_years = ['None']
                selected_features = ['None']

            # Filter the data based on the selections
            filtered_data = df.copy()

            if view_option == "View with Filter":  # Apply filtering if "View with Filter" is selected
                # Filter by selected states
                if selected_states != ['None']:
                    filtered_data = filtered_data[filtered_data['Metro'].isin(selected_states)]

                # Filter by selected years and features
                if selected_years != ['None'] and selected_features != ['None']:
                    selected_columns = []
                    for feature in selected_features:
                        for year in selected_years:
                            feature_column_name = f"{feature} {year}"
                            if feature_column_name in df.columns:
                                selected_columns.append(feature_column_name)

                    if selected_columns:
                        filtered_data = filtered_data[['Metro'] + selected_columns]
                    else:
                        filtered_data = pd.DataFrame()  # No matching columns

                # If only years are selected, show columns for those years
                if selected_years != ['None'] and selected_features == ['None']:
                    year_columns = [col for col in df.columns if any(year in col for year in selected_years)]
                    if year_columns:
                        filtered_data = filtered_data[['Metro'] + year_columns]
                    else:
                        filtered_data = pd.DataFrame()  # No matching columns

                # If only features are selected, show columns for those features
                if selected_features != ['None'] and selected_years == ['None']:
                    feature_columns = [col for col in df.columns if
                                       any(feature in col for feature in selected_features)]
                    if feature_columns:
                        filtered_data = filtered_data[['Metro'] + feature_columns]
                    else:
                        filtered_data = pd.DataFrame()  # No matching columns

            # Display the filtered data or full data if "View All Data" is selected
            if not filtered_data.empty:
                st.write(f"### Data for your selection:")
                if selected_states != ['None']:
                    st.write(f"Metro: {', '.join(selected_states)}")
                if selected_years != ['None']:
                    st.write(f"Years: {', '.join(selected_years)}")
                if selected_features != ['None']:
                    st.write(f"Features: {', '.join(selected_features)}")

                # Display the filtered data
                st.write(filtered_data)
            else:
                st.write("No data available for the selected criteria.")

        with tab2:
            # Visualization Tab
            st.write("### Chart")

            # Select up to 5 states for visualization
            selected_states_for_vis = st.multiselect("Select Metros (up to 5)", df['Metro'].unique().tolist(),
                                                     default=df['Metro'].unique().tolist()[:5])

            # Select a feature for visualization
            selected_feature_for_vis = st.selectbox("Select Feature", list(features_years.keys()))

            # Only show the line graph if at least one state and one feature is selected
            if selected_states_for_vis and selected_feature_for_vis:
                # Filter the data for selected states and feature
                df_filtered = df[df['Metro'].isin(selected_states_for_vis)]

                # Prepare the data for plotting
                plot_data = pd.DataFrame()
                for state in selected_states_for_vis:
                    for year in sorted(years):
                        feature_column_name = f"{selected_feature_for_vis} {year}"
                        if feature_column_name in df.columns:
                            new_data = pd.DataFrame({
                                'Metro': [state],
                                'Year': [year],
                                'Value': [df.loc[df['Metro'] == state, feature_column_name].values[0]]
                            })
                            plot_data = pd.concat([plot_data, new_data], ignore_index=True)

                # Plot the line graph
                if not plot_data.empty:
                    fig = px.line(plot_data, x='Year', y='Value', color='Metro',
                                  title=f'{selected_feature_for_vis} over Years')
                    st.plotly_chart(fig)
                else:
                    st.write("No data available for the selected feature and states.")
elif st.session_state.page == "About":
    st.title("About")
    st.write("This website is designed to provide accessible and comprehensive energy-related data derived from the American Community Survey (ACS), along with additional resources on various energy topics. Our goal is to make critical energy information and resources easily available to both the general public and researchers. Whether you're a student, policymaker, or simply someone interested in understanding energy usage patterns, this platform offers valuable insights and data on energy consumption, sources, and trends across different regions. With a user-friendly layout and additional resources, we aim to support informed discussions and research efforts that can contribute to a more sustainable energy future.")

elif st.session_state.page == "Energy Resources":
    st.title("Energy Resources")
    st.write("This page provides information about different energy resources and their uses.")
elif st.session_state.page == "Education Center":
    st.title("Education Center")
    st.write(
        "Welcome to the Education Center! Here, you’ll find resources to help you understand different types of energy resources, energy efficiency, and sustainability practices. Our goal is to make energy-related information accessible and easy to understand.")

    # Section 1: Introduction to Energy
    st.header("Introduction to Energy")
    st.write("""
            Energy is the capacity to do work. It powers everything from our homes and vehicles to the technology we use daily. 
            There are various forms of energy, including kinetic (movement), thermal (heat), and electrical energy.
            Energy can be derived from renewable sources like solar and wind, or from non-renewable sources like fossil fuels.
        """)

    # Section 2: Types of Energy Resources
    st.header("Types of Energy Resources")

    # Subsection: Renewable Energy
    st.subheader("Renewable Energy")
    st.write("""
            Renewable energy comes from sources that are naturally replenished. Common types of renewable energy include:

            - **Solar Energy**: Harnessed from sunlight using solar panels, it’s a clean and abundant source of energy.
            - **Wind Energy**: Generated by wind turbines, it's one of the fastest-growing energy sources worldwide.
            - **Hydropower**: Produced from the movement of water in rivers and dams, it's the largest source of renewable energy.
            - **Geothermal Energy**: Derived from the Earth's internal heat, used primarily for heating and electricity generation.
            - **Biomass**: Organic material like wood, agricultural waste, or even algae is burned or processed to produce energy.
        """)

    # Subsection: Non-Renewable Energy
    st.subheader("Non-Renewable Energy")
    st.write("""
            Non-renewable energy sources are finite and will eventually deplete. They include:

            - **Fossil Fuels**: Includes coal, oil, and natural gas. These fuels release CO₂ when burned, contributing to climate change.
            - **Nuclear Energy**: Generated by splitting atoms (fission) in nuclear reactors. Although it doesn’t produce CO₂, it generates radioactive waste.
        """)




# Call the function to display the Education Center content
