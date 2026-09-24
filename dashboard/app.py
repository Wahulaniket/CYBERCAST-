import streamlit as st
import pandas as pd
import os
import sys

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.inference.engine import predict_attack_progression

st.set_page_config(page_title="AI Cyber Defence", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
# AI CYBER DEFENCE
### Predictive Network Security Operations Dashboard
*Temporal World Model for forecasting malicious network activity and attacker progression from network telemetry.*
""")

st.markdown("**● OFFLINE MODE | ● WORLD MODEL READY | ● INFERENCE ENGINE READY**")
st.markdown("---")

st.sidebar.header("Data Input")
data_source = st.sidebar.radio("Source", ["Demo Dataset", "Upload CSV"])
uploaded_file = None
if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload Telemetry", type=['csv'])

horizon = st.sidebar.selectbox("Prediction Horizon", [1, 3, 5, 10], index=1)
device_choice = st.sidebar.selectbox("Device", ["Auto", "CPU", "GPU"])

if st.sidebar.button("RUN ANALYSIS"):
    input_path = None
    if data_source == "Demo Dataset":
        input_path = "tests/data/sample_flow.csv"
        if not os.path.exists(input_path):
            st.error("No demo dataset available. Upload a compatible telemetry CSV.")
    elif uploaded_file is not None:
        input_path = "temp_upload.csv"
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    else:
        st.error("The uploaded telemetry file is empty or not provided.")
    
    if input_path and os.path.exists(input_path):
        with st.spinner("Running Inference Engine..."):
            try:
                res = predict_attack_progression(input_path)
                
                if res["status"] != "SUCCESS":
                    st.error(f"Inference Error: {res.get('status')}")
                else:
                    st.success("Analysis Complete")
                    
                    # Executive Metrics
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("CURRENT RISK", f"{res['current_risk']*100:.1f}%")
                    c2.metric("PREDICTED STAGE", res['predicted_stage'])
                    c3.metric("ALERT LEVEL", res['alert_level'])
                    c4.metric("RISK TREND", res['risk_trend'])
                    
                    st.markdown("---")
                    
                    # Risk Forecast
                    st.subheader("FUTURE RISK FORECAST")
                    st.caption("Forecast Horizon: 15 seconds")
                    risk_data = {"Current": res['current_risk']}
                    risk_data.update(res['risk_forecast'])
                    chart_df = pd.DataFrame(list(risk_data.items()), columns=['Time', 'Risk Probability'])
                    st.line_chart(chart_df.set_index('Time'))
                    st.info(res['explanation'])
                    
                    st.markdown("---")
                    
                    # ATT&CK Progression
                    st.subheader("ATTACK PROGRESSION")
                    st.caption("ATT&CK stage is an approximate behavioural mapping derived from predicted network-state characteristics.")
                    progression_str = f"{res['current_stage']} ➔ {res['predicted_stage']}"
                    st.markdown(f"**Progression:** {progression_str} (Confidence: {res['stage_confidence']*100:.1f}%)")
                    
                    st.markdown("---")
                    
                    # Explainability
                    e1, e2 = st.columns(2)
                    with e1:
                        st.subheader("TOP CONTRIBUTING FEATURES")
                        st.caption("WHY DID THE MODEL PREDICT THIS?")
                        feat_df = pd.DataFrame(res['top_features'])
                        if not feat_df.empty:
                            feat_chart_df = feat_df[['feature', 'attribution']].set_index('feature')
                            st.bar_chart(feat_chart_df)
                    
                    with e2:
                        st.subheader("TEMPORAL IMPORTANCE")
                        st.caption("Which historical time windows contributed most strongly.")
                        temp_df = pd.DataFrame({"Time Window": [f"T-{45 - i*5}s" for i in range(10)], "Importance": res['temporal_importance']})
                        st.bar_chart(temp_df.set_index('Time Window'))
                    
                    st.markdown("---")
                    
                    # Network State
                    st.subheader("PREDICTED FUTURE NETWORK STATES")
                    state_df = pd.DataFrame(res['predicted_states'])
                    st.dataframe(state_df)
                    
                    st.markdown("---")
                    
                    # Evidence / Status
                    st.subheader("DATA QUALITY & EVIDENCE")
                    raw_df = pd.read_csv(input_path)
                    st.dataframe(raw_df.tail())
                    
                    st.subheader("SYSTEM INFORMATION")
                    st.code(f"Architecture: {res['model']['name']}\nState Dimension: {res['model']['state_dimension']}\nSequence Length: {res['model']['sequence_length']}\nOffline Mode: Enabled")
                    
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
