import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def create_report():
    doc = docx.Document()

    # Base page settings
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    # Styling helper
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    def set_cell_borders(cell):
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        for b in ['top', 'left', 'bottom', 'right']:
            edge = OxmlElement(f'w:{b}')
            edge.set(qn('w:val'), 'single')
            edge.set(qn('w:sz'), '4')
            edge.set(qn('w:space'), '0')
            edge.set(qn('w:color'), '000000')
            tcBorders.append(edge)
        tcPr.append(tcBorders)

    def set_cell_shading(cell, color_hex="F2F2F2"):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), color_hex)
        tcPr.append(shd)

    def set_cell_padding(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for margin, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{margin}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def add_page_number(run):
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar')
        fldChar3.set(qn('w:fldCharType'), 'end')
        r = run._r
        r.append(fldChar1)
        r.append(instrText)
        r.append(fldChar2)
        r.append(fldChar3)

    def p_text(text, bold=False, italic=False, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.15):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.size = Pt(size)
        run.font.name = 'Times New Roman'
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(14)
        run.font.name = 'Times New Roman'
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        run.bold = True
        run.italic = True
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
        return p

    def add_fig_image(img_path, caption_text, width_inches=6.0):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(img_path, width=Inches(width_inches))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(10)
            run = p_cap.add_run(caption_text)
            run.font.size = Pt(10.5)
            run.font.name = 'Times New Roman'
            run.font.italic = True
        else:
            print(f"Warning: Image path not found: {img_path}")

    # ==========================================
    # 1. COVER PAGE
    # ==========================================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(18)
    run_t = p_title.add_run("DEEP LEARNING-BASED ELECTRIC VEHICLE BATTERY HEALTH AND REMAINING USEFUL LIFE PREDICTION WITH EXPLAINABLE AI AND COUNTERFACTUAL WHAT-IF RECOMMENDER")
    run_t.bold = True
    run_t.font.size = Pt(15)
    run_t.font.name = 'Times New Roman'

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(12)
    p_sub.paragraph_format.space_after = Pt(2)
    r = p_sub.add_run("CASE STUDY REPORT")
    r.bold = True
    r.font.size = Pt(14)
    r.font.name = 'Times New Roman'

    p_sub2 = doc.add_paragraph()
    p_sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub2.paragraph_format.space_before = Pt(2)
    p_sub2.paragraph_format.space_after = Pt(2)
    r = p_sub2.add_run("for")
    r.font.size = Pt(12)
    r.font.name = 'Times New Roman'

    p_sub3 = doc.add_paragraph()
    p_sub3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub3.paragraph_format.space_before = Pt(2)
    p_sub3.paragraph_format.space_after = Pt(18)
    r = p_sub3.add_run("21CSC406J – NEURAL NETWORKS AND DEEP LEARNING")
    r.bold = True
    r.font.size = Pt(13)
    r.font.name = 'Times New Roman'

    p_sub4 = doc.add_paragraph()
    p_sub4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub4.paragraph_format.space_before = Pt(12)
    p_sub4.paragraph_format.space_after = Pt(6)
    r = p_sub4.add_run("Submitted by")
    r.bold = True
    r.font.size = Pt(12)
    r.font.name = 'Times New Roman'

    students = [
        "B S VIKASH SRIKANTH [RA2311026010583]",
        "S RAVI PRAKASH [RA2311026010591]",
        "A GRIFFIN GEORGE [RA2311026010585]"
    ]
    for s in students:
        p_st = doc.add_paragraph()
        p_st.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_st.paragraph_format.space_before = Pt(0)
        p_st.paragraph_format.space_after = Pt(2)
        r = p_st.add_run(s)
        r.bold = True
        r.font.size = Pt(12)
        r.font.name = 'Times New Roman'

    p_req = doc.add_paragraph()
    p_req.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_req.paragraph_format.space_before = Pt(18)
    p_req.paragraph_format.space_after = Pt(4)
    r = p_req.add_run("In partial fulfilment of the requirements for the degree of")
    r.font.size = Pt(11)
    r.font.name = 'Times New Roman'

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(2)
    p_deg.paragraph_format.space_after = Pt(14)
    r1 = p_deg.add_run("BACHELOR OF TECHNOLOGY\nin\n")
    r1.bold = True
    r1.font.size = Pt(12)
    r2 = p_deg.add_run("COMPUTER SCIENCE AND ENGINEERING\n")
    r2.bold = True
    r2.font.size = Pt(12)
    r3 = p_deg.add_run("with specialization in ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING")
    r3.bold = True
    r3.font.size = Pt(11)

    # University Logo
    logo_path = r"Z:\Games\ev battery project\srm_logo_extracted.png"
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(10)
        p_logo.paragraph_format.space_after = Pt(12)
        p_logo.add_run().add_picture(logo_path, width=Inches(2.45))

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(4)
    p_dept.paragraph_format.space_after = Pt(2)
    r = p_dept.add_run("DEPARTMENT OF COMPUTATIONAL INTELLIGENCE\nCOLLEGE OF ENGINEERING AND TECHNOLOGY\nSRM INSTITUTE OF SCIENCE AND TECHNOLOGY\nKATTANKULATHUR – 603 203")
    r.bold = True
    r.font.size = Pt(11)
    r.font.name = 'Times New Roman'

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(14)
    p_date.paragraph_format.space_after = Pt(0)
    r = p_date.add_run("NOVEMBER 2026")
    r.bold = True
    r.font.size = Pt(12)
    r.font.name = 'Times New Roman'

    doc.add_page_break()

    # ==========================================
    # 2. BONAFIDE CERTIFICATE
    # ==========================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(10)
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY")
    r.bold = True
    r.font.size = Pt(14)
    r.font.name = 'Times New Roman'

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.space_before = Pt(0)
    p_loc.paragraph_format.space_after = Pt(14)
    r = p_loc.add_run("KATTANKULATHUR – 603 203")
    r.bold = True
    r.font.size = Pt(12)
    r.font.name = 'Times New Roman'

    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(10)
    p_cert.paragraph_format.space_after = Pt(18)
    r = p_cert.add_run("BONAFIDE CERTIFICATE")
    r.bold = True
    r.font.size = Pt(16)
    r.font.name = 'Times New Roman'

    cert_text1 = (
        "This is to certify that the Case Study Report titled \"DEEP LEARNING-BASED ELECTRIC VEHICLE "
        "BATTERY HEALTH AND REMAINING USEFUL LIFE PREDICTION WITH EXPLAINABLE AI AND COUNTERFACTUAL WHAT-IF RECOMMENDER\" "
        "is a bonafide record of work carried out by the following student(s) as part of the course "
        "21CSC406J – NEURAL NETWORKS AND DEEP LEARNING, during the academic year 2026–2027 Odd Semester."
    )
    p_text(cert_text1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=10, line_spacing=1.3)

    cert_text2 = (
        "This report has been submitted in partial fulfilment of the requirements for the successful "
        "completion of the course and has not been submitted elsewhere for any academic or non-academic purpose."
    )
    p_text(cert_text2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=10, line_spacing=1.3)

    cert_text3 = "The work is found to be satisfactory and is hereby accepted."
    p_text(cert_text3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=14, line_spacing=1.3)

    p_subby = doc.add_paragraph()
    p_subby.paragraph_format.space_after = Pt(6)
    r = p_subby.add_run("Submitted by:")
    r.bold = True
    r.font.size = Pt(12)

    # Student Table
    t_students = doc.add_table(rows=4, cols=2)
    t_students.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Register Number", "Name of Student(s)"]
    for j, h in enumerate(headers):
        c = t_students.cell(0, j)
        c.text = h
        c.paragraphs[0].runs[0].bold = True
        c.paragraphs[0].runs[0].font.name = 'Times New Roman'
        c.paragraphs[0].runs[0].font.size = Pt(11)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_borders(c)
        set_cell_shading(c, "EAEAEA")
        set_cell_padding(c, 100, 100, 150, 150)

    st_data = [
        ("RA2311026010583", "B S VIKASH SRIKANTH"),
        ("RA2311026010591", "S RAVI PRAKASH"),
        ("RA2311026010585", "A GRIFFIN GEORGE")
    ]
    for i, (reg, name) in enumerate(st_data):
        c0 = t_students.cell(i+1, 0)
        c1 = t_students.cell(i+1, 1)
        c0.text = reg
        c1.text = name
        for cell in [c0, c1]:
            cell.paragraphs[0].runs[0].font.name = 'Times New Roman'
            cell.paragraphs[0].runs[0].font.size = Pt(11)
            set_cell_borders(cell)
            set_cell_padding(cell, 80, 80, 120, 120)
        c0.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

    t_students.columns[0].width = Inches(2.5)
    t_students.columns[1].width = Inches(3.8)

    p_dt = doc.add_paragraph()
    p_dt.paragraph_format.space_before = Pt(16)
    p_dt.paragraph_format.space_after = Pt(28)
    r = p_dt.add_run("Date of Submission: November 2026")
    r.font.size = Pt(12)
    r.font.name = 'Times New Roman'

    # Signature Block Table
    t_sig = doc.add_table(rows=1, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_sig0 = t_sig.cell(0, 0)
    c_sig1 = t_sig.cell(0, 1)

    c_sig0.text = "\n\n___________________________________\nDr. Uma E\nSupervisor, Assistant Professor\nDepartment of Computational Intelligence\nSRMIST, Kattankulathur"
    c_sig1.text = "\n\n___________________________________\nDr. R. Annie Uthra\nProfessor & Head\nDepartment of Computational Intelligence\nSRMIST, Kattankulathur"

    for c in [c_sig0, c_sig1]:
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.bold = True
        set_cell_padding(c, 100, 100, 100, 100)

    t_sig.columns[0].width = Inches(3.2)
    t_sig.columns[1].width = Inches(3.2)

    doc.add_page_break()

    # ==========================================
    # 3. ABSTRACT
    # ==========================================
    add_h1("ABSTRACT")
    abstract_p1 = (
        "Electric Vehicle (EV) battery packs are subject to progressive and nonlinear electro-chemical degradation "
        "governed by cyclic charging, C-rate stress, cell temperature variations, depth-of-discharge, and deep-discharge "
        "voltage events. Accurate joint estimation of State of Health (SOH) and Remaining Useful Life (RUL) is mission-critical "
        "for guaranteeing passenger safety, mitigating catastrophic thermal runaway risks, optimizing dynamic Battery "
        "Management System (BMS) operations, and improving second-life battery economic valuation [13], [14]. Conventional "
        "equivalent circuit models (ECM) and empirical electrochemical approaches fail under dynamic multi-cell cross-chemistry "
        "operating environments due to rigid parametric assumptions and sensitivity to noisy telemetry [13]."
    )
    p_text(abstract_p1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8, line_spacing=1.2)

    abstract_p2 = (
        "This case study presents an end-to-end deep learning framework based on a Multi-Task Gated Recurrent Unit (GRU) [7] "
        "augmented with Temporal Bahdanau-style Self-Attention [6] and physics-grounded electro-thermal stress engineering [2], [12]. "
        "The model is systematically trained and cross-evaluated across 5,031 real-world electrochemical cycling profiles "
        "drawn from three benchmark lithium-ion datasets: NASA Prognostics Center of Excellence (PCoE 18650 LiCoO2 cells) [3], "
        "the University of Maryland CALCE Battery Research Group (CS2 pouch cells) [4], and the Oxford University Battery Degradation "
        "Suite (Kokam NMC/LCO pouch cells) [5]. To resolve the opaque 'black-box' nature of deep recurrent networks in automotive "
        "safety certifications, the framework incorporates an Explainable AI (XAI) feature attribution engine [9] alongside "
        "an interactive Counterfactual 'What-If' BMS Prescription Recommender [10]. The counterfactual engine projects how dynamic "
        "adjustments in thermal derating, peak charge C-rate limiting, and discharge cutoff optimization tangibly slow capacity "
        "fade and extend residual pack longevity [10], [13]. Experimental results demonstrate that the proposed GRU + Temporal Attention "
        "architecture achieves state-of-the-art predictive performance, registering an SOH Mean Absolute Error (MAE) of 0.81%, "
        "Root Mean Squared Error (RMSE) of 1.28%, R2 of 0.984, and an RUL prediction error within 4.2 cycles, decisively "
        "outperforming baseline MLP, 1D-CNN [1], and standard bidirectional LSTM architectures [8]."
    )
    p_text(abstract_p2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=12, line_spacing=1.2)

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(6)
    p_kw.paragraph_format.space_after = Pt(12)
    r_kwh = p_kw.add_run("Keywords: ")
    r_kwh.bold = True
    r_kwh.font.size = Pt(11)
    r_kwb = p_kw.add_run("Electric Vehicle Battery, State of Health (SOH), Remaining Useful Life (RUL), Gated Recurrent Unit (GRU), Temporal Attention, Physics-Grounded Degradation, Explainable AI (XAI), Counterfactual Optimization, Battery Management System (BMS).")
    r_kwb.italic = True
    r_kwb.font.size = Pt(11)

    doc.add_page_break()

    # ==========================================
    # 4. TABLE OF CONTENTS
    # ==========================================
    add_h1("TABLE OF CONTENTS")
    t_toc = doc.add_table(rows=8, cols=3)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_data = [
        ("CHAPTER NO", "TITLE", "Page No"),
        ("1", "INTRODUCTION", "1"),
        ("2", "THEORETICAL FOUNDATION: CNN, TRANSFER LEARNING, ATTENTION & GANs", "3"),
        ("3", "CASE ANALYSIS & IMPLEMENTATION", "7"),
        ("4", "PROPOSED IMPROVEMENTS / OPTIMIZATION STRATEGIES", "14"),
        ("5", "CONCLUSION AND FUTURE WORK", "17"),
        ("", "REFERENCES", "18"),
        ("", "APPENDICES", "20")
    ]
    for i, row in enumerate(toc_data):
        for j, val in enumerate(row):
            c = t_toc.cell(i, j)
            c.text = val
            p = c.paragraphs[0]
            if i == 0:
                p.runs[0].bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_cell_shading(c, "EAEAEA")
            else:
                if j == 1:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(11)
            set_cell_borders(c)
            set_cell_padding(c, 80, 80, 100, 100)

    t_toc.columns[0].width = Inches(1.3)
    t_toc.columns[1].width = Inches(4.3)
    t_toc.columns[2].width = Inches(1.0)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(14)

    # ==========================================
    # 5. LIST OF FIGURES
    # ==========================================
    add_h1("LIST OF FIGURES")
    lof_data = [
        ("FIG. NO", "FIGURE TITLE", "Page No"),
        ("2.1", "Recurrent Neural Network and Gated Recurrent Unit (GRU) Gating Structure", "4"),
        ("2.2", "Bahdanau Temporal Self-Attention Mechanism for Degradation Dynamics", "5"),
        ("3.1", "BatteryAI Intelligent EV Battery Health Analytics Platform Welcome Interface", "8"),
        ("3.2", "Multi-Dataset SOH Degradation Fade Trajectories (NASA, others)", "9"),
        ("3.3", "End-to-End Multi-Task GRU with Temporal Attention Architecture Flow", "10"),
        ("3.4", "Live Forecaster Telemetry, SOH Degradation Curve, and Real-Time State KPIs", "12"),
        ("3.5", "Anomaly Mode Active: Sudden Capacity Drop (-40%) and Severe EOL Alerting", "13"),
        ("3.6", "Model Performance Comparison: Ablation Benchmark Across Deep Architectures", "14"),
        ("4.1", "Explainable AI (XAI) Degradation Driver Attribution and Prescription Insights", "15"),
        ("4.2", "Interactive Counterfactual 'What-If' BMS Dynamic Control Simulation Interface", "16")
    ]
    t_lof = doc.add_table(rows=len(lof_data), cols=3)
    t_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(lof_data):
        for j, val in enumerate(row):
            c = t_lof.cell(i, j)
            c.text = val
            p = c.paragraphs[0]
            if i == 0:
                p.runs[0].bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_cell_shading(c, "EAEAEA")
            else:
                if j == 1:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(10.5)
            set_cell_borders(c)
            set_cell_padding(c, 70, 70, 90, 90)

    t_lof.columns[0].width = Inches(1.1)
    t_lof.columns[1].width = Inches(4.5)
    t_lof.columns[2].width = Inches(1.0)

    p_space2 = doc.add_paragraph()
    p_space2.paragraph_format.space_before = Pt(14)

    # ==========================================
    # 6. LIST OF TABLES
    # ==========================================
    add_h1("LIST OF TABLES")
    lot_data = [
        ("TABLE NO", "TABLE TITLE", "Page No"),
        ("3.1", "Summary Description of Lithium-Ion Battery Datasets (NASA, CALCE, Oxford)", "8"),
        ("3.2", "Engineered Physics-Grounded Degradation Stress Features", "9"),
        ("3.3", "Ablation Performance Comparison Across Deep Learning Architectures", "13")
    ]
    t_lot = doc.add_table(rows=len(lot_data), cols=3)
    t_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(lot_data):
        for j, val in enumerate(row):
            c = t_lot.cell(i, j)
            c.text = val
            p = c.paragraphs[0]
            if i == 0:
                p.runs[0].bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_cell_shading(c, "EAEAEA")
            else:
                if j == 1:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(10.5)
            set_cell_borders(c)
            set_cell_padding(c, 70, 70, 90, 90)

    t_lot.columns[0].width = Inches(1.1)
    t_lot.columns[1].width = Inches(4.5)
    t_lot.columns[2].width = Inches(1.0)

    # Add section break for main body with page numbering
    body_section = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    body_section.top_margin = Inches(1.0)
    body_section.bottom_margin = Inches(1.0)
    body_section.left_margin = Inches(1.0)
    body_section.right_margin = Inches(1.0)

    # Add page number in footer of main body
    footer_p = body_section.footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_fn = footer_p.add_run()
    run_fn.font.name = 'Times New Roman'
    run_fn.font.size = Pt(11)
    add_page_number(run_fn)

    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    add_h1("CHAPTER 1\nINTRODUCTION")

    add_h2("1.1 Background")
    p_text(
        "The global automotive paradigm is undergoing an unprecedented transition from internal combustion engine (ICE) "
        "vehicles toward electrified mobility powered by rechargeable Lithium-Ion Batteries (LIB) [14]. LIB systems, particularly "
        "those incorporating Lithium Cobalt Oxide (LiCoO2), Lithium Nickel Manganese Cobalt Oxide (LiNiMnCoO2 or NMC), and "
        "Lithium Iron Phosphate (LiFePO4 or LFP) chemistries, represent the undisputed standard for modern Electric Vehicles "
        "(EVs) due to their superior gravimetric energy density, high discharge power capability, low self-discharge rates, "
        "and long operational lifespans [13], [14]. However, the performance and reliability of EV battery packs continuously deteriorate "
        "over operational life due to irreversible parasitic electrochemical and mechanical processes [2]. These degradation mechanisms "
        "include Solid Electrolyte Interphase (SEI) layer growth, lithium plating at high charge C-rates, transition metal dissolution, "
        "active electrode material crack formation, and loss of cyclable lithium inventory (LLI) [2], [13]."
    )
    p_text(
        "Within an operating vehicle, the battery system is monitored by an embedded electronic Battery Management System (BMS) [13], [14]. "
        "The BMS is responsible for tracking two vital health indices: State of Health (SOH) and Remaining Useful Life (RUL) [8], [13]. "
        "State of Health quantifies the current available discharge capacity of the battery relative to its factory-rated nominal "
        "capacity, expressed mathematically as:"
    )
    p_text("SOH(k) = ( Q_actual(k) / Q_nominal ) × 100 %", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=6)
    p_text(
        "where Q_actual(k) denotes the maximum extractable charge capacity at cycle k, and Q_nominal denotes the pristine nominal capacity. "
        "An EV battery is widely recognized to reach its End-of-Life (EOL) threshold for primary automotive propulsion when its SOH degrades "
        "below 80% (or in certain duty cycles, 70%), beyond which acceleration sluggishness, severe driving range reduction, and internal "
        "resistance heating pose severe operational hazards [8], [13]. Remaining Useful Life (RUL) projects the exact remaining cycle count or operating "
        "time until the cell reaches this EOL boundary:"
    )
    p_text("RUL(k) = k_EOL - k", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=6)
    p_text(
        "Accurate, multi-step prospective estimation of both SOH and RUL is pivotal for predictive thermal management, dynamic charging "
        "rate modulation, preventive maintenance scheduling, warranty liability forecasting, and second-life battery grid storage grading [2], [13]."
    )

    add_h2("1.2 Problem Statement")
    p_text(
        "Despite significant industrial demand, real-time SOH tracking and RUL trajectory forecasting remain formidable engineering challenges "
        "due to several intrinsic factors:"
    )
    bullet_points_prob = [
        ("Extreme Nonlinearity and Knee-Point Phenomenon: ", "Battery degradation does not proceed along a simple linear curve. Instead, cells exhibit complex multi-phase trajectories characterized by gradual capacity fade followed by a sharp accelerated aging transition ('knee point'), where degradation velocity abruptly triples [2]."),
        ("Dynamic Operating Noise and Capacity Regeneration: ", "Real-world driving profiles induce irregular charge/discharge rates, ambient temperature shifts, and prolonged rest periods that trigger transient electrochemical relaxation phenomena, leading to artificial capacity recovery spikes that fool simplistic filtering algorithms [8], [12]."),
        ("Limitations of Empirical Equivalent Circuit Models (ECM): ", "Traditional approaches rely on Kalman Filters (EKF/UKF) coupled with equivalent resistance-capacitance circuits [13]. These models require exhaustive offline parameter identification, fail to generalize across differing battery cell chemistries (e.g., LCO vs. NMC pouch cells), and cannot capture high-order temporal degradation dynamics under varied thermal stresses [13], [14]."),
        ("The 'Black-Box' Interpretability Barrier: ", "While recent deep learning models achieve impressive curve fitting, standard recurrent neural networks offer zero explanatory transparency into which physical stress variables (C-rate, voltage extremes, thermal strain) are accelerating degradation [1], [8]. In safety-critical automotive environments, engineering teams and regulatory bodies demand explainable diagnostics and actionable mitigation strategies [9], [10].")
    ]
    for title, desc in bullet_points_prob:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r_t = p.add_run("•  " + title)
        r_t.bold = True
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)
        r_d = p.add_run(desc)
        r_d.font.name = 'Times New Roman'
        r_d.font.size = Pt(11)

    add_h2("1.3 Objectives")
    p_text(
        "To decisively address the aforementioned challenges, this case study formulates and implements a production-ready, "
        "interpretable deep learning framework for lithium-ion battery health diagnostics. The specific objectives of this study are:"
    )
    objectives = [
        "To develop an end-to-end data preprocessing and physics-stress engineering pipeline across heterogeneous public battery aging datasets (NASA PCoE [3], CALCE [4], and Oxford University [5]).",
        "To design and train a Multi-Task Gated Recurrent Unit (GRU) [7] network augmented with a Temporal Self-Attention mechanism [6] that concurrently estimates continuous SOH percentage and forecasts RUL cycle boundaries [8].",
        "To benchmark the proposed GRU + Attention model against standard deep learning architectures (MLP, 1D-CNN, Bidirectional LSTM) across rigorous statistical metrics (MAE, RMSE, MAPE, R2) [1], [8].",
        "To implement a real-time Anomaly Simulation and Detection engine capable of modeling abrupt capacity drops (-40% capacity collapse) and alerting BMS supervisors to critical EOL boundary breaches [13].",
        "To integrate an Explainable AI (XAI) feature attribution module [9] coupled with an interactive Counterfactual 'What-If' BMS Recommender [10], providing actionable operating prescriptions (thermal derating, fast-charge current caps, cutoff voltage limits) to maximize pack longevity [13].",
        "To deploy the comprehensive framework as a modern, interactive Streamlit-based enterprise engineering dashboard ('BatteryAI') supporting multi-dataset inspection, automated diagnostic narratives, and downloadable PDF/Excel reporting."
    ]
    for i, obj in enumerate(objectives):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(f"1.3.{i+1}  {obj}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)

    doc.add_page_break()

    # ==========================================
    # CHAPTER 2: THEORETICAL FOUNDATION
    # ==========================================
    add_h1("CHAPTER 2\nTHEORETICAL FOUNDATION: CNN, TRANSFER LEARNING, ATTENTION & RECURRENT NETWORKS")

    add_h2("2.1 Convolutional Neural Networks (CNN) in Time-Series Telemetry")
    p_text(
        "Convolutional Neural Networks (CNNs), originally pioneered for spatial feature extraction in computer vision [1], have "
        "demonstrated high utility for raw sensory time-series analysis in cyber-physical systems. In battery degradation modeling, "
        "a 1D-CNN slides one-dimensional parameterized convolutional kernels across temporal sequences of voltage, current, "
        "and temperature measurements to capture localized morphological patterns, such as the peak position of incremental capacity "
        "curves or the inflection slope of constant-current charging phases [12]."
    )
    p_text("𝑐𝑖 = 𝑠𝑖𝑔𝑚𝑎( 𝑆𝑢𝑚𝑗₌₀𝐾⁻¹ 𝑊𝑗 · 𝑥𝑖₊𝑗 + 𝑏 )", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=6)
    p_text(
        "where sigma represents a non-linear activation function such as ReLU, and K is the kernel temporal width [1]. While 1D-CNNs exhibit high "
        "computational throughput and parallelizability during training, standard convolutional architectures are intrinsically constrained "
        "by their finite receptive field, making it difficult to capture long-range electrochemical aging dependencies spanning hundreds of "
        "successive driving and charging cycles [1], [8]."
    )

    add_h2("2.2 Recurrent Neural Networks and Gated Recurrent Units (GRU)")
    p_text(
        "To model long-term sequential dependencies, Recurrent Neural Networks (RNNs) maintain an internal hidden state vector that recursively "
        "propagates information across time steps [1]. However, standard RNNs suffer from vanishing and exploding gradient phenomena when trained "
        "via Backpropagation Through Time (BPTT) over extended cycle horizons [1]. The Long Short-Term Memory (LSTM) [8] and Gated Recurrent Unit "
        "(GRU) [7] architectures mitigate this limitation by introducing internal gating mechanisms that regulate information retention and erasure."
    )
    p_text(
        "In this research, the Gated Recurrent Unit (GRU) [7] is chosen as the primary recurrent backbone over standard LSTM [8] due to its "
        "streamlined architecture, lower computational complexity, and superior convergence speed on moderate-sized time-series sets. Unlike "
        "the three-gate LSTM with separate cell state, the GRU merges the cell state and hidden state, controlling temporal flow using only "
        "two gating vectors: The Update Gate and the Reset Gate [7]. The governing state equations are defined as:"
    )
    p_text("𝑈𝑝𝑑𝑎𝑡𝑒 𝐺𝑎𝑡𝑒: 𝑧ₜ = 𝑠𝑖𝑔𝑚𝑎( 𝑊𝑧 · 𝑥ₜ + 𝑈𝑧 · ℎₜ₋₁ + 𝑏𝑧 )", bold=True, space_before=2, space_after=2)
    p_text("𝑅𝑒𝑠𝑒𝑡 𝐺𝑎𝑡𝑒: 𝑟ₜ = 𝑠𝑖𝑔𝑚𝑎( 𝑊𝑟 · 𝑥ₜ + 𝑈𝑟 · ℎₜ₋₁ + 𝑏𝑟 )", bold=True, space_before=2, space_after=2)
    p_text("𝐶𝑎𝑛𝑑𝑖𝑑𝑎𝑡𝑒 𝑆𝑡𝑎𝑡𝑒: ℎ~ₜ = 𝑡𝑎𝑛ℎ( 𝑊ₕ · 𝑥ₜ + 𝑈ₕ · (𝑟ₜ ⊙ ℎₜ₋₁) + 𝑏ₕ )", bold=True, space_before=2, space_after=2)
    p_text("𝐻𝑖𝑑𝑑𝑒𝑛 𝑈𝑝𝑑𝑎𝑡𝑒: ℎₜ = (1 - 𝑧ₜ) ⊙ ℎₜ₋₁ + 𝑧ₜ ⊙ ℎ~ₜ", bold=True, space_before=2, space_after=6)
    p_text(
        "where ⊙ denotes the element-wise Hadamard product, and sigma denotes the sigmoid function [1], [7]. The update gate determines the exact "
        "proportion of past historical degradation memory to preserve versus novel electrochemical information to incorporate, enabling robust "
        "tracking of gradual capacity fade while resisting transient measurement perturbations [7], [8]."
    )

    add_h2("2.3 Temporal Attention Mechanism")
    p_text(
        "Although GRUs preserve sequential memory better than standard RNNs, information stored across extensive horizons (e.g., 200+ cycles) "
        "tends to suffer from gradual attenuation [7]. Furthermore, in battery lifetime analysis, not all historical cycles exert equal influence "
        "over instantaneous degradation; cycles exhibiting severe thermal spikes or deep over-discharge carry disproportionate diagnostic "
        "significance [2]. To dynamically prioritize critical historical events, we incorporate a Bahdanau-inspired Temporal Attention Mechanism [6] "
        "directly atop the GRU hidden representations."
    )
    p_text(
        "Given the sequence of hidden vectors emitted by the GRU layer, the attention mechanism computes a normalized scalar alignment score "
        "for each temporal step using a learned feedforward scoring function [6]:"
    )
    p_text("𝑒ₜ = 𝑣ₐ𝑇 · 𝑡𝑎𝑛ℎ( 𝑊ₐ · ℎₜ + 𝑏ₐ )", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
    p_text("𝑎𝑙𝑝ℎ𝑎ₜ = 𝑒𝑥𝑝(𝑒ₜ) / 𝑆𝑢𝑚ₖ₌₁𝑇 𝑒𝑥𝑝(𝑒ₖ)", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4)
    p_text(
        "The computed attention distribution reflects the relative importance of cycle t [6]. A composite context vector c is then synthesized via "
        "a weighted summation of all hidden representations:"
    )
    p_text("𝑐 = 𝑆𝑢𝑚ₜ₌₁𝑇 𝑎𝑙𝑝ℎ𝑎ₜ · ℎₜ", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=6)
    p_text(
        "This context vector c captures both short-term stress dynamics and macroscopic aging trends, serving as the rich feature "
        "representation supplied to the multi-task prediction heads [6]. To dynamically prioritize critical historical events, we incorporate "
        "a Bahdanau-inspired Temporal Attention Mechanism directly atop the GRU hidden representations [6], [7]."
    )

    add_h2("2.4 Transfer Learning & Domain Generalization in Battery Systems")
    p_text(
        "A critical limitation in automotive battery AI is the domain shift arising from differing cell form factors (cylindrical 18650 vs. "
        "prismatic vs. polymer pouch), distinct cathode active materials (LiCoO2 vs. NMC vs. LFP), and varying ambient thermal chambers [11], [13]. "
        "Transfer learning provides a principled paradigm to train a deep recurrent feature backbone on rich laboratory benchmark datasets "
        "(e.g., NASA PCoE [3]) and transfer learned degradation representations to cross-chemistry target datasets (e.g., CALCE [4] and Oxford [5]) "
        "with fine-tuning of terminal dense layers [11]. This dramatically minimizes training convergence time and eliminates the requirement "
        "to cycle novel cell chemistries to destruction over multi-year laboratory tests [11]."
    )

    add_h2("2.5 Explainable AI (XAI) and Generative Counterfactual Prescriptions")
    p_text(
        "While deep neural networks achieve superior empirical accuracy, automotive safety standards (such as ISO 26262) mandate transparency "
        "and verification [13]. Explainable AI (XAI) bridges this divide [9]. In our framework, gradient-weighted and perturbation-based sensitivity "
        "methods are deployed to quantify the exact marginal contribution of individual physical telemetry variables (temperature, C-rate, "
        "discharge cutoff voltage) to the predicted SOH and RUL [9]."
    )
    p_text(
        "Furthermore, we extend diagnostics into prescriptive generative intervention via Counterfactual 'What-If' Simulation [10]. A counterfactual "
        "query explores: 'What would the battery's projected lifetime trajectory be if operating parameters were altered to a safer regime?' [10] "
        "By perturbing input stress vectors x under defined operational constraints (e.g., enforcing cell temperature T <= 32°C and limiting "
        "charge rate to 0.75C), the model computes the counterfactual health trajectory SOH_cf(t) and quantifies the exact lifetime extension "
        "in additional cycles, transforming passive monitoring into active supervisory BMS control [10], [13]."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 3: CASE ANALYSIS & IMPLEMENTATION
    # ==========================================
    add_h1("CHAPTER 3\nCASE ANALYSIS & IMPLEMENTATION")

    add_h2("3.1 Case Description and Benchmark Datasets")
    p_text(
        "To guarantee experimental rigor, robustness, and chemistry-agnostic generalization, the proposed framework was developed and "
        "evaluated across three globally recognized lithium-ion battery degradation repositories, encompassing 5,031 full charge-discharge "
        "cycles under varied operating conditions: NASA Prognostics Center of Excellence (PCoE) [3], CALCE Battery Research Group at the "
        "University of Maryland [4], and the Oxford University Battery Degradation Suite [5]:"
    )

    # Table 3.1
    p_lot_cap = doc.add_paragraph()
    p_lot_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot_cap.paragraph_format.space_before = Pt(6)
    p_lot_cap.paragraph_format.space_after = Pt(4)
    r = p_lot_cap.add_run("Table 3.1: Summary Description of Lithium-Ion Battery Datasets")
    r.bold = True
    r.font.size = Pt(11)

    t_dsets = doc.add_table(rows=4, cols=6)
    t_dsets.alignment = WD_TABLE_ALIGNMENT.CENTER
    dset_data = [
        ["Dataset", "Cell ID", "Form Factor / Chemistry", "Nominal Cap.", "Operating Conditions", "Total Cycles"],
        ["NASA PCoE [3]", "B0005, B0006, B0007, B0018", "18650 Cylindrical / LiCoO2", "2.0 Ah", "24°C room temp, 2.0A discharge, 4.2V CC-CV", "616"],
        ["CALCE Univ. [4]", "CS2_16, CS2_35, CS2_36, CS2_37", "Pouch Cell / LiCoO2", "1.1 Ah", "Dynamic C-rates (0.5C to 2C), partial cycles", "3,595"],
        ["Oxford Univ. [5]", "Cell 1 to Cell 8 (Kokam)", "Pouch Cell / NMC & LCO", "0.74 Ah", "40°C thermal chamber, dynamic drive profiles", "820"]
    ]
    for i, row in enumerate(dset_data):
        for j, val in enumerate(row):
            c = t_dsets.cell(i, j)
            c.text = val
            p = c.paragraphs[0]
            if i == 0:
                p.runs[0].bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_cell_shading(c, "EAEAEA")
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j in [1, 2, 4] else WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(9.5)
            set_cell_borders(c)
            set_cell_padding(c, 60, 60, 80, 80)

    t_dsets.columns[0].width = Inches(1.1)
    t_dsets.columns[1].width = Inches(1.2)
    t_dsets.columns[2].width = Inches(1.4)
    t_dsets.columns[3].width = Inches(0.8)
    t_dsets.columns[4].width = Inches(1.3)
    t_dsets.columns[5].width = Inches(0.7)

    p_text(
        "Figure 3.1 displays the landing dashboard of the developed BatteryAI analytics suite, welcoming users with architectural "
        "capabilities before cell-level telemetry is ingested."
    )
    add_fig_image(
        r"Z:\Games\ev battery project\screenshot\Screenshot 2026-11-09 121707.png",
        "Fig. 3.1: BatteryAI Intelligent EV Battery Health Analytics Platform Welcome Interface"
    )

    add_h2("3.2 Physics-Grounded Degradation Feature Engineering")
    p_text(
        "Directly feeding raw, noisy telemetry (e.g. unconditioned point-by-point voltage sampling) into recurrent networks often leads "
        "to overfitting and poor generalization [12]. In this work, domain knowledge of lithium-ion degradation kinetics was leveraged to construct "
        "eight high-order physical stress features extracted from each charging and discharging cycle [2], [12]:"
    )

    # Table 3.2
    p_tab_cap2 = doc.add_paragraph()
    p_tab_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab_cap2.paragraph_format.space_before = Pt(6)
    p_tab_cap2.paragraph_format.space_after = Pt(4)
    r = p_tab_cap2.add_run("Table 3.2: Engineered Physics-Grounded Degradation Stress Features")
    r.bold = True
    r.font.size = Pt(11)

    t_feats = doc.add_table(rows=7, cols=3)
    t_feats.alignment = WD_TABLE_ALIGNMENT.CENTER
    feat_data = [
        ["Feature Name", "Physical Formulation / Metric", "Electrochemical Aging Significance"],
        ["Voltage Drop Duration", "𝐷𝑒𝑙𝑡𝑎 𝑡𝑉ₘₐₓ ₋> 𝑉ₘ𝑖ₙ", "Directly reflects rising internal cell impedance and ohmic overpotential [12]."],
        ["Charge Duration Ratio", "𝑡𝐶𝐶 / (𝑡𝐶𝐶 + 𝑡𝐶𝑉)", "Shrinking Constant-Current phase indicates loss of active electrode material [12]."],
        ["Peak Cell Temperature", "𝑇ₘₐₓ (°𝐶)", "Accelerates SEI decomposition and irreversible electrolyte consumption above 35°C [2], [13]."],
        ["Deep Discharge Flag", "𝐼(𝑉ₘ𝑖ₙ < 3.0𝑉)", "Captures copper dissolution and negative electrode structural damage [13]."],
        ["Effective C-Rate", "𝐼𝑑𝑖ₛ𝑐ₕₐ𝑟𝑔ₑ / 𝑄ₙₒₘ𝑖ₙₐₗ", "Higher discharge rates induce mechanical lattice strain and lithium concentration gradients [2]."],
        ["Thermal Degradation Stress", "𝐼𝑛𝑡𝑒𝑔𝑟𝑎𝑙 (𝑇 - 𝑇𝑟ₑ𝑓) 𝑑𝑡", "Cumulative thermal stress indicator quantifying Arrhenius degradation acceleration [2], [13]."]
    ]
    for i, row in enumerate(feat_data):
        for j, val in enumerate(row):
            c = t_feats.cell(i, j)
            c.text = val
            p = c.paragraphs[0]
            if i == 0:
                p.runs[0].bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_cell_shading(c, "EAEAEA")
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(9.5)
            set_cell_borders(c)
            set_cell_padding(c, 60, 60, 80, 80)

    t_feats.columns[0].width = Inches(1.8)
    t_feats.columns[1].width = Inches(2.0)
    t_feats.columns[2].width = Inches(2.7)

    p_text(
        "These features are extracted from charging and discharging data to identify the physical factors that contribute to battery degradation [12]. "
        "Voltage Drop Duration measures the time taken for voltage to decrease from its maximum to minimum value, helping identify an increase in internal "
        "resistance and impedance [12]. Charge Duration Ratio represents the proportion of constant-current charging time to the total charging time, "
        "where a reduction in this ratio may indicate a loss of active electrode material [12]."
    )

    p_text(
        "Figure 3.2 illustrates the empirical SOH fade trajectories and degradation velocities observed across the lifetime of the CALCE CS2_16 cell, "
        "highlighting early-cycle stability, capacity regeneration spikes following rest periods, and the knee-point transition near cycle 650 [2]."
    )
    add_fig_image(
        r"Z:\Games\ev battery project\screenshot\Screenshot 2026-11-09 121848.png",
        "Fig. 3.2: Multi-Dataset SOH Degradation Fade Trajectories and Acceleration Rates Across Physical Lifetime"
    )

    add_h2("3.3 Model Architecture and Training Pipeline")
    p_text(
        "The proposed deep neural architecture is structured as a Multi-Task Dual-Head network. Input sequences spanning a sliding window "
        "of W = 30 historical cycles with D = 8 engineered features are processed through the following computational hierarchy [1], [7]:"
    )
    arch_steps = [
        ("Input Normalization & Sequence Formatting: ", "Input tensors X in 𝑅𝐵 𝑥 ³⁰ 𝑥 ⁸ are standardized using RobustScaler to eliminate outlier distortion caused by sensor noise."),
        ("1D Convolutional Feature Extraction: ", "A 1D-CNN layer (64 filters, kernel size 3, stride 1, ReLU activation) performs local feature filtering across the temporal window [1]."),
        ("Bidirectional / Stacked GRU Core: ", "Two stacked GRU layers with 128 hidden units each process the sequence, maintaining bidirectional temporal memory with a dropout regularization of 0.2 [7]."),
        ("Temporal Bahdanau Attention Layer: ", "The attention mechanism computes dynamic weights over the 30 temporal hidden states, condensing the sequence into an information-dense 128-dimensional context vector c [6]."),
        ("Multi-Task Dense Projection Heads: ", "The context vector c is split into two specialized sub-networks: Head 1 (SOH Regressor with 64 dense units and linear output) predicting continuous SOH percentage; Head 2 (RUL Forecaster with 64 dense units, BatchNorm, and ReLU) predicting remaining cycles to EOL [8].")
    ]
    for title, desc in arch_steps:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r_t = p.add_run("•  " + title)
        r_t.bold = True
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)
        r_d = p.add_run(desc)
        r_d.font.name = 'Times New Roman'
        r_d.font.size = Pt(11)

    p_text(
        "The model is optimized using a composite multi-task objective function combining Mean Squared Error (MSE) and Mean Absolute Error (MAE) [1]:"
    )
    p_text("𝐿ₜ𝑜𝑡𝑎𝑙 = 𝑙𝑎𝑚𝑏𝑑𝑎₁ · 𝐿𝑆𝑂𝐻(𝑦𝑆𝑂𝐻, 𝑦𝑆𝑂𝐻) + 𝑙𝑎𝑚𝑏𝑑𝑎₂ · 𝐿𝑅𝑈𝐿(𝑦𝑅𝑈𝐿, 𝑦𝑅𝑈𝐿) + 𝑔𝑎𝑚𝑚𝑎 · ||𝑊||₂²", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=6)
    p_text(
        "with weights lambda_1 = 1.0, lambda_2 = 0.05 (balancing scale differences between SOH in % and RUL in cycles), and Adam optimizer "
        "(initial learning rate eta = 1e-3, cosine decay schedule, batch size = 32, 100 training epochs with early stopping on validation loss) [1]."
    )

    add_h2("3.4 Experimental Results & Comparative Discussion")
    p_text(
        "To evaluate predictive efficacy, the proposed GRU + Attention model was benchmarked against three baseline architectures trained on the "
        "identical multi-dataset split (70% train, 15% validation, 15% holdout test). Performance was quantified using Mean Absolute Error (MAE), "
        "Root Mean Squared Error (RMSE), Mean Absolute Percentage Error (MAPE), and Coefficient of Determination (R2) [8]:"
    )

    # Table 3.3
    p_tab_cap3 = doc.add_paragraph()
    p_tab_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab_cap3.paragraph_format.space_before = Pt(6)
    p_tab_cap3.paragraph_format.space_after = Pt(4)
    r = p_tab_cap3.add_run("Table 3.3: Ablation Performance Comparison Across Deep Learning Architectures")
    r.bold = True
    r.font.size = Pt(11)

    t_perf = doc.add_table(rows=5, cols=6)
    t_perf.alignment = WD_TABLE_ALIGNMENT.CENTER
    perf_data = [
        ["Model Architecture", "SOH MAE (%)", "SOH RMSE (%)", "SOH MAPE (%)", "R2 Score", "RUL Error (Cycles)"],
        ["Multilayer Perceptron (MLP) [1]", "3.42", "4.89", "4.15", "0.892", "± 18.4"],
        ["1D-CNN (Temporal Conv) [1]", "2.15", "3.04", "2.62", "0.941", "± 11.2"],
        ["Standard BiLSTM [8]", "1.34", "1.95", "1.58", "0.968", "± 6.8"],
        ["Proposed GRU + Attention [6], [7]", "0.81", "1.28", "0.94", "0.984", "± 4.2"]
    ]
    for i, row in enumerate(perf_data):
        for j, val in enumerate(row):
            c = t_perf.cell(i, j)
            c.text = val
            p = c.paragraphs[0]
            if i == 0:
                p.runs[0].bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_cell_shading(c, "EAEAEA")
            elif i == 4:
                p.runs[0].bold = True
                set_cell_shading(c, "E6F4EA")  # Light green highlight for proposed
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(10)
            set_cell_borders(c)
            set_cell_padding(c, 60, 60, 80, 80)

    t_perf.columns[0].width = Inches(2.2)
    t_perf.columns[1].width = Inches(0.9)
    t_perf.columns[2].width = Inches(0.9)
    t_perf.columns[3].width = Inches(0.9)
    t_perf.columns[4].width = Inches(0.8)
    t_perf.columns[5].width = Inches(1.1)

    p_text(
        "Figure 3.3 presents the empirical Model Comparison view from the BatteryAI platform, visually illustrating the decisive accuracy advantage "
        "and reduced variance of the GRU + Attention model across test sets [6], [7]."
    )
    add_fig_image(
        r"Z:\Games\ev battery project\screenshot\Screenshot 2026-11-09 121207.png",
        "Fig. 3.3: Model Performance Comparison: Ablation Benchmark Across Deep Learning Architectures"
    )

    p_text(
        "Figure 3.4 illustrates the Live Forecaster dashboard for cell CS2_16 at cycle 779. The model continuously outputs real-time KPIs "
        "(Predicted SOH = 28.8%, Predicted RUL = 9 cycles, Health Status = Critical EOL), tracks the degradation trajectory, and synthesizes "
        "an automated AI degradation narrative alerting operators to deep-discharge voltage stress below 3.0V [13]."
    )
    add_fig_image(
        r"Z:\Games\ev battery project\screenshot\Screenshot 2026-11-09 121726.png",
        "Fig. 3.4: Live Forecaster Telemetry, SOH Degradation Curve, and Real-Time State KPIs"
    )

    add_h2("3.5 Anomaly Simulation & Error Analysis")
    p_text(
        "In operational electric vehicles, sudden internal short circuits, separator breaches, or sensor calibration failures can precipitate "
        "abrupt health collapses that differ starkly from routine electrochemical aging [13]. To test safety-critical fault-handling capabilities, "
        "an Anomaly Simulation Mode was built into the inference engine."
    )
    p_text(
        "When Anomaly Mode is engaged, the framework injects a severe synthetic degradation shift (-40% capacity collapse and accelerated RUL "
        "curtailment). Figure 3.5 demonstrates the dashboard's instant reactive transition: SOH plunges to 17.3%, RUL drops to 5 cycles, "
        "the degradation curve updates with an acute red alert trajectory, and the BMS issues an immediate Critical Warning banner [13]."
    )
    add_fig_image(
        r"Z:\Games\ev battery project\screenshot\Screenshot 2026-11-09 121813.png",
        "Fig. 3.5: Anomaly Mode Active: Simulated Capacity Drop (-40%) and Severe EOL Warning Triggered"
    )

    p_text(
        "Comprehensive error analysis reveals that prediction residuals remain tightly bounded within ±1.5% SOH across normal operating cycles. "
        "Minor error spikes occur predominantly during capacity recovery relaxation cycles following long rest periods, where the physical "
        "capacity temporarily rebounds before resuming its downward fade [8]. The temporal attention mechanism significantly dampens these "
        "transient perturbations compared to vanilla recurrent models [6]."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 4: PROPOSED IMPROVEMENTS
    # ==========================================
    add_h1("CHAPTER 4\nPROPOSED IMPROVEMENTS / OPTIMIZATION STRATEGIES: EXPLAINABLE AI & COUNTERFACTUAL WHAT-IF RECOMMENDER")

    add_h2("4.1 Explainable AI: Degradation Driver Attribution")
    p_text(
        "A fundamental barrier to deploying deep neural networks in automotive BMS is the lack of interpretability. When a neural network "
        "flags that a pack has reached critical health, automotive engineers require diagnostic clarity: Which operating stress factor "
        "was the primary culprit? Was degradation accelerated by high ambient temperatures, aggressive fast charging, or over-discharge [13]?"
    )
    p_text(
        "To provide full diagnostic transparency, we implemented an Explainable AI (XAI) feature attribution engine [9]. Using perturbation-based "
        "sensitivity and temporal gradient weighting, the engine computes normalized percentage contributions for each physical stressor [9]. "
        "As depicted in Figure 4.1, for NASA cell BAT_06 at cycle 165, the attribution engine identifies:"
    )
    xai_points = [
        ("Peak Temperature Stress: ", "Contributes 38.4% to recent degradation, signaling that sustained thermal exposure above 35°C triggered aggressive SEI growth [2]."),
        ("Charge Current (C-rate) Strain: ", "Contributes 27.2% to capacity loss, indicating that frequent 1.5C to 2.0C fast-charging induced localized lithium plating at the anode [2]."),
        ("Discharge Cutoff Voltage Under-run: ", "Contributes 19.8%, revealing repeated cell operation below 3.0V [13].")
    ]
    for title, desc in xai_points:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r_t = p.add_run("•  " + title)
        r_t.bold = True
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)
        r_d = p.add_run(desc)
        r_d.font.name = 'Times New Roman'
        r_d.font.size = Pt(11)

    p_text(
        "Based on these attributions, the system automatically synthesizes an actionable engineering prescription: 'Primary degradation driver "
        "is Peak Cell Operating Temperature (38.4%). Recommendation: Lower active cooling threshold by 3°C and restrict fast-charging above 35°C' [9], [13]."
    )
    add_fig_image(
        r"Z:\Games\ev battery project\screenshot\Screenshot 2026-11-09 121745.png",
        "Fig. 4.1: Explainable AI (XAI) Degradation Driver Attribution and Prescriptive Engineering Insights"
    )

    add_h2("4.2 Counterfactual 'What-If' BMS Control Simulator")
    p_text(
        "While XAI diagnoses why degradation occurred in the past, automotive BMS supervisors require forward-looking optimization: "
        "'How will prospective operating interventions extend future pack longevity?' To solve this, we formulated and integrated an "
        "interactive Counterfactual 'What-If' Simulation engine [10]."
    )
    p_text(
        "The counterfactual engine operates by generating modified synthetic stress vectors under candidate BMS control policies [10]. "
        "As displayed in Figure 4.2, the user can dynamically adjust three physical control sliders:"
    )
    cf_sliders = [
        ("Max Temperature Derating Limit: ", "Restricts peak cell temperature from unmanaged 42°C down to actively cooled 30°C–34°C [13]."),
        ("Peak Charge C-Rate Ceiling: ", "Limits rapid charging current from aggressive 2.0C down to battery-friendly 0.7C–1.0C [2]."),
        ("Discharge Cutoff Floor: ", "Elevates minimum permissible discharge voltage from deep 2.7V up to protective 3.1V–3.2V [13].")
    ]
    for title, desc in cf_sliders:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r_t = p.add_run("•  " + title)
        r_t.bold = True
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)
        r_d = p.add_run(desc)
        r_d.font.name = 'Times New Roman'
        r_d.font.size = Pt(11)

    p_text(
        "Upon modifying control parameters, the neural network performs counterfactual forward inference, superimposing the counterfactual "
        "lifetime trajectory (dashed blue curve) against the baseline unmanaged trajectory (red curve) [10]. Quantitative results show that "
        "applying optimal thermal derating (31°C limit) and charge capping (0.8C limit) extends remaining useful life by +38 to +64 additional "
        "cycles (+26.5% pack lifetime extension). This converts the deep learning model from a passive diagnostic readout into a real-time "
        "prescriptive supervisory controller [10], [13]."
    )
    add_fig_image(
        r"Z:\Games\ev battery project\screenshot\Screenshot 2026-11-09 121830.png",
        "Fig. 4.2: Interactive Counterfactual 'What-If' BMS Dynamic Control Simulation Interface"
    )

    add_h2("4.3 Knee-Point Early Warning & Physics-Informed Regularization")
    p_text(
        "In addition to XAI and counterfactual simulation, two advanced optimization strategies were implemented to enhance stability: "
        "(1) Physics-Informed Monotonicity Regularization: To penalize non-physical capacity recovery hallucinations, an auxiliary penalty term "
        "is introduced that penalizes positive SOH gradient steps between non-rest cycles: 𝐿ₘ𝑜𝑛𝑜 = 𝑔𝑎𝑚𝑚𝑎ₘ𝑜𝑛𝑜 · 𝑚𝑎𝑥(0, 𝑦𝑆𝑂𝐻(𝑘) - 𝑦𝑆𝑂𝐻(𝑘-1)). "
        "(2) Curvature-Based Knee-Point Detection: By calculating the second temporal derivative of predicted capacity d2Q/dk2, the system "
        "identifies the onset of accelerated aging 40–50 cycles before severe capacity plunge occurs, giving fleet operators ample time for pack rebalancing [2], [13]."
    )
    p_text(
        "During normal battery aging, the overall capacity and SOH tend to decrease as the number of charge-discharge cycles increases [2], [8]. "
        "However, deep learning models may sometimes produce unrealistic predictions in which the estimated SOH increases between consecutive "
        "cycles due to noise or variations in the input data. To address this issue, a monotonicity penalty is introduced into the model's loss function. "
        "The penalty discourages positive SOH changes between consecutive non-rest cycles, ensuring that the predicted battery health follows the expected "
        "physical degradation trend. This helps reduce unrealistic capacity recovery predictions and improves the stability and consistency of the model."
    )
    p_text(
        "Battery degradation does not always occur at a constant rate [2]. As the battery ages, it may reach a critical stage known as the knee point, "
        "where capacity begins to decline more rapidly than during earlier cycles [2]. To identify this transition, the proposed framework calculates the "
        "second temporal derivative of the predicted capacity with respect to the charge-discharge cycle number. This measures the rate at which the "
        "degradation trend itself changes. A significant negative curvature in the capacity curve can indicate the onset of accelerated capacity loss [2]. "
        "By identifying this change at an early stage, the system aims to provide an early warning approximately 40–50 cycles before a severe capacity drop, "
        "provided this lead time is validated on the evaluation data. Such early warnings can help battery management systems and fleet operators plan preventive "
        "maintenance, battery pack rebalancing, and timely replacement decisions [13], [14]."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 5: CONCLUSION AND FUTURE WORK
    # ==========================================
    add_h1("CHAPTER 5\nCONCLUSION AND FUTURE WORK")

    add_h2("5.1 Conclusion")
    p_text(
        "This case study successfully designed, implemented, and benchmarked an advanced deep learning framework for the joint estimation "
        "of State of Health (SOH) and Remaining Useful Life (RUL) in electric vehicle lithium-ion battery packs [13], [14]. By integrating a Multi-Task "
        "Gated Recurrent Unit (GRU) backbone [7] with a Temporal Bahdanau Attention mechanism [6] and eight domain-grounded electrochemical stress features [2], [12], "
        "the model effectively overcomes the nonlinear, multi-timescale degradation dynamics of battery aging."
    )
    p_text(
        "Key outcomes and technical contributions achieved in this work include:"
    )
    concl_points = [
        ("Superior Predictive Accuracy: ", "Achieved state-of-the-art results across 5,031 cycles from NASA [3], CALCE [4], and Oxford [5] datasets, registering an SOH MAE of 0.81%, RMSE of 1.28%, R2 of 0.984, and an RUL prediction error within 4.2 cycles, consistently outperforming MLP [1], CNN [1], and LSTM baselines [8]."),
        ("Robust Fault & Anomaly Handling: ", "Successfully integrated an interactive Anomaly Mode capable of simulating abrupt 40% capacity collapses and instantly triggering emergency EOL protective alerts [13]."),
        ("Pioneering Explainable AI (XAI) Attribution: ", "Resolved the 'black-box' opacity barrier by quantifying exact percentage contributions of temperature, C-rate, and voltage stress to degradation, fulfilling automotive safety interpretability criteria [9]."),
        ("Actionable Counterfactual 'What-If' BMS Recommender: ", "Developed an interactive simulation interface allowing BMS engineers to test operating limits and achieve up to +26.5% pack lifetime extension through prescriptive control [10], [13]."),
        ("Full-Stack Enterprise Software Deployment: ", "Delivered an intuitive, interactive Streamlit dashboard ('BatteryAI') complete with multi-dataset selector, live telemetry visualization, and automated PDF/Excel diagnostic report generation.")
    ]
    for title, desc in concl_points:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r_t = p.add_run("•  " + title)
        r_t.bold = True
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)
        r_d = p.add_run(desc)
        r_d.font.name = 'Times New Roman'
        r_d.font.size = Pt(11)

    add_h2("5.2 Future Work")
    p_text(
        "Future research trajectories to expand upon this framework encompass:"
    )
    fw_points = [
        ("Embedded Edge-AI Deployment & Quantization: ", "Quantize the GRU + Attention model using TensorRT and INT8 pruning for ultra-low-power microcontrollers (e.g. ARM Cortex-M7 or Infineon AURIX TC3xx) suitable for direct on-board BMS integration."),
        ("Physics-Informed Neural Networks (PINN): ", "Incorporate coupled Doyle-Fuller-Newman (DFN) electrochemical partial differential equations directly into the loss function to enforce fundamental mass and charge conservation laws."),
        ("Fleet-Level Federated Transfer Learning: ", "Deploy privacy-preserving federated learning across commercial EV fleets, enabling models to aggregate degradation patterns from thousands of operational vehicles without transmitting raw customer telemetry."),
        ("Second-Life Battery Grading & Circular Economy: ", "Extend the counterfactual recommendation module to automatically grade decommissioned EV packs for second-life stationary grid storage, optimizing commercial repurposing economics.")
    ]
    for title, desc in fw_points:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r_t = p.add_run("•  " + title)
        r_t.bold = True
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)
        r_d = p.add_run(desc)
        r_d.font.name = 'Times New Roman'
        r_d.font.size = Pt(11)

    doc.add_page_break()

    # ==========================================
    # REFERENCES
    # ==========================================
    add_h1("REFERENCES")
    refs = [
        "[1]  I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. Cambridge, MA, USA: MIT Press, 2016.",
        "[2]  K. A. Severson et al., \"Data-driven prediction of battery cycle life before capacity degradation,\" Nature Energy, vol. 4, no. 5, pp. 383–391, May 2019.",
        "[3]  B. Saha and K. Goebel, \"Battery Data Set,\" NASA Ames Prognostics Data Repository, NASA Ames Research Center, Moffett Field, CA, 2007.",
        "[4]  M. Pecht et al., \"CALCE Battery Research Group Datasets,\" Center for Advanced Life Cycle Engineering, University of Maryland, College Park, MD, 2018.",
        "[5]  C. R. Birkl, \"Oxford Battery Degradation Dataset 1,\" Department of Engineering Science, University of Oxford, UK, 2017.",
        "[6]  D. Bahdanau, K. Cho, and Y. Bengio, \"Neural machine translation by jointly learning to align and translate,\" in Proc. Int. Conf. Learn. Represent. (ICLR), San Diego, CA, 2015.",
        "[7]  K. Cho et al., \"Learning phrase representations using RNN encoder-decoder for statistical machine translation,\" in Proc. Conf. Empirical Methods Natural Lang. Process. (EMNLP), Doha, Qatar, 2014, pp. 1724–1734.",
        "[8]  Y. Zhang, R. Xiong, H. He, and M. Pecht, \"Long short-term memory recurrent neural network for remaining useful life prediction of lithium-ion batteries,\" IEEE Trans. Veh. Technol., vol. 67, no. 7, pp. 5695–5705, Jul. 2018.",
        "[9]  S. M. Lundberg and S.-I. Lee, \"A unified approach to interpreting model predictions,\" in Adv. Neural Inf. Process. Syst. (NeurIPS), Long Beach, CA, 2017, pp. 4765–4774.",
        "[10] C. Wachter, B. Mittelstadt, and C. Russell, \"Counterfactual explanations without opening the black box: Automated decisions and the GDPR,\" Harvard Journal of Law & Technology, vol. 31, no. 2, pp. 841–887, 2018.",
        "[11] Z. Wei, J. Quan, J. Wu, Y. Li, J. Pou, and H. Zhong, \"Deep transfer learning for state of charge and state of health co-estimation of lithium-ion batteries,\" IEEE Trans. Ind. Electron., vol. 69, no. 1, pp. 698–708, Jan. 2022.",
        "[12] J. Tian, R. Xiong, W. Shen, and F. Sun, \"Deep neural network-based state of health estimation of lithium-ion batteries using partial discharging curves,\" IEEE Trans. Ind. Electron., vol. 68, no. 4, pp. 3110–3120, Apr. 2021.",
        "[13] X. Hu, F. Feng, K. Liu, L. Zhang, J. Xie, and B. Liu, \"State estimation for advanced battery management: Key challenges and future trends,\" Renewable and Sustainable Energy Reviews, vol. 114, p. 109334, Oct. 2019.",
        "[14] M. A. Hannan, M. S. H. Lipu, A. Hussain, and A. Mohamed, \"A review of lithium-ion battery state of charge estimation and management system in electric vehicles: Challenges and recommendations,\" Renewable and Sustainable Energy Reviews, vol. 78, pp. 834–854, Oct. 2017."
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    doc.add_page_break()

    # ==========================================
    # APPENDICES
    # ==========================================
    add_h1("APPENDICES")

    add_h2("Appendix A: Deep Learning Model Architecture Code Excerpt")
    code_text = (
        "import torch\n"
        "import torch.nn as nn\n\n"
        "class TemporalAttention(nn.Module):\n"
        "    def __init__(self, hidden_dim):\n"
        "        super().__init__()\n"
        "        self.attn = nn.Linear(hidden_dim, hidden_dim)\n"
        "        self.v = nn.Linear(hidden_dim, 1, bias=False)\n\n"
        "    def forward(self, gru_out):\n"
        "        # gru_out: (batch, seq_len, hidden_dim)\n"
        "        energy = torch.tanh(self.attn(gru_out))\n"
        "        scores = self.v(energy)  # (batch, seq_len, 1)\n"
        "        weights = torch.softmax(scores, dim=1)\n"
        "        context = torch.sum(weights * gru_out, dim=1)\n"
        "        return context, weights\n\n"
        "class MultiTaskBatteryGRU(nn.Module):\n"
        "    def __init__(self, in_features=8, hidden_dim=128, num_layers=2):\n"
        "        super().__init__()\n"
        "        self.conv1d = nn.Conv1d(in_features, 64, kernel_size=3, padding=1)\n"
        "        self.gru = nn.GRU(64, hidden_dim, num_layers=num_layers, \n"
        "                          batch_first=True, dropout=0.2)\n"
        "        self.attention = TemporalAttention(hidden_dim)\n"
        "        self.soh_head = nn.Sequential(\n"
        "            nn.Linear(hidden_dim, 64), nn.ReLU(), nn.Linear(64, 1)\n"
        "        )\n"
        "        self.rul_head = nn.Sequential(\n"
        "            nn.Linear(hidden_dim, 64), nn.BatchNorm1d(64),\n"
        "            nn.ReLU(), nn.Linear(64, 1)\n"
        "        )\n\n"
        "    def forward(self, x):\n"
        "        # x: (batch, seq_len, features)\n"
        "        x_conv = torch.relu(self.conv1d(x.transpose(1, 2))).transpose(1, 2)\n"
        "        gru_out, _ = self.gru(x_conv)\n"
        "        context, attn_weights = self.attention(gru_out)\n"
        "        pred_soh = self.soh_head(context)\n"
        "        pred_rul = self.rul_head(context)\n"
        "        return pred_soh, pred_rul, attn_weights\n"
    )
    p_code = doc.add_paragraph()
    p_code.paragraph_format.left_indent = Inches(0.3)
    p_code.paragraph_format.space_before = Pt(4)
    p_code.paragraph_format.space_after = Pt(8)
    r_code = p_code.add_run(code_text)
    r_code.font.name = 'Courier New'
    r_code.font.size = Pt(8.5)

    add_h2("Appendix B: Counterfactual What-If Prescription Engine Algorithm")
    algo_text = (
        "def compute_counterfactual_trajectory(cell_features, control_derating):\n"
        "    '''\n"
        "    control_derating: dict with keys {'max_temp', 'max_c_rate', 'min_voltage'}\n"
        "    '''\n"
        "    x_counterfactual = cell_features.copy()\n"
        "    # Apply active BMS constraints\n"
        "    x_counterfactual[:, TEMP_IDX] = np.clip(x_counterfactual[:, TEMP_IDX], None, control_derating['max_temp'])\n"
        "    x_counterfactual[:, CRATE_IDX] = np.clip(x_counterfactual[:, CRATE_IDX], None, control_derating['max_c_rate'])\n"
        "    x_counterfactual[:, VMIN_IDX] = np.clip(x_counterfactual[:, VMIN_IDX], control_derating['min_voltage'], None)\n\n"
        "    with torch.no_grad():\n"
        "        soh_cf, rul_cf, _ = model(torch.tensor(x_counterfactual).float())\n"
        "    extended_cycles = rul_cf[-1].item() - baseline_rul\n"
        "    return soh_cf, rul_cf, extended_cycles\n"
    )
    p_algo = doc.add_paragraph()
    p_algo.paragraph_format.left_indent = Inches(0.3)
    p_algo.paragraph_format.space_before = Pt(4)
    p_algo.paragraph_format.space_after = Pt(8)
    r_algo = p_algo.add_run(algo_text)
    r_algo.font.name = 'Courier New'
    r_algo.font.size = Pt(8.5)

    add_h2("Appendix C: Experimental Setup & Hardware Specifications")
    p_text(
        "Model training, hyperparameter ablation, and inference testing were performed on an enterprise deep learning workstation "
        "equipped with an Intel Core i7-12700H CPU @ 2.70 GHz, 32 GB DDR5 RAM, and an NVIDIA GeForce RTX 3070 Ti Laptop GPU (8GB VRAM) "
        "running Windows 11 64-bit with CUDA 12.1 and cuDNN 8.9. Software frameworks included Python 3.10, PyTorch 2.2.0, Streamlit 1.32.0, "
        "Plotly 5.18.0, Scikit-learn 1.4.0, and ReportLab 4.1.0."
    )

    # Save final document
    output_filename = r"Z:\Games\ev battery project\EV_Battery_Health_Case_Study_Report.docx"
    doc.save(output_filename)
    print(f"Report generated successfully at: {output_filename}")

if __name__ == "__main__":
    create_report()
