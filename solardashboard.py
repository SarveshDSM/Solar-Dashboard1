import streamlit as st
import pandas as pd

# Title
st.title("Solar Generation Monitoring Dashboard")

# File upload
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Extract month columns (assuming the months start after a fixed set of metadata columns)
    metadata_cols = ['ca no', 'Solar Capacity', 'Expected Solar Generation', 'catr', 'CONSUMER Name']
    month_cols = [col for col in df.columns if col not in metadata_cols]

    # Let user pick a month
    selected_month = st.selectbox("Select Month to Analyze", month_cols)

    if selected_month:
        st.subheader(f"Analysis for: {selected_month}")

        # Zero generation
        zero_gen_df = df[df[selected_month] == 0]
        st.markdown("### Consumers with Zero Generation")
        st.dataframe(zero_gen_df[['ca no', 'CONSUMER Name', selected_month]])

        # Drop > 50% compared to expected generation
        drop_df = df[df[selected_month] < 0.5 * df['Expected Solar Generation']]
        st.markdown("### Consumers with >50% Drop in Generation Compared to Expected")
        st.dataframe(drop_df[['ca no', 'CONSUMER Name', 'Expected Solar Generation', selected_month]])

        # Downloadable reports
        st.download_button("Download Zero Generation Report", zero_gen_df.to_csv(index=False), file_name="zero_generation.csv")
        st.download_button("Download Drop Report", drop_df.to_csv(index=False), file_name="drop_report.csv")
