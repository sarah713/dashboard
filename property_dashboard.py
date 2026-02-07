import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import os
from io import BytesIO
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# Page configuration
st.set_page_config(
    page_title="Property Consultants Dashboard", 
    layout="wide",
    initial_sidebar_state="collapsed"
)
count = st_autorefresh(interval=30000, key="datarefresh")
# Binayah Theme Colors
FOREST_GREEN = '#004D42'
GOLDEN = '#D4AF37'
TEXT_DARK = '#1A1A1A'

# Custom CSS
st.markdown(f"""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Background */
    .stApp {{
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    }}
    
    /* Remove all default padding */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 98% !important;
    }}
    
    /* Hide empty elements */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"]:empty {{
        display: none !important;
    }}
    
    /* Team section styling */
    .team-section {{
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    }}
    
    /* Headers */
    h2 {{
        color: {FOREST_GREEN};
        font-weight: 700;
        font-size: 1.8rem;
        padding-bottom: 0.8rem;
        margin-bottom: 1.5rem;
        margin-top: 0;
        border-bottom: 2px solid {GOLDEN};
    }}
    
    /* Remove extra spacing from Streamlit elements */
    .element-container {{
        margin-bottom: 0 !important;
    }}
    
    /* Hide empty containers */
    div:empty {{
        display: none !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Helper Functions
def load_google_sheet(sheet_url):
    """
    Load data from Google Sheets.
    Sheet must be published to the web or shared with 'Anyone with the link can view'
    
    Input: Google Sheets URL (regular or sharing link)
    Returns: pandas DataFrame
    """
    try:
        # Extract sheet ID from URL
        if '/d/' in sheet_url:
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        else:
            st.error("Invalid Google Sheets URL format")
            return None
        
        # Convert to CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        # Read the CSV
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"Error loading Google Sheet: {str(e)}")
        st.info("Make sure the sheet is shared as 'Anyone with the link can view'")
        return None

def load_image_from_drive(drive_url):
    """Convert Google Drive share link to direct download link and load image"""
    try:
        if pd.isna(drive_url) or str(drive_url).strip() == '':
            return None
            
        drive_url = str(drive_url)
        
        if '/file/d/' in drive_url:
            file_id = drive_url.split('/file/d/')[1].split('/')[0]
        elif 'id=' in drive_url:
            file_id = drive_url.split('id=')[1].split('&')[0]
        else:
            return None
        
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return img
    except Exception:
        return None
    return None

def create_horizontal_bar_chart(agent_name, metric1_name, metric1_value, metric2_name, metric2_value):
    """Create a horizontal bar chart with two metrics"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=[agent_name], 
        x=[metric1_value], 
        name=metric1_name,
        orientation='h', 
        marker=dict(color=FOREST_GREEN),
        text=[metric1_value], 
        textposition='inside',
        textfont=dict(color='white', size=14, family='Arial Black'),
        hovertemplate=f'<b>{metric1_name}</b>: %{{x}}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        y=[agent_name], 
        x=[metric2_value], 
        name=metric2_name,
        orientation='v', 
        marker=dict(color=GOLDEN),
        text=[metric2_value], 
        textposition='inside',
        textfont=dict(color='white', size=14, family='Arial Black'),
        hovertemplate=f'<b>{metric2_name}</b>: %{{x}}<extra></extra>'
    ))
    
    fig.update_layout(
        height=120, 
        margin=dict(l=100, r=40, t=50, b=20),
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation='h', 
            yanchor='top', 
            y=1.3, 
            xanchor='left', 
            x=0,
            font=dict(size=11)
        ),
        xaxis=dict(
            showgrid=True, 
            gridcolor='#E8E8E8', 
            showline=False, 
            zeroline=False,
            fixedrange=True
        ),
        yaxis=dict(
            showgrid=False, 
            showline=False, 
            tickfont=dict(size=12, color=TEXT_DARK, family='Arial', weight='bold')
        ),
        bargap=0.3,
        barmode='group'
    )
    return fig

# Main Application
def main():
    # Logo (only if exists)
    if os.path.exists('binayah.png'):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            logo = Image.open('binayah.png')
            st.image(logo, width=200)

    # Google Sheets URL Input
    # Store the sheet URL in Streamlit secrets or as environment variable for deployed version
    # For local testing, you can hardcode it here temporarily
    
    # Check if running locally or deployed
    if 'GOOGLE_SHEET_URL' in st.secrets:
        # Deployed version - read from secrets
        sheet_url = st.secrets['GOOGLE_SHEET_URL']
        df = load_google_sheet(sheet_url)
    else:
        # Local version - show input or use hardcoded URL
        st.markdown("### 📊 Configure Data Source")
        sheet_url = st.text_input(
            "Google Sheets URL", 
            placeholder="https://docs.google.com/spreadsheets/d/1FdRDF7z5v7ejd1Ld6VUvDtASPE3tS36-MrbGg1cSUHY/edit",
            help="Paste your Google Sheets URL here. Sheet must be shared with 'Anyone with the link can view'"
        )
        
        if sheet_url:
            df = load_google_sheet(sheet_url)
        else:
            st.info("👆 Please enter your Google Sheets URL to load the dashboard")
            
            # Show instructions
            with st.expander("📋 How to set up your Google Sheet"):
                st.markdown("""
                **Step 1: Prepare your Google Sheet**
                - Create a Google Sheet with these exact columns:
                  - Agent Name
                  - Team (values: "Offplan" or "Secondary")
                  - Calls Made
                  - Meetings Done
                  - Listings Done
                  - Photo (Google Drive links)
                
                **Step 2: Share your sheet**
                - Click "Share" button
                - Change to "Anyone with the link can view"
                - Copy the link
                
                **Step 3: Paste the link above**
                - The dashboard will load automatically
                - Any changes to the sheet will reflect when you refresh
                
                **For deployment:**
                - Add your sheet URL to Streamlit secrets as `GOOGLE_SHEET_URL`
                """)
            st.stop()
    
    if df is None:
        st.stop()
    
    # Validate columns
    required_columns = ['Agent Name', 'Team', 'Calls Made', 'Meetings Done', 'Listings Done', 'Photo']
    if not all(col in df.columns for col in required_columns):
        st.error(f"Sheet must contain these columns: {', '.join(required_columns)}")
        st.info(f"Found columns: {', '.join(df.columns)}")
        st.stop()
    
    # Data Processing
    offplan_df = df[df['Team'].str.strip().str.lower() == 'offplan'].copy()
    secondary_df = df[df['Team'].str.strip().str.lower() == 'secondary'].copy()
    
    def score(row):
        m = row['Meetings Done'] if pd.notna(row['Meetings Done']) else 0
        c = row['Calls Made'] if pd.notna(row['Calls Made']) else 0
        return (m * 0.8) + (c * 0.2)
    
    for d in [offplan_df, secondary_df]:
        d['Score'] = d.apply(score, axis=1)
        d.sort_values('Score', ascending=False, inplace=True)

    # Two-column layout
    left_col, right_col = st.columns(2, gap="large")
    
    # OFFPLAN TEAM
    with left_col:
        st.markdown("<div class='team-section'>", unsafe_allow_html=True)
        st.markdown("<h2>OFFPLAN PROJECTS</h2>", unsafe_allow_html=True)
        
        for _, row in offplan_df.iterrows():
            cols = st.columns([1, 4])
            
            with cols[0]:
                img = load_image_from_drive(row['Photo'])
                if img: 
                    st.image(img, use_container_width=True)
                else: 
                    st.markdown(f"<p style='text-align:center; padding-top:30px; font-weight:bold; color:{FOREST_GREEN};'>{row['Agent Name']}</p>", unsafe_allow_html=True)
            
            with cols[1]:
                calls = int(row['Calls Made']) if pd.notna(row['Calls Made']) else 0
                meetings = int(row['Meetings Done']) if pd.notna(row['Meetings Done']) else 0
                fig = create_horizontal_bar_chart(row['Agent Name'], "Calls", calls, "Meetings", meetings)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("</div>", unsafe_allow_html=True)

    # SECONDARY TEAM
    with right_col:
        st.markdown("<div class='team-section'>", unsafe_allow_html=True)
        st.markdown("<h2>SECONDARY</h2>", unsafe_allow_html=True)
        
        for _, row in secondary_df.iterrows():
            cols = st.columns([1, 4])
            
            with cols[0]:
                img = load_image_from_drive(row['Photo'])
                if img: 
                    st.image(img, use_container_width=True)
                else: 
                    st.markdown(f"<p style='text-align:center; padding-top:30px; font-weight:bold; color:{FOREST_GREEN};'>{row['Agent Name']}</p>", unsafe_allow_html=True)
            
            with cols[1]:
                calls = int(row['Calls Made']) if pd.notna(row['Calls Made']) else 0
                listings = int(row['Listings Done']) if pd.notna(row['Listings Done']) else 0
                fig = create_horizontal_bar_chart(row['Agent Name'], "Calls", calls, "Listings", listings)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()