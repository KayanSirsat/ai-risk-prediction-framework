"""
Global Styles Module
AI-Driven Risk Prediction Framework

Premium Indigo/Slate design system with high-fidelity styling.
"""

import streamlit as st

# Premium Color Palette
COLORS = {
    # Background Layers
    "bg_primary": "#020617",  # Slate-950
    "bg_card": "#0f172a",  # Slate-900
    "bg_elevated": "#1e293b",  # Slate-800
    "bg_tertiary": "#1e293b",  # Slate-800 (alias for compatibility)
    "bg_input": "#0f172a",  # Slate-900 (for inputs)
    "bg_sidebar": "#0f172a",  # Slate-900
    "bg_sidebar_hover": "#1e293b",  # Slate-800
    "bg_sidebar_active": "rgba(99, 102, 241, 0.15)",
    # Borders
    "border_primary": "#1e293b",  # Slate-800
    "border_secondary": "#334155",  # Slate-700
    "border_tertiary": "#475569",  # Slate-600
    "border_subtle": "#334155",  # Slate-700 (alias)
    "border_focus": "#6366f1",  # Indigo-500
    "border_sidebar": "rgba(255, 255, 255, 0.06)",
    # Brand/Accent
    "brand_primary": "#6366f1",  # Indigo-500
    "brand_dark": "#4f46e5",  # Indigo-600
    "brand_light": "#818cf8",  # Indigo-400
    "brand_subtle": "rgba(99, 102, 241, 0.1)",
    # Text
    "text_primary": "#f8fafc",  # Slate-50
    "text_secondary": "#e2e8f0",  # Slate-200
    "text_tertiary": "#cbd5e1",  # Slate-300
    "text_muted": "#94a3b8",  # Slate-400
    "text_disabled": "#64748b",  # Slate-500
    # Status Colors
    "success": "#22c55e",  # Green-500
    "success_bg": "rgba(34, 197, 94, 0.1)",
    "warning": "#f59e0b",  # Amber-500
    "warning_bg": "rgba(245, 158, 11, 0.1)",
    "error": "#ef4444",  # Red-500
    "error_bg": "rgba(239, 68, 68, 0.1)",
    "error_hover": "rgba(239, 68, 68, 0.1)",
    "info": "#3b82f6",  # Blue-500
    "info_bg": "rgba(59, 130, 246, 0.1)",
}


def apply_custom_styles():
    """Apply global premium CSS styles to the Streamlit app."""

    st.markdown(
        f"""
    <style>
        /* ============================================
           GLOBAL IMPORTS & RESETS
           ============================================ */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        /* Hide Streamlit Branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* ============================================
           MAIN LAYOUT
           ============================================ */
        .stApp {{
            background-color: {COLORS["bg_primary"]};
        }}
        
        .main .block-container {{
            padding: 2.5rem 3rem;
            max-width: 1400px;
        }}
        
        /* ============================================
           TYPOGRAPHY
           ============================================ */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLORS["text_primary"]} !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
        }}
        
        p, span, div, label {{
            color: {COLORS["text_secondary"]};
        }}
        
        /* ============================================
           METRIC CARDS (stMetric) - Premium Styling
           ============================================ */
        [data-testid="stMetric"] {{
            background: {COLORS["bg_card"]};
            border: 1px solid {COLORS["border_primary"]};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        [data-testid="stMetric"]:hover {{
            border-color: {COLORS["border_secondary"]};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
            transform: translateY(-1px);
        }}
        
        [data-testid="stMetric"] label {{
            color: {COLORS["text_muted"]} !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {COLORS["text_primary"]} !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            line-height: 1.2;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            margin-top: 0.25rem;
        }}
        
        /* ============================================
           BUTTONS - Premium with Transitions
           ============================================ */
        .stButton > button {{
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            border-radius: 6px !important;
            padding: 0.625rem 1.25rem !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border: none !important;
            letter-spacing: 0.01em;
        }}
        
        /* Primary Button - Indigo-600 */
        .stButton > button[kind="primary"] {{
            background: {COLORS["brand_dark"]} !important;
            color: white !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        }}
        
        .stButton > button[kind="primary"]:hover {{
            background: {COLORS["brand_primary"]} !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.5) !important;
            transform: translateY(-1px);
        }}
        
        .stButton > button[kind="primary"]:active {{
            transform: translateY(0);
        }}
        
        /* Secondary Button */
        .stButton > button[kind="secondary"] {{
            background: transparent !important;
            color: {COLORS["text_secondary"]} !important;
            border: 1px solid {COLORS["border_primary"]} !important;
        }}
        
        .stButton > button[kind="secondary"]:hover {{
            background: {COLORS["bg_card"]} !important;
            border-color: {COLORS["border_secondary"]} !important;
            color: {COLORS["text_primary"]} !important;
        }}
        
        /* ============================================
           SIDEBAR - Clean Unified Background
           ============================================ */
        [data-testid="stSidebar"] {{
            background: {COLORS["bg_primary"]} !important;
            border-right: 1px solid {COLORS["border_primary"]};
        }}
        
        [data-testid="stSidebar"] > div:first-child {{
            background: {COLORS["bg_primary"]};
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: {COLORS["text_secondary"]};
        }}
        
        /* Sidebar Navigation Items */
        [data-testid="stSidebar"] .stRadio > div {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
            padding: 0 0.75rem;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label {{
            background: transparent;
            border-radius: 8px;
            padding: 0.75rem;
            margin: 0;
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid transparent;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label:hover {{
            background: {COLORS["bg_card"]};
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {{
            background: {COLORS["brand_subtle"]};
            border-color: rgba(99, 102, 241, 0.3);
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label span {{
            color: {COLORS["text_secondary"]} !important;
            font-weight: 500 !important;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] span {{
            color: {COLORS["text_primary"]} !important;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label > div:first-child {{
            display: none;
        }}
        
        /* ============================================
           FORM INPUTS - White on Dark
           ============================================ */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextArea > div > div > textarea {{
            background: {COLORS["bg_elevated"]} !important;
            border: 1px solid {COLORS["border_primary"]} !important;
            border-radius: 8px !important;
            color: {COLORS["text_primary"]} !important;
            font-size: 0.9rem !important;
            padding: 0.75rem 1rem !important;
            transition: all 0.2s ease;
        }}
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {COLORS["brand_primary"]} !important;
            box-shadow: 0 0 0 3px {COLORS["brand_subtle"]} !important;
            outline: none;
        }}
        
        .stTextInput > div > div > input::placeholder {{
            color: {COLORS["text_muted"]} !important;
        }}
        
        .stTextInput > label,
        .stSelectbox > label,
        .stTextArea > label {{
            color: {COLORS["text_tertiary"]} !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem;
        }}
        
        /* Select Dropdown Styling */
        [data-baseweb="select"] > div {{
            background: {COLORS["bg_elevated"]} !important;
            border-color: {COLORS["border_primary"]} !important;
        }}
        
        /* ============================================
           SLIDERS
           ============================================ */
        .stSlider > div > div > div > div {{
            background: {COLORS["brand_primary"]} !important;
        }}
        
        .stSlider > div > div > div {{
            background: {COLORS["border_primary"]} !important;
        }}
        
        .stSlider [data-testid="stTickBarMin"],
        .stSlider [data-testid="stTickBarMax"] {{
            color: {COLORS["text_muted"]} !important;
        }}
        
        /* ============================================
           TOGGLES/CHECKBOXES
           ============================================ */
        .stCheckbox > label {{
            color: {COLORS["text_secondary"]} !important;
        }}
        
        /* ============================================
           DATA TABLES
           ============================================ */
        [data-testid="stDataFrame"] {{
            background: {COLORS["bg_card"]};
            border: 1px solid {COLORS["border_primary"]};
            border-radius: 12px;
            overflow: hidden;
        }}
        
        [data-testid="stDataFrame"] thead tr th {{
            background: {COLORS["bg_elevated"]} !important;
            color: {COLORS["text_tertiary"]} !important;
            font-weight: 600 !important;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 1rem !important;
            border-bottom: 1px solid {COLORS["border_primary"]} !important;
        }}
        
        [data-testid="stDataFrame"] tbody tr td {{
            background: {COLORS["bg_card"]} !important;
            color: {COLORS["text_secondary"]} !important;
            padding: 0.875rem 1rem !important;
            border-bottom: 1px solid {COLORS["border_primary"]} !important;
        }}
        
        [data-testid="stDataFrame"] tbody tr:hover td {{
            background: {COLORS["bg_elevated"]} !important;
        }}
        
        /* ============================================
           CUSTOM COMPONENTS
           ============================================ */
        
        /* Premium Card */
        .premium-card {{
            background: {COLORS["bg_card"]};
            border: 1px solid {COLORS["border_primary"]};
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
        }}
        
        /* Chart Placeholder with Dashed Border */
        .chart-placeholder {{
            background: transparent;
            border: 2px dashed {COLORS["border_secondary"]};
            border-radius: 12px;
            padding: 3rem 2rem;
            text-align: center;
            transition: all 0.2s ease;
        }}
        
        .chart-placeholder:hover {{
            border-color: {COLORS["border_tertiary"]};
            background: rgba(255, 255, 255, 0.02);
        }}
        
        .chart-placeholder-icon {{
            font-size: 2.5rem;
            color: {COLORS["text_disabled"]};
            margin-bottom: 1rem;
        }}
        
        .chart-placeholder-title {{
            color: {COLORS["text_muted"]};
            font-size: 0.95rem;
            font-weight: 500;
        }}
        
        .chart-placeholder-subtitle {{
            color: {COLORS["text_disabled"]};
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }}
        
        /* Risk Banner with Thick Left Border */
        .risk-banner {{
            border-radius: 8px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.5rem;
            border-left: 4px solid;
            transition: all 0.2s ease;
        }}
        
        .risk-banner-high {{
            background: {COLORS["error_bg"]};
            border-left-color: {COLORS["error"]};
        }}
        
        .risk-banner-medium {{
            background: {COLORS["warning_bg"]};
            border-left-color: {COLORS["warning"]};
        }}
        
        .risk-banner-low {{
            background: {COLORS["success_bg"]};
            border-left-color: {COLORS["success"]};
        }}
        
        .risk-banner-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: {COLORS["text_muted"]};
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .risk-banner-value {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 0.25rem;
        }}
        
        .risk-value-high {{ color: {COLORS["error"]}; }}
        .risk-value-medium {{ color: {COLORS["warning"]}; }}
        .risk-value-low {{ color: {COLORS["success"]}; }}
        
        /* Status Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }}
        
        .badge-high {{
            background: {COLORS["error_bg"]};
            color: {COLORS["error"]};
        }}
        
        .badge-medium {{
            background: {COLORS["warning_bg"]};
            color: {COLORS["warning"]};
        }}
        
        .badge-low {{
            background: {COLORS["success_bg"]};
            color: {COLORS["success"]};
        }}
        
        .badge-info {{
            background: {COLORS["info_bg"]};
            color: {COLORS["info"]};
        }}
        
        /* Micro-copy */
        .micro-copy {{
            font-size: 0.8rem;
            margin-top: 0.5rem;
            font-weight: 500;
        }}
        
        .micro-copy-positive {{
            color: {COLORS["success"]};
        }}
        
        .micro-copy-negative {{
            color: {COLORS["error"]};
        }}
        
        .micro-copy-neutral {{
            color: {COLORS["text_muted"]};
        }}
        
        /* Header */
        .app-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid {COLORS["border_primary"]};
        }}
        
        .header-brand {{
            display: flex;
            align-items: center;
            gap: 0.875rem;
        }}
        
        .header-logo {{
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, {COLORS["brand_primary"]} 0%, {COLORS["brand_dark"]} 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .header-title {{
            font-size: 1.35rem;
            font-weight: 700;
            color: {COLORS["text_primary"]};
            letter-spacing: -0.02em;
        }}
        
        .status-indicator {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: {COLORS["success_bg"]};
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 20px;
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
            font-weight: 600;
            color: {COLORS["success"]};
        }}
        
        .status-dot {{
            width: 8px;
            height: 8px;
            background: {COLORS["success"]};
            border-radius: 50%;
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        /* Page Headers */
        .page-title {{
            font-size: 1.875rem;
            font-weight: 700;
            color: {COLORS["text_primary"]};
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }}
        
        .page-subtitle {{
            font-size: 1rem;
            color: {COLORS["text_muted"]};
            margin-bottom: 2rem;
            font-weight: 400;
        }}
        
        .section-header {{
            font-size: 0.875rem;
            font-weight: 600;
            color: {COLORS["text_muted"]};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid {COLORS["border_primary"]};
        }}
        
        /* Settings Card */
        .settings-card {{
            background: {COLORS["bg_card"]};
            border: 1px solid {COLORS["border_primary"]};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        
        .settings-card-title {{
            font-size: 1rem;
            font-weight: 600;
            color: {COLORS["text_primary"]};
            margin-bottom: 1.25rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid {COLORS["border_primary"]};
        }}
        
        /* SHAP Progress Bar - Indigo */
        .shap-progress-bar {{
            background: {COLORS["bg_elevated"]};
            border-radius: 6px;
            height: 8px;
            overflow: hidden;
        }}
        
        .shap-progress-fill {{
            background: {COLORS["brand_primary"]};
            height: 100%;
            border-radius: 6px;
            transition: width 0.3s ease;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_header():
    """Render the global application header."""
    st.markdown(
        """
        <div class="app-header">
            <div class="header-brand">
                <div class="header-logo">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <span class="header-title">RiskAI</span>
            </div>
            <div class="status-indicator">
                <span class="status-dot"></span>
                System Active
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str):
    """Render page title and subtitle."""
    st.markdown(
        f"""
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
    """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str):
    """Render section header."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
