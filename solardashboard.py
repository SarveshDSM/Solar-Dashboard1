import streamlit as st
import pandas as pd
from PIL import Image

# Page configuration
st.set_page_config(page_title="Solar Monitoring Dashboard", layout="wide")

# Tata Power Logo
logo = Image.open("tata_power_logo.jpeg")
st.image(logo, width=150)

# Title
st.title("🌞 Solar Generation Monitoring Dashboard")

# Designed by Netmetering Team (top placement)
st.markdown("<h5 style='text-align: right; color: gray;'>🔧 Designed by Netmetering Team | Tata Power</h5>", unsafe_allow_html=True)

# Solar panel image
solar_image = Image.open("solar_panel.jpeg")
st.image(solar_image, use_column_width=True)

# File uploader
uploaded_file = st.file_uploader("📤 Upload your Solar Generation Excel File", type=["xlsx"])

if uploaded_file:
    # Read and clean Excel
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # Identify month columns
    metadata_cols = ['ca no', 'Solar Capacity', 'Expected Solar Generation', 'catr', 'CONSUMER Name']
    month_cols = [col for col in df.columns if col not in metadata_cols]

    # Show available months
    st.markdown("### 📅 Available Months")
    st.write(", ".join(month_cols))

    # Month input
    entered_month = st.text_input("Enter Month for Analysis (e.g., Apr-24):")

    if entered_month:
        if entered_month not in df.columns:
            st.error(f"❌ Month '{entered_month}' not found. Please check the available months above.")
        else:
            st.success(f"Showing results for: {entered_month}")

            # Zero generation filter
            zero_gen_df = df[df[entered_month] == 0]
            st.markdown("### ⚠️ Consumers with Zero Generation")
            st.dataframe(zero_gen_df[['ca no', 'CONSUMER Name', entered_month]])

            # >50% drop filter
            drop_df = df[df[entered_month] < 0.5 * df['Expected Solar Generation']]
            st.markdown("### 📉 Consumers with >50% Drop Compared to Expected Generation")
            st.dataframe(drop_df[['ca no', 'CONSUMER Name', 'Expected Solar Generation', entered_month]])

            # Download buttons
            st.download_button("⬇️ Download Zero Generation Report", zero_gen_df.to_csv(index=False), file_name="zero_generation.csv")
            st.download_button("⬇️ Download Drop Report", drop_df.to_csv(index=False), file_name="drop_report.csv")
