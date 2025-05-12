import streamlit as st
import pandas as pd
from PIL import Image
import base64
from io import BytesIO
import plotly.express as px

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



# ---------- Upload Excel File ----------
uploaded_file = st.file_uploader("📤 Upload Solar Generation Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.dropna(axis=1, how='all')

        key_cols = ['ca no', 'Solar Capacity', 'Expected Solar Generation', 'catr', 'CONSUMER Name']
        month_cols = [col for col in df.columns if col not in key_cols]
        month_cols = sorted(month_cols, key=lambda x: pd.to_datetime(x, errors='coerce') if '-' in x else x)

        missing = [col for col in key_cols if col not in df.columns]
        if missing:
            st.error(f"Missing required columns: {missing}")
        else:
            df = df.fillna(0)
            for col in month_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            selected_month = st.selectbox("📅 Select Month for Analysis", options=month_cols)

            if selected_month:
                st.success(f"Showing results for: {selected_month}")

                # Zero Generation
                zero_gen_df = df[df[selected_month] == 0]
                st.markdown("### ⚠️ Consumers with Zero Generation")
                st.dataframe(zero_gen_df[['ca no', 'CONSUMER Name', selected_month]])

                # >50% Drop
                drop_df = df[df[selected_month] < 0.5 * df['Expected Solar Generation']]
                st.markdown("### 📉 Consumers with >50% Drop vs. Expected")
                st.dataframe(drop_df[['ca no', 'CONSUMER Name', 'Expected Solar Generation', selected_month]])

                # Downloads
                st.download_button("⬇️ Download Zero Gen Report", zero_gen_df.to_csv(index=False), file_name="zero_generation.csv")
                st.download_button("⬇️ Download Drop Report", drop_df.to_csv(index=False), file_name="drop_report.csv")

                # Bar Chart of Underperformers
                st.markdown("### 📊 Underperforming Consumers Bar Chart")
                if not drop_df.empty:
                    chart_df = drop_df[['CONSUMER Name', selected_month, 'Expected Solar Generation']]
                    chart_df['% of Expected'] = (chart_df[selected_month] / chart_df['Expected Solar Generation']) * 100
                    chart_df = chart_df.sort_values('% of Expected')
                    fig = px.bar(chart_df.head(20), x='CONSUMER Name', y='% of Expected',
                                 title="Top 20 Underperformers",
                                 labels={'% of Expected': '% Generated vs Expected'},
                                 color='% of Expected', color_continuous_scale='OrRd')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No underperformers (<50%) for the selected month.")

                # Summary Statistics
                st.markdown("### 📈 Summary Statistics")
                view_mode = st.radio("View summary by:", ["Month", "Solar Capacity Group"])

                if view_mode == "Month":
                    summary = df[month_cols].describe().transpose()
                    st.dataframe(summary)
                else:
                    bins = st.slider("Set Solar Capacity Ranges (kW)", 0, int(df['Solar Capacity'].max()) + 10, step=5)
                    df['Capacity Group'] = pd.cut(df['Solar Capacity'], bins=[0, 5, 10, 25, 50, 100, 500, 1000, 5000, 10000],
                                                  labels=["0–5", "5–10", "10–25", "25–50", "50–100", "100–500", "500–1k", "1k–5k", "5k–10k"])
                    cap_summary = df.groupby('Capacity Group')[selected_month].agg(['count', 'sum', 'mean', 'median']).reset_index()
                    st.dataframe(cap_summary)

    except Exception as e:
        st.error(f"Error processing the file: {e}")



