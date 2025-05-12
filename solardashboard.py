import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import base64
from io import BytesIO

st.set_page_config(page_title="Solar Monitoring Dashboard", layout="wide")

# Utility: convert image to base64
def get_base64_of_image(image_path):
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Load images
logo_base64 = get_base64_of_image("tata_power_logo.jpg")
solar_image = Image.open("solar_panel.jpg")

# Header
st.markdown(f"""
<div style='text-align: center;'>
    <img src='data:image/jpeg;base64,{logo_base64}' width='150'/>
    <h2 style='margin-top: 10px;'>🌞 Solar Generation Monitoring Dashboard</h2>
    <p style='color: gray;'>🔧 Netmetering Team | Tata Power</p>
</div>
""", unsafe_allow_html=True)

# Banner
st.image(solar_image, use_column_width=True)

# Upload
uploaded_file = st.file_uploader("📤 Upload Solar Generation Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        df = df.dropna(axis=1, how='all')
        df = df.loc[:, ~df.columns.duplicated()]

        # Identify columns
        fixed_cols = ['ca no', 'Solar Capacity', 'Expected Solar Generation', 'catr', 'CONSUMER Name']
        month_cols = [col for col in df.columns if col not in fixed_cols]
        df[month_cols] = df[month_cols].apply(pd.to_numeric, errors='coerce')
        df = df.fillna(0)

        selected_month = st.selectbox("📅 Select Month for Analysis", options=sorted(month_cols, key=str))
        if selected_month:
            st.success(f"Showing results for: {selected_month}")

            # KPIs
            col1, col2, col3 = st.columns(3)
            total_generation = df[selected_month].sum()
            expected_total = df['Expected Solar Generation'].sum()
            avg_capacity = df['Solar Capacity'].mean()

            col1.metric("Total Generation (kWh)", f"{total_generation:,.0f}")
            col2.metric("Expected Generation (kWh)", f"{expected_total:,.0f}")
            col3.metric("Avg Solar Capacity (kWp)", f"{avg_capacity:,.2f}")

            # Bar chart of underperformers
            drop_df = df[df[selected_month] < 0.5 * df['Expected Solar Generation']]
            fig = px.bar(drop_df, x='CONSUMER Name', y=selected_month, color='Solar Capacity',
                         title="📉 Underperformers (<50% Expected)", labels={selected_month: 'Generation'},
                         height=400)
            fig.update_layout(xaxis_tickangle=-45)

            st.plotly_chart(fig, use_container_width=True)

            # Tables in two columns
            st.markdown("### 📊 Consumer-Level Reports")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### ⚠️ Zero Generation Consumers")
                zero_df = df[df[selected_month] == 0]
                st.dataframe(zero_df[['ca no', 'CONSUMER Name', selected_month]])
                st.download_button("⬇️ Download Zero Report", zero_df.to_csv(index=False), file_name="zero_generation.csv")

            with col2:
                st.markdown("#### 📉 >50% Drop Consumers")
                st.dataframe(drop_df[['ca no', 'CONSUMER Name', 'Expected Solar Generation', selected_month]])
                st.download_button("⬇️ Download Drop Report", drop_df.to_csv(index=False), file_name="drop_report.csv")

            # Expander for raw data
            with st.expander("🔍 Full Dataset Preview"):
                st.dataframe(df)

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")



