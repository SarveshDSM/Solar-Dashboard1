import streamlit as st
import pandas as pd
from PIL import Image
import base64
from io import BytesIO

# Set Streamlit page config
st.set_page_config(page_title="Solar Monitoring Dashboard", layout="wide")

# ---------- Utility to encode image ----------
def get_base64_of_image(image_path):
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")  # JPEG format required, even for .jpg files
    return base64.b64encode(buffered.getvalue()).decode()

# ---------- Load images ----------
logo_base64 = get_base64_of_image("tata_power_logo.jpg")  # Your .jpg logo


# ---------- Centered Header ----------
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

# ---------- File Upload ----------
uploaded_file = st.file_uploader("📤 Upload Solar Generation Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()  # Remove any whitespace in column names

    # Define columns
    metadata_cols = ['ca no', 'Solar Capacity', 'Expected Solar Generation', 'catr', 'CONSUMER Name']
    month_cols = [col for col in df.columns if col not in metadata_cols]

    st.markdown("### 📅 Available Months in Uploaded File")
    st.write(", ".join([str(m) for m in month_cols]))

    # Select month
    selected_month = st.text_input("📆 Enter Month for Analysis (e.g., Apr-24):")

    if selected_month:
        if selected_month not in df.columns:
            st.error(f"❌ Month '{selected_month}' not found. Please check the available months above.")
        else:
            st.success(f"Showing data for: {selected_month}")

            # ---------- Zero Generation ----------
            zero_gen_df = df[df[selected_month] == 0]
            st.markdown("### ⚠️ Consumers with Zero Generation")
            st.dataframe(zero_gen_df[['ca no', 'CONSUMER Name', selected_month]])

            # ---------- >50% Drop ----------
            drop_df = df[df[selected_month] < 0.5 * df['Expected Solar Generation']]
            st.markdown("### 📉 Consumers with >50% Drop vs Expected Generation")
            st.dataframe(drop_df[['ca no', 'CONSUMER Name', 'Expected Solar Generation', selected_month]])

            # ---------- Download Buttons ----------
            st.download_button("⬇️ Download Zero Generation Report", zero_gen_df.to_csv(index=False), file_name="zero_generation.csv")
            st.download_button("⬇️ Download Drop Report", drop_df.to_csv(index=False), file_name="drop_report.csv")

