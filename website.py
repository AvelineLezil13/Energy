import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load the data
df = pd.read_excel("Combined_State.xlsx")
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
tab1, tab2 = st.tabs(["Data", "Visualizations"])

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
    st.write("### Visualizations")

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
            fig = px.line(plot_data, x='Year', y='Value', color='State', title=f'{selected_feature_for_vis} over Years')
            st.plotly_chart(fig)
        else:
            st.write("No data available for the selected feature and states.")
