import os
import pandas as pd
import streamlit as st
import time
from datetime import datetime
import plotly.express as px
from fpdf import FPDF
from playsound import playsound
from streamlit_autorefresh import st_autorefresh

# ==== Page Config ====
st.set_page_config(page_title="PhysioLive Dashboard", layout="wide")
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='margin-top: -0.9em; margin-bottom: -0.4em; font-size: 3em;'>PhysioLive Dashboard</h1>
        <h4 style='margin-top: 0.0em; color: #555;'>Real-Time Monitoring of <strong>PhysioBand</strong></h4>
    </div>
""", unsafe_allow_html=True)

# ==== File & Config ====
CSV_FILE = "../data/live_data.csv"
ALERT_LOG = "../data/alert_log.csv"
ALERT_SOUND = "alert.mp3"
LOGO_FILE = "../assets/logo.png"

HEADERS = ['timestamp', 'aX', 'aY', 'aZ', 'gX', 'gY', 'gZ']

# ==== Settings ====
refresh_rate = 1.0  # seconds
show_table = True

# 🔄 Auto-refresh
st_autorefresh(interval=int(refresh_rate * 10000), key="datarefresh")

# ==== Initialize Alert Log ====
if not os.path.exists(ALERT_LOG):
    pd.DataFrame(columns=["timestamp", "channel", "value"]).to_csv(ALERT_LOG, index=False)

# ==== Load Live Data ====
@st.cache_data(ttl=5.0)
def load_data():
    try:
        df = pd.read_csv(CSV_FILE)
        df.columns = HEADERS
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.tail(200)
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return pd.DataFrame()

# ==== Log Threshold Alerts ====
def log_alert(channel, value):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_df = pd.DataFrame([[now, channel, value]], columns=["timestamp", "channel", "value"])
    alert_df.to_csv(ALERT_LOG, mode='a', header=False, index=False)

# ==== Plot Helper ====
def color_line_plot(df, column, threshold, title, yaxis_label):
    color = "green" if df[column].iloc[-1] < threshold else "red"
    fig = px.line(df, x="timestamp", y=column, title=title, markers=True)
    fig.update_traces(line_color=color)
    fig.update_layout(yaxis_title=yaxis_label, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ==== PDF Report ====
def generate_pdf_report(df, accel_thresholds, gyro_thresholds, patient_name, patient_age):
    pdf = FPDF()
    pdf.add_page()

    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=8, y=7, w=45)

    pdf.set_xy(40, 10)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(172, 15.5, txt="PhysioLive Session Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Patient Name: {patient_name}", ln=True)
    pdf.cell(200, 10, txt=f"Patient Age: {patient_age}", ln=True)
    pdf.cell(200, 10, txt=f"Session Time: {df['timestamp'].min()} to {df['timestamp'].max()}", ln=True)
    pdf.cell(200, 10, txt=f"Total Records: {len(df)}", ln=True)
    pdf.ln(5)

    for col in ['aX', 'aY', 'aZ', 'gX', 'gY', 'gZ']:
        avg = df[col].mean()
        maxv = df[col].max()
        threshold = accel_thresholds[col] if col.startswith('a') else gyro_thresholds[col]
        pdf.cell(200, 10, txt=f"{col.upper()} - Avg: {avg:.2f} | Max: {maxv:.2f} | Threshold: {threshold}", ln=True)

    if os.path.exists(ALERT_LOG):
        alert_df = pd.read_csv(ALERT_LOG)
        pdf.ln(5)
        pdf.cell(200, 10, txt=f"Alerts Logged: {len(alert_df)}", ln=True)

    report_file = "mpu_session_report.pdf"
    pdf.output(report_file)
    return report_file

# ==== MAIN ====
with st.spinner("Refreshing live data..."):
    df = load_data()

if df.empty:
    st.warning("No data available yet.")
else:
    col1, col2 = st.columns(2)
    accel_thresholds = {}
    gyro_thresholds = {}

    with col1:
        st.markdown("""
        <div style='font-size: 24px; font-weight: 600; margin-bottom: 4px;'>📈 Accelerometer</div>
        <hr style='border-top: 2px solid #444; margin-top: 0px; margin-bottom: 12px;'>
        """, unsafe_allow_html=True)

        for i, axis in enumerate(['aX', 'aY', 'aZ']):
            axis_label = f"{axis[-1]}-axis"
            threshold = st.slider(f"{axis_label} Threshold", min_value=-9.0, max_value=9.0, value=4.5, step=0.1, key=f"th_{axis}")
            accel_thresholds[axis] = threshold

            current = df[axis].iloc[-1]
            color_line_plot(df, axis, threshold, f"{axis_label} Analysis", "m/s²")

            if current > threshold:
                log_alert(axis, current)
                try:
                    playsound(ALERT_SOUND, block=False)
                except:
                    pass

            st.markdown(f"<h5>{axis_label} Readings: {current:.2f} {'>' if current > threshold else '<'} {threshold} {'❌' if current > threshold else '✅'}</h5>", unsafe_allow_html=True)
            if i < 2:
                st.markdown("<hr style='border-top: 1px solid #ddd;'>", unsafe_allow_html=True)

    st.markdown("<hr style='border-top: 2px solid #aaa;'>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='font-size: 24px; font-weight: 600; margin-bottom: 4px;'>📉 Gyroscope</div>
        <hr style='border-top: 2px solid #444; margin-top: 0px; margin-bottom: 12px;'>
        """, unsafe_allow_html=True)

        for i, axis in enumerate(['gX', 'gY', 'gZ']):
            axis_label = f"{axis[-1]}-axis"
            threshold = st.slider(f"{axis_label} Threshold", min_value=-300, max_value=300, value=100, step=5, key=f"th_{axis}")
            gyro_thresholds[axis] = threshold

            current = df[axis].iloc[-1]
            color_line_plot(df, axis, threshold, f"{axis_label} Analysis", "°/s")

            if current > threshold:
                log_alert(axis, current)
                try:
                    playsound(ALERT_SOUND, block=False)
                except:
                    pass

            st.markdown(f"<h5>{axis_label} Readings: {current:.2f} {'>' if current > threshold else '<'} {threshold} {'❌' if current > threshold else '✅'}</h5>", unsafe_allow_html=True)
            if i < 2:
                st.markdown("<hr style='border-top: 1px solid #ddd;'>", unsafe_allow_html=True)

    if show_table:
        st.markdown("---")
        st.subheader("📋 Recent Sensor Readings")
        st.dataframe(df.tail(10), use_container_width=True)

    st.markdown("---")
    st.subheader("📄 Download Session Report")

    with st.expander("Generate Report"):
        with st.form("patient_form"):
            patient_name = st.text_input("Patient Name")
            patient_age = st.number_input("Patient Age", min_value=0, max_value=120, step=1)
            submitted = st.form_submit_button("Generate PDF Report")

    if submitted and patient_name and patient_age:
        report_path = generate_pdf_report(df, accel_thresholds, gyro_thresholds, patient_name, patient_age)
        with open(report_path, "rb") as f:
            st.download_button("📥 Download Report", f, file_name="MPU_Session_Report.pdf")
    elif submitted:
        st.error("Please enter both patient name and age.")