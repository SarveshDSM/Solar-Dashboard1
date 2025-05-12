import streamlit as st
import pandas as pd
from PIL import Image
import base64
from io import BytesIO

# Set Streamlit page config
st.set_page_config(page_title="Solar Monitoring Dashboard", layout="wide")

# ---------- Utility: Image to base64 ----------
def get_base64_of_image(image_path):
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")  # Use JPEG format even if it's .jpg
    return base64.b64encode(buffered.getvalue()).decode()

# ---------- Load logo and banner images ----------
logo_base64 = get_base64_of_image("tata_power_logo.jpg")   # Your .jpg logo
solar_image = Image.open("solar_panel.jpg")                # Your .jpg solar panel image

# ---------- Centered Header with Logo and Title ----------
st.markdown(
    f"""
    <div style='text-align: center;'>
        <img src='data:image/jpeg;base64,{logo_base64}' width='200'/>
        <h1 style='margin-top: 10px;'>🌞 Solar Generation Monitoring Dashboard</h1>
        <h5 style='color: gray;'>🔧 Designed by Netmetering Team | Tata Power</h5>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Banner Image ----------
st.image(solar_image, use_column_width=True)

# ---------- Upload Excel File ----------
uploaded_file = st.file_uploader("📤 Upload Solar Generation Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Read Excel
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()  # Remove whitespace from column names

    # Remove duplicate columns if any
    df = df.loc[:, ~df.columns.duplicated()]

    # Identify month columns
    metadata_cols = ['ca no', 'Solar Capacity', 'Expected Solar Generation', 'catr', 'CONSUMER Name']
    month_cols = [col for col in df.columns if col not in metadata_cols]

    # Dropdown to select a month
    selected_month = st.selectbox("📅 Select Month for Analysis", options=sorted(month_cols, key=str))

    # Filter and Display Results
    if selected_month:
        st.success(f"Showing results for: {selected_month}")

        # --- Zero Generation ---
        zero_gen_df = df[df[selected_month] == 0]
        st.markdown("### ⚠️ Consumers with Zero Generation")
        st.dataframe(zero_gen_df[['ca no', 'CONSUMER Name', selected_month]])

        # --- >50% Drop ---
        drop_df = df[df[selected_month] < 0.5 * df['Expected Solar Generation']]
        st.markdown("### 📉 Consumers with >50% Drop Compared to Expected Generation")
        st.dataframe(drop_df[['ca no', 'CONSUMER Name', 'Expected Solar Generation', selected_month]])

        # --- Download Buttons ---
        st.download_button("⬇️ Download Zero Generation Report", zero_gen_df.to_csv(index=False), file_name="zero_generation.csv")
        st.download_button("⬇️ Download Drop Report", drop_df.to_csv(index=False), file_name="drop_report.csv")

