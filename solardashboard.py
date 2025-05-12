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
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# ---------- Load logo and banner images ----------
logo_base64 = get_base64_of_image("tata_power_logo.jpg")
solar_image = Image.open("solar_panel.jpg")

# ---------- Header ----------
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
    try:
        # Read Excel with proper header
        df = pd.read_excel(uploaded_file)

        # Clean column names
        df.columns = df.columns.astype(str).str.strip()

        # Remove duplicate or empty columns
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.dropna(axis=1, how='all')

        # Expected columns
        key_cols = ['ca no', 'Solar Capacity', 'Expected Solar Generation', 'catr', 'CONSUMER Name']
        month_cols = [col for col in df.columns if col not in key_cols]

        # Sort month columns (just in case)
        month_cols = sorted(month_cols, key=lambda x: pd.to_datetime(x, errors='coerce') if '-' in x else x)

        # Check all required columns
        missing = [col for col in key_cols if col not in df.columns]
        if missing:
            st.error(f"Missing required columns: {missing}")
        else:
            # Fill NaN with 0
            df = df.fillna(0)

            # Ensure month columns are numeric
            for col in month_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # --- Select Month ---
            selected_month = st.selectbox("📅 Select Month for Analysis", options=month_cols)

            if selected_month:
                st.success(f"Showing results for: {selected_month}")

                # --- Zero Generation ---
                zero_gen_df = df[df[selected_month] == 0]
                zero_gen_count = len(zero_gen_df)

                # --- >50% Drop ---
                drop_df = df[df[selected_month] < 0.5 * df['Expected Solar Generation']]
                drop_df = drop_df[drop_df[selected_month] != 0]  # Exclude zero generation cases
                drop_count = len(drop_df)

                # Show summary above the tables
                st.markdown(f"### Summary for {selected_month}")
                st.write(f"Total Zero Generation Cases: {zero_gen_count}")
                st.write(f"Total >50% Drop Cases (excluding zero cases): {drop_count}")

                # Use columns layout for side-by-side views
                col1, col2 = st.columns(2)

                # --- Zero Generation ---
                with col1:
                    st.markdown("### ⚠️ Consumers with Zero Generation")
                    st.dataframe(zero_gen_df[['ca no', 'CONSUMER Name', selected_month]])

                    # Download Button
                    st.download_button("⬇️ Download Zero Generation Report", zero_gen_df.to_csv(index=False), file_name="zero_generation.csv")

                # --- >50% Drop ---
                with col2:
                    st.markdown("### 📉 Consumers with >50% Drop Compared to Expected Generation")
                    st.dataframe(drop_df[['ca no', 'CONSUMER Name', 'Expected Solar Generation', selected_month]])

                    # Download Button
                    st.download_button("⬇️ Download Drop Report", drop_df.to_csv(index=False), file_name="drop_report.csv")

    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")






