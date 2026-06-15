import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="AI Security Copilot Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# MODERN DARK THEME STYLING
# ==========================================
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Main App Background */
    .stApp {
        background-color: #0f1419;
        color: #e0e7ff;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0a0e14;
        border-right: 1px solid #1e293b;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        border-left: none;
    }
    
    /* Remove Streamlit default margins */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1a202c 0%, #0f172a 100%);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 24px;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
        transform: translateY(-2px);
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
    }
    
    .metric-trend {
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .trend-up {
        color: #10b981;
    }
    
    .trend-danger {
        color: #ef4444;
    }
    
    /* Tables */
    .table-wrapper {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Header */
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 28px;
        padding-bottom: 20px;
        border-bottom: 1px solid #1e293b;
    }
    
    .page-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    
    .page-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 4px;
    }
    
    .timestamp-badge {
        background: #1e293b;
        color: #94a3b8;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Section Titles */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 16px;
        margin-top: 24px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Badge Styles */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-high {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .badge-medium {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-low {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .badge-completed {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* Status Indicator */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        margin-right: 6px;
    }
    
    /* Threat Bars */
    .threat-item {
        margin-bottom: 16px;
    }
    
    .threat-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    
    .threat-label-text {
        color: #e0e7ff;
    }
    
    .threat-count {
        color: #94a3b8;
        font-weight: 600;
    }
    
    .threat-bar-bg {
        background: #1e293b;
        border-radius: 8px;
        height: 6px;
        overflow: hidden;
    }
    
    .threat-bar-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.3s ease;
    }
    
    /* Chat Panel */
    .chat-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid #1e293b;
    }
    
    .chat-icon {
        font-size: 1.8rem;
    }
    
    .chat-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #f8fafc;
        margin: 0;
    }
    
    .chat-status {
        font-size: 0.8rem;
        color: #10b981;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 4px;
    }
    
    /* Placeholder text */
    .placeholder-text {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
    
    /* Links and buttons */
    .view-all-btn {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .view-all-btn:hover {
        background: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# DATA & HELPER FUNCTIONS
# ==========================================
def get_log_data():
    """Generate sample log analysis data"""
    logs = [
        ["auth.log", "Linux Auth Log", "18 May 2025, 10:45 PM", "Completed", "Medium"],
        ["apache_access.log", "Apache Log", "18 May 2025, 10:30 PM", "Completed", "High"],
        ["windows_security.evtx", "Windows Event Log", "18 May 2025, 09:15 PM", "Completed", "Medium"],
        ["nginx_error.log", "Nginx Log", "18 May 2025, 08:40 PM", "Completed", "Low"],
        ["system.log", "System Log", "18 May 2025, 08:10 PM", "Completed", "Low"],
    ]
    return pd.DataFrame(logs, columns=["Log File", "Type", "Analyzed At", "Status", "Risk Level"])

def get_recent_reports():
    """Generate sample recent reports"""
    reports = [
        ["Security_Report_18_May.pdf", "18 May 2025, 10:40 PM"],
        ["Threat_Analysis_Report.pdf", "18 May 2025, 09:30 PM"],
        ["Vulnerability_Assessment.pdf", "18 May 2025, 08:20 PM"],
    ]
    return pd.DataFrame(reports, columns=["Report Name", "Generated At"])

def get_threat_data():
    """Get threat detection data"""
    threats = [
        {"name": "Brute Force Attempts", "count": 18, "color": "#ef4444", "percentage": 85},
        {"name": "Failed Login Attempt", "count": 12, "color": "#f59e0b", "percentage": 60},
        {"name": "SQL Injection Attempt", "count": 5, "color": "#f59e0b", "percentage": 25},
        {"name": "Suspicious IP Access", "count": 4, "color": "#3b82f6", "percentage": 25},
        {"name": "Malware Activity", "count": 2, "color": "#8b5cf6", "percentage": 10},
    ]
    return threats

def get_risk_distribution():
    """Get risk distribution data for pie chart"""
    return {
        "High": 12,
        "Medium": 18,
        "Low": 20
    }

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### 🛡️ AI SECURITY COPILOT")
    st.markdown("---")
    
    menu_items = [
        ("📊", "Dashboard", "dashboard"),
        ("📄", "Log Analyzer", "logs"),
        ("🤖", "AI Copilot", "copilot"),
        ("🔍", "Vulnerability Explorer", "vuln"),
        ("📊", "Threat Intelligence", "threats"),
        ("📋", "Reports", "reports"),
        ("📦", "Assets", "assets"),
        ("⚙️", "Settings", "settings"),
    ]
    
    for icon, label, key in menu_items:
        st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{key}")
    
    st.markdown("---")
    
    # User Profile Section
    st.markdown("""
    <div style='background: #111827; padding: 20px; border-radius: 12px; border: 1px solid #1e293b;'>
        <div style='display: flex; align-items: center; gap: 12px;'>
            <div style='width: 40px; height: 40px; border-radius: 50%; background: #3b82f6; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 0.8rem;'>CA</div>
            <div>
                <div style='font-size: 0.95rem; font-weight: 600; color: #f8fafc;'>Cyber Analyst</div>
                <div style='font-size: 0.75rem; color: #10b981; display: flex; align-items: center; gap: 6px;'><span style='width: 6px; height: 6px; background: #10b981; border-radius: 50%;'></span>Online</div>
            </div>
        </div>
        <div style='margin-top: 16px;'>
            <div style='font-size: 0.75rem; color: #94a3b8; margin-bottom: 8px;'>Pro Plan</div>
            <div style='background: #1e293b; border-radius: 8px; height: 4px; overflow: hidden;'>
                <div style='background: #3b82f6; height: 100%; width: 75%;'></div>
            </div>
            <div style='font-size: 0.7rem; color: #64748b; margin-top: 6px;'>Expires: 12 Dec 2025</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN CONTENT
# ==========================================
# Page Header
st.markdown(f"""
<div class='page-header'>
    <div>
        <h1 class='page-title'>Dashboard Overview</h1>
        <p class='page-subtitle'>Monitor your security posture and analysis in real time.</p>
    </div>
    <div class='timestamp-badge'>📅 {datetime.now().strftime('%d %b %Y')} | 🕒 {datetime.now().strftime('%I:%M %p')}</div>
</div>
""", unsafe_allow_html=True)

# Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>📁 Logs Analyzed</div>
        <div class='metric-value'>1,248</div>
        <div class='metric-trend trend-up'>↑ 12% from yesterday</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>🚨 Alerts Detected</div>
        <div class='metric-value' style='color: #ef4444;'>37</div>
        <div class='metric-trend trend-danger'>↑ 8% from yesterday</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>📈 Risk Score</div>
        <div class='metric-value' style='color: #f59e0b;'>68</div>
        <div style='font-size: 0.8rem; color: #f59e0b; margin-top: 8px;'>Medium Risk</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>📊 Reports Generated</div>
        <div class='metric-value' style='color: #10b981;'>12</div>
        <div class='metric-trend trend-up'>↑ 20% from yesterday</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main Content Area
col_main, col_chat = st.columns([1.6, 1])

with col_main:
    # Recent Log Analysis
    st.markdown("<h3 class='section-title'>🔍 Recent Log Analysis</h3>", unsafe_allow_html=True)
    
    col_table, col_view = st.columns([5, 1])
    with col_view:
        st.markdown("<div style='text-align: right; margin-top: 8px;'><button class='view-all-btn'>View All</button></div>", unsafe_allow_html=True)
    
    log_df = get_log_data()
    st.markdown("""
    <style>
    .dataframe {
        background: #111827 !important;
        color: #e0e7ff !important;
        border: 1px solid #1e293b !important;
    }
    .dataframe thead {
        background: #0f1419 !important;
    }
    .dataframe th {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.dataframe(log_df, use_container_width=True, hide_index=True)
    
    # Charts Row
    st.markdown("<br>", unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("<h3 class='section-title'>📊 Risk Distribution</h3>", unsafe_allow_html=True)
        
        risk_data = get_risk_distribution()
        fig = go.Figure(data=[go.Pie(
            labels=list(risk_data.keys()),
            values=list(risk_data.values()),
            hole=.3,
            marker=dict(
                colors=['#ef4444', '#f59e0b', '#10b981'],
                line=dict(color='#0f1419', width=2)
            ),
            textposition='auto',
            hoverinfo='label+value+percent',
        )])
        
        fig.update_layout(
            template='plotly_dark',
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff', size=11),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("""
        <div style='font-size: 0.8rem; color: #94a3b8; margin-top: 12px;'>
            <div style='margin-bottom: 8px;'><span style='color: #ef4444;'>■</span> High (12) - 24%</div>
            <div style='margin-bottom: 8px;'><span style='color: #f59e0b;'>■</span> Medium (18) - 36%</div>
            <div><span style='color: #10b981;'>■</span> Low (20) - 40%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_chart2:
        st.markdown("<h3 class='section-title'>⚠️ Top Threats Detected</h3>", unsafe_allow_html=True)
        
        threats = get_threat_data()
        threats_html = ""
        
        for threat in threats:
            threats_html += f"""
            <div class='threat-item'>
                <div class='threat-label'>
                    <span class='threat-label-text'>{threat['name']}</span>
                    <span class='threat-count' style='color: {threat['color']};'>{threat['count']}</span>
                </div>
                <div class='threat-bar-bg'>
                    <div class='threat-bar-fill' style='width: {threat['percentage']}%; background: {threat['color']};'></div>
                </div>
            </div>
            """
        
        st.markdown(f"<div style='background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 20px;'>{threats_html}</div>", unsafe_allow_html=True)
    
    # Recent Reports
    st.markdown("<h3 class='section-title'>📋 Recent Reports</h3>", unsafe_allow_html=True)
    
    reports_df = get_recent_reports()
    st.dataframe(reports_df, use_container_width=True, hide_index=True)
    
    col_space, col_btn = st.columns([4, 1])
    with col_btn:
        st.markdown("<div style='text-align: right;'><button class='view-all-btn'>View All</button></div>", unsafe_allow_html=True)

# Chat Panel
with col_chat:
    st.markdown("""
    <div class='chat-header'>
        <div class='chat-icon'>🤖</div>
        <div>
            <h3 class='chat-title'>AI Security Copilot</h3>
            <div class='chat-status'><span style='width: 6px; height: 6px; background: #10b981; border-radius: 50%;'></span>Online</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat Messages Container
    chat_container = st.container(height=400)
    
    with chat_container:
        # Welcome message
        st.chat_message("assistant").markdown("""
        👋 **Hello Cyber Analyst!**
        
        I'm your AI Security Copilot powered by advanced ML models. I can help you with:
        
        • 🔍 Log analysis & threat detection
        • 🎯 Vulnerability assessments
        • 📊 Security reports
        • 💡 Incident response guidance
        
        *What can I help you with today?*
        """)
    
    # Chat Input
    st.markdown("<br>", unsafe_allow_html=True)
    user_input = st.chat_input("Ask anything about security...")
    
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.chat_message("assistant").markdown("""
        I've processed your request. Based on our analysis:
        
        **Key Findings:**
        - ✅ No critical threats detected
        - ⚠️ 3 medium-risk alerts
        - 📈 Trend: Stable over last 24h
        
        Would you like me to dive deeper into any area?
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #64748b; padding-top: 16px;'>
    <div>🔒 System Status: <span style='color: #10b981;'>Secure</span> | 🤖 AI Engine: <span style='color: #3b82f6;'>GPT-4o</span> | 💾 Database: <span style='color: #10b981;'>Connected</span></div>
    <div>Version: 1.0.0</div>
</div>
""", unsafe_allow_html=True)
