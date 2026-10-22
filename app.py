import os
from datetime import date
import pandas as pd
import streamlit as st

# PDF Generation imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

DATA_FILE = "water_quality_records.csv"

st.set_page_config(page_title="Natural Shrimp Aquaculture - Central Lab Management", layout="wide")

# 1. Initialize Data File with Correct Lab Headings
def init_data():
    if not os.path.exists(DATA_FILE):
        default_df = pd.DataFrame(columns=[
            "Record_ID", "Date", "Client_Block", "Sample_Name", "Sample_Source",
            "Technician", "pH", "DO_mgL", "Alkalinity", "Ammonia_TAN", "Nitrate", 
            "Nitrite", "Phosphorus", "TSS", "EC", "TDS",
            "Plankton_Observed", "Plankton_Prevalence",
            "Total_Vibrios", "Total_Coliforms_TPC", "Luminescent_Vibrios",
            "Risk_Status", "Remarks"
        ])
        default_df.to_csv(DATA_FILE, index=False)

init_data()

EXPECTED_COLUMNS = [
    "Record_ID", "Date", "Client_Block", "Sample_Name", "Sample_Source",
    "Technician", "pH", "DO_mgL", "Alkalinity", "Ammonia_TAN", "Nitrate",
    "Nitrite", "Phosphorus", "TSS", "EC", "TDS", "Plankton_Observed",
    "Plankton_Prevalence", "Total_Vibrios", "Total_Coliforms_TPC",
    "Luminescent_Vibrios", "Risk_Status", "Remarks"
]

def load_data():
    """Load records safely and ensure the expected columns are available."""
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    try:
        df = pd.read_csv(DATA_FILE)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
        st.error("The records CSV could not be read. Please check the data file or restore a backup.")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    for column in EXPECTED_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA

    return df[EXPECTED_COLUMNS]

def save_data(df):
    """Save records using the standard column order."""
    df = df.reindex(columns=EXPECTED_COLUMNS)
    df.to_csv(DATA_FILE, index=False)

# Official Central Lab Report PDF Generator Function
def generate_lab_report_pdf(row):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=13, leading=15, alignment=1, textColor=colors.HexColor("#315F91"))
    subtitle_style = ParagraphStyle(name='SubTitleStyle', parent=styles['Heading2'], fontSize=10, leading=12, alignment=1, textColor=colors.HexColor("#4F5D65"))
    cell_style = ParagraphStyle(name='CellStyle', parent=styles['Normal'], fontSize=8.5, leading=10)
    bold_cell = ParagraphStyle(name='BoldCellStyle', parent=styles['Normal'], fontSize=8.5, leading=10, fontName='Helvetica-Bold')

    # Header section matching Central Lab Format
    story.append(Paragraph("<b>NATURAL SHRIMP AQUACULTURE LLC (NSA)</b>", title_style))
    story.append(Paragraph("CENTRAL LAB - WATER QUALITY PARAMETER TEST REPORT", subtitle_style))
    story.append(Paragraph("SOP Code: CL/AP/WQM/PC/SOP-01-F01 | Revision No: 01", subtitle_style))
    story.append(Spacer(1, 10))

    # Customer & Lab Information Section
    info_data = [
        [Paragraph("<b>Record ID:</b>", cell_style), Paragraph(str(row.get("Record_ID", "")), cell_style), Paragraph("<b>Date:</b>", cell_style), Paragraph(str(row.get("Date", "")), cell_style)],
        [Paragraph("<b>Client / Block:</b>", cell_style), Paragraph(str(row.get("Client_Block", "")), cell_style), Paragraph("<b>Technician:</b>", cell_style), Paragraph(str(row.get("Technician", "")), cell_style)],
        [Paragraph("<b>Sample Name:</b>", cell_style), Paragraph(str(row.get("Sample_Name", "")), cell_style), Paragraph("<b>Sample Source:</b>", cell_style), Paragraph(str(row.get("Sample_Source", "")), cell_style)],
    ]
    t_info = Table(info_data, colWidths=[100, 170, 100, 170])
    t_info.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#315F91")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F2F5F8")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 10))

    # 1. Physical & Chemical Parameters Table
    story.append(Paragraph("<b>1. PHYSICAL & CHEMICAL PARAMETERS (ANALYTICAL PROCEDURES)</b>", bold_cell))
    story.append(Spacer(1, 4))
    
    chem_headers = ["Parameters", "Unit", "Test Method", "Result", "Optimum Range"]
    chem_rows = [
        [Paragraph(f"<b>{h}</b>", bold_cell) for h in chem_headers],
        [Paragraph("pH Level", cell_style), Paragraph("-", cell_style), Paragraph("pH Meter", cell_style), Paragraph(str(row.get("pH", "")), cell_style), Paragraph("7.5 - 8.5", cell_style)],
        [Paragraph("Dissolved Oxygen (DO)", cell_style), Paragraph("mg/L", cell_style), Paragraph("DO Meter", cell_style), Paragraph(str(row.get("DO_mgL", "")), cell_style), Paragraph("> 4.5", cell_style)],
        [Paragraph("Alkalinity", cell_style), Paragraph("mg/L", cell_style), Paragraph("HACH 8203", cell_style), Paragraph(str(row.get("Alkalinity", "")), cell_style), Paragraph("> 100", cell_style)],
        [Paragraph("Nitrogen: Ammonical (TAN)", cell_style), Paragraph("mg/L", cell_style), Paragraph("HACH 8155", cell_style), Paragraph(str(row.get("Ammonia_TAN", "")), cell_style), Paragraph("< 0.5", cell_style)],
        [Paragraph("Nitrogen: Nitrate", cell_style), Paragraph("mg/L", cell_style), Paragraph("HACH 8171", cell_style), Paragraph(str(row.get("Nitrate", "")), cell_style), Paragraph("< 5.0", cell_style)],
        [Paragraph("Nitrogen: Nitrite", cell_style), Paragraph("mg/L", cell_style), Paragraph("HACH 8507", cell_style), Paragraph(str(row.get("Nitrite", "")), cell_style), Paragraph("< 1.0", cell_style)],
        [Paragraph("Phosphorus", cell_style), Paragraph("mg/L", cell_style), Paragraph("HACH 8048", cell_style), Paragraph(str(row.get("Phosphorus", "")), cell_style), Paragraph("0.5 - 20", cell_style)],
        [Paragraph("TSS", cell_style), Paragraph("mg/L", cell_style), Paragraph("HACH", cell_style), Paragraph(str(row.get("TSS", "")), cell_style), Paragraph("-", cell_style)],
        [Paragraph("Electrical Conductivity (EC)", cell_style), Paragraph("ms/cm", cell_style), Paragraph("HACH", cell_style), Paragraph(str(row.get("EC", "")), cell_style), Paragraph("-", cell_style)],
        [Paragraph("TDS", cell_style), Paragraph("ppm", cell_style), Paragraph("-", cell_style), Paragraph(str(row.get("TDS", "")), cell_style), Paragraph("-", cell_style)],
    ]
    
    t_chem = Table(chem_rows, colWidths=[150, 60, 100, 90, 140])
    t_chem.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#315F91")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_chem)
    story.append(Spacer(1, 10))

    # 2. Plankton Distribution Table
    story.append(Paragraph("<b>2. PLANKTON DISTRIBUTION</b>", bold_cell))
    story.append(Spacer(1, 4))
    plankton_data = [
        [Paragraph("<b>Plankton Observed</b>", bold_cell), Paragraph("<b>Prevalence (%)</b>", bold_cell)],
        [Paragraph(str(row.get("Plankton_Observed", "")), cell_style), Paragraph(str(row.get("Plankton_Prevalence", "")) + "%", cell_style)]
    ]
    t_plankton = Table(plankton_data, colWidths=[300, 240])
    t_plankton.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F5D65")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_plankton)
    story.append(Spacer(1, 10))

    # 3. Bacteriology Test Report Table
    story.append(Paragraph("<b>3. BACTERIOLOGY TEST REPORT</b>", bold_cell))
    story.append(Spacer(1, 4))
    bac_data = [
        [Paragraph("<b>Sample Name</b>", bold_cell), Paragraph("<b>Total Vibrios (CFU/mL)</b>", bold_cell), Paragraph("<b>Total Coliforms / TPC (CFU/mL)</b>", bold_cell), Paragraph("<b>Luminescent Vibrios (CFU/mL)</b>", bold_cell)],
        [Paragraph(str(row.get("Sample_Source", "")), cell_style), Paragraph(str(row.get("Total_Vibrios", "")), cell_style), Paragraph(str(row.get("Total_Coliforms_TPC", "")), cell_style), Paragraph(str(row.get("Luminescent_Vibrios", "")), cell_style)]
    ]
    t_bac = Table(bac_data, colWidths=[110, 140, 150, 140])
    t_bac.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F5D65")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_bac)
    story.append(Spacer(1, 15))

    # Remarks & Signatures
    story.append(Paragraph(f"<b>Risk Status:</b> {row.get('Risk_Status', '')}", bold_cell))
    story.append(Paragraph(f"<b>Remarks:</b> {row.get('Remarks', '')}", cell_style))
    story.append(Spacer(1, 20))

    sig_data = [
        [Paragraph("<b>Tested By:</b> " + str(row.get("Technician", "")), cell_style), Paragraph("<b>Authorized Signatory:</b> Dr. Ramarajan K", cell_style)]
    ]
    t_sig = Table(sig_data, colWidths=[270, 270])
    t_sig.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(t_sig)

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- UI HEADER ---
st.markdown("<h2 style='text-align: center; color: #315F91;'>🦐 Natural Shrimp Aquaculture LLC</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #4F5D65;'>Central Lab Water Quality & Bacteriology Test Entry</h3>", unsafe_allow_html=True)
st.divider()

# Tabs Setup
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Enter Lab Test Report", 
    "📊 Live Ponds Status & Alerts", 
    "📈 Historical Trend Analysis", 
    "⚙️ Backup & PDF Report Download"
])

# ==========================================
# 1. ENTER WATER QUALITY DATA (BLANK FORM)
# ==========================================
with tab1:
    st.subheader("🧪 Central Lab Water Parameter Test Data Entry")
    st.info("ஆய்வக சோதனை முடிவுகளை (Water Quality, Plankton & Bacteriology) கீழே உள்ள கட்டங்களில் பதிவிடவும்.")
    
    with st.form("water_test_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### General Details")
            test_date = st.date_input("Testing Date", value=date.today())
            client_block = st.selectbox("Client / Block", [
                "Block 1 - Pond 1", "Block 1 - Pond 2", "Block 1 - Pond 3",
                "Block 2 - Pond 1", "Block 2 - Pond 2", "Block 2 - Pond 3",
                "Block 3 - 3J07", "Block 3 - 3K05",
                "Hatchery PLRT", "Hatchery LRT", "Hatchery Algae", "Maturation Tank", "Nursery"
            ])
            sample_name = st.text_input("Sample Name", value="")
            sample_source = st.text_input("Sample Source / Code", value="")
            technician = st.text_input("Technician Name")
            
            st.markdown("#### Plankton Observation")
            plankton_obs = st.text_input("Plankton Observed", value="")
            plankton_prev = st.number_input("Plankton Prevalence (%)", min_value=0.0, max_value=100.0, value=0.0)

        with col2:
            st.markdown("#### Chemical Parameters")
            ph = st.number_input("pH Level", min_value=0.0, max_value=14.0, value=8.0, step=0.1)
            do = st.number_input("Dissolved Oxygen - DO (mg/L)", min_value=0.0, max_value=20.0, value=6.0, step=0.1)
            alkalinity = st.number_input("Alkalinity (mg/L) [Opt: >100]", min_value=0.0, max_value=500.0, value=0.0)
            ammonia = st.number_input("TAN / Ammonical Nitrogen (mg/L) [Opt: <0.5]", min_value=0.0, max_value=5.0, value=0.0, step=0.001)
            nitrate = st.number_input("Nitrate (mg/L) [Opt: <5]", min_value=0.0, max_value=50.0, value=0.0)
            nitrite = st.number_input("Nitrite (mg/L) [Opt: <1.0]", min_value=0.0, max_value=10.0, value=0.0, step=0.001)
            phosphorus = st.number_input("Phosphorus (mg/L) [Opt: 0.5-20]", min_value=0.0, max_value=50.0, value=0.0)

        with col3:
            st.markdown("#### Physical & Bacteriology")
            tss = st.number_input("TSS (mg/L)", min_value=0.0, max_value=500.0, value=0.0)
            ec = st.number_input("Electrical Conductivity - EC (ms/cm)", min_value=0.0, max_value=100.0, value=0.0)
            tds = st.number_input("TDS (ppm)", min_value=0.0, max_value=5000.0, value=0.0)
            
            total_vibrios = st.text_input("Total Vibrios (CFU/mL)", value="")
            total_coliforms_tpc = st.text_input("Total Coliforms / TPC (CFU/mL)", value="")
            lum_vibrios = st.text_input("Luminescent Vibrios (CFU/mL)", value="Nil")
            
            remarks = st.text_input("Remarks / Observations", value="")
            
        submitted = st.form_submit_button("Save Lab Test Report", type="primary")
        
        if submitted:
            if not technician.strip():
                st.warning("தயவுசெய்து டெக்னீஷியன் பெயரை உள்ளிடவும்!")
            else:
                df = load_data()
                # Generate the next ID from existing IDs so deleted rows do not
                # cause an ID collision.
                existing_numbers = (
                    df["Record_ID"].astype(str)
                    .str.extract(r"^WQ-(\d+)$")[0]
                    .dropna()
                )
                next_number = (
                    int(existing_numbers.astype(int).max()) + 1
                    if not existing_numbers.empty else 1
                )
                new_id = f"WQ-{next_number}"
                
                # Risk Analysis Auto Logic
                risk = "Safe (Green)"
                if ammonia > 0.5 or do < 4.0 or ph < 7.0 or ph > 9.0:
                    risk = "CRITICAL DANGER (Red Alert)"
                elif ammonia > 0.1 or do < 4.5:
                    risk = "Warning (Yellow)"
                
                new_row = pd.DataFrame([{
                    "Record_ID": new_id, "Date": str(test_date), "Client_Block": client_block,
                    "Sample_Name": sample_name, "Sample_Source": sample_source, "Technician": technician,
                    "pH": ph, "DO_mgL": do, "Alkalinity": alkalinity, "Ammonia_TAN": ammonia, 
                    "Nitrate": nitrate, "Nitrite": nitrite, "Phosphorus": phosphorus, "TSS": tss, 
                    "EC": ec, "TDS": tds, "Plankton_Observed": plankton_obs, "Plankton_Prevalence": plankton_prev,
                    "Total_Vibrios": total_vibrios, "Total_Coliforms_TPC": total_coliforms_tpc, 
                    "Luminescent_Vibrios": lum_vibrios, "Risk_Status": risk, "Remarks": remarks
                }])
                
                updated_df = pd.concat([df, new_row], ignore_index=True)
                save_data(updated_df)
                st.success(f"ஆய்வக முடிவுகள் வெற்றிகரமாகச் சேமிக்கப்பட்டன! Record ID: {new_id}")

# ==========================================
# 2. LIVE PONDS STATUS & ALERTS
# ==========================================
with tab2:
    st.subheader("🚨 Live Ponds Status & Alerts")
    df = load_data()
    if df.empty:
        st.info("இதுவரை பதிவுகள் எதுவும் இல்லை.")
    else:
        def highlight_risk(val):
            if "CRITICAL" in str(val):
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            elif "Warning" in str(val):
                return 'background-color: #fff3cd; color: #856404;'
            else:
                return 'background-color: #d4edda; color: #155724;'

        styled_df = df.style.map(highlight_risk, subset=['Risk_Status'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ==========================================
# 3. HISTORICAL TREND ANALYSIS
# ==========================================
with tab3:
    st.subheader("📈 Water Parameter Trend Analysis")
    df = load_data()
    if not df.empty:
        selected_block = st.selectbox("Select Block/Pond to Analyze", df["Client_Block"].unique())
        pond_data = df[df["Client_Block"] == selected_block]
        st.dataframe(pond_data, use_container_width=True, hide_index=True)
        
        if len(pond_data) > 0:
            st.write("### Key Parameters Trend Chart")
            chart_data = pond_data.set_index("Date")[["Ammonia_TAN", "pH", "DO_mgL", "Nitrite"]]
            st.line_chart(chart_data)

# ==========================================
# 4. BACKUP & PDF REPORT DOWNLOAD
# ==========================================
with tab4:
    st.subheader("⚙️ Data Backup & Official Central Lab PDF Report")
    df = load_data()
    
    if not df.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 📄 Generate & Download Central Lab PDF Report")
            selected_record = st.selectbox("Select Record ID for PDF Download", df["Record_ID"].values)
            record_row = df[df["Record_ID"] == selected_record].iloc[0].to_dict()
            
            pdf_bytes = generate_lab_report_pdf(record_row)
            st.download_button(
                label=f"📥 Download Central Lab PDF ({selected_record})",
                data=pdf_bytes,
                file_name=f"Central_Lab_Report_{selected_record}.pdf",
                mime="application/pdf",
                type="primary"
            )

        with col_b:
            st.markdown("#### 📥 Full Database CSV Backup")
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Complete CSV Backup",
                data=csv_data,
                file_name=f"water_quality_backup_{date.today()}.csv",
                mime="text/csv"
            )
