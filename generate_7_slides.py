import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ==========================================
# COLOR PALETTE (Modern Sustainable Tech Theme)
# ==========================================
DARK_GREEN = RGBColor(15, 76, 58)      # Deep Forest / Emerald Green #0F4C3A
FOREST_MED  = RGBColor(22, 101, 52)     # Medium Forest Green #166534
ACCENT_MINT = RGBColor(16, 185, 129)    # Vibrant Tech Mint #10B981
LIGHT_MINT  = RGBColor(236, 253, 245)   # Mint Tint #ECFDF5
BG_LIGHT    = RGBColor(248, 250, 252)   # Slate 50 Off-White #F8FAFC
CARD_BG     = RGBColor(255, 255, 255)   # Crisp White #FFFFFF
BORDER_GREY = RGBColor(226, 232, 240)   # Slate 200 #E2E8F0
TEXT_MAIN   = RGBColor(15, 23, 42)      # Slate 900 #0F172A
TEXT_MUTED  = RGBColor(100, 116, 139)   # Slate 500 #64748B
TEXT_DARK   = RGBColor(30, 41, 59)      # Slate 800 #1E293B
WHITE       = RGBColor(255, 255, 255)   # Pure White
BIN_BLUE    = RGBColor(37, 99, 235)     # Recyclable Blue
BIN_GREEN   = RGBColor(22, 163, 74)     # Organic Green
BIN_YELLOW  = RGBColor(202, 138, 4)     # Paper/Plastic Yellow
BIN_RED     = RGBColor(220, 38, 38)     # Hazardous Red
BIN_GREY    = RGBColor(71, 85, 105)     # General/E-waste Grey

FONT_FAMILY = "Segoe UI"

def set_slide_background(slide, color=BG_LIGHT):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_breadcrumb=None, is_dark=False):
    # Top accent line
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = ACCENT_MINT
    top_bar.line.color.rgb = ACCENT_MINT
    
    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.733), Inches(1.1))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    if category_breadcrumb:
        p_sub = tf.paragraphs[0]
        p_sub.text = category_breadcrumb.upper()
        p_sub.font.name = FONT_FAMILY
        p_sub.font.size = Pt(9.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = ACCENT_MINT if is_dark else FOREST_MED
        p_sub.space_after = Pt(2)
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]
        
    p_title.text = title_text
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = WHITE if is_dark else TEXT_MAIN

def add_footer(slide, slide_num, total_slides=7, is_dark=False):
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.4))
    tf = footer_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "SRM Institute of Science and Technology | Department of Computational Intelligence | B.Tech CSE (AI & ML)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(8.5)
    p.font.color.rgb = RGBColor(148, 163, 184) if is_dark else TEXT_MUTED
    
    num_p = tf.add_paragraph()
    num_p.text = f"{slide_num:02d} / {total_slides:02d}"
    num_p.alignment = PP_ALIGN.RIGHT
    num_p.font.name = FONT_FAMILY
    num_p.font.size = Pt(8.5)
    num_p.font.bold = True
    num_p.font.color.rgb = ACCENT_MINT if is_dark else FOREST_MED

def create_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_GREY):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

# ==============================================================================
# 7-SLIDE CORE PRESENTATION BUILDER
# ==============================================================================
def build_7_slide_presentation(filename="Smart_Waste_Classification_7_Slides.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # ----------------------------------------------------
    # SLIDE 1: Title Slide (Academic & Modern Minimalist)
    # ----------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, RGBColor(246, 249, 248))
    
    # Left decorative vertical accent bar
    bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.45), Inches(7.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = DARK_GREEN
    bar.line.fill.background()
    
    subbar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.45), Inches(0), Inches(0.12), Inches(7.5))
    subbar.fill.solid()
    subbar.fill.fore_color.rgb = ACCENT_MINT
    subbar.line.fill.background()

    # Academic Category Badge
    badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(0.8), Inches(4.5), Inches(0.38))
    badge.fill.solid()
    badge.fill.fore_color.rgb = LIGHT_MINT
    badge.line.color.rgb = ACCENT_MINT
    badge.line.width = Pt(1)
    tf_b = badge.text_frame
    tf_b.margin_left = Inches(0.15)
    tf_b.margin_top = Inches(0.04)
    p_b = tf_b.paragraphs[0]
    p_b.text = "FINAL YEAR B.TECH (CSE - AI & ML) PROJECT REVIEW"
    p_b.font.name = FONT_FAMILY
    p_b.font.size = Pt(9)
    p_b.font.bold = True
    p_b.font.color.rgb = FOREST_MED

    # Main Project Title Box
    title_box = slide1.shapes.add_textbox(Inches(1.2), Inches(1.35), Inches(10.8), Inches(1.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    
    p1 = tf_t.paragraphs[0]
    p1.text = "SMART WASTE CLASSIFICATION SYSTEM"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = DARK_GREEN
    
    p2 = tf_t.add_paragraph()
    p2.text = "USING DEEP LEARNING WITH BIN RECOMMENDATION & ANALYTICS DASHBOARD"
    p2.font.name = FONT_FAMILY
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = FOREST_MED
    p2.space_before = Pt(4)

    p3 = tf_t.add_paragraph()
    p3.text = "An intelligent, sustainable computer vision framework for automated waste segregation and real-time facility intelligence."
    p3.font.name = FONT_FAMILY
    p3.font.size = Pt(12)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_before = Pt(8)

    # Metadata Cards (2 Columns: Students & Institutional Credentials)
    # Left Card: Student Team
    card_stu = create_card(slide1, Inches(1.2), Inches(3.6), Inches(5.3), Inches(2.9))
    tf_s = card_stu.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = Inches(0.3)
    
    p = tf_s.paragraphs[0]
    p.text = "STUDENT INVESTIGATORS"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = FOREST_MED
    p.space_after = Pt(8)
    
    students = [
        ("Student Name 1", "RA211100301XXXX"),
        ("Student Name 2", "RA211100301XXXX"),
        ("Student Name 3", "RA211100301XXXX"),
        ("Student Name 4", "RA211100301XXXX")
    ]
    for name, reg in students:
        p_row = tf_s.add_paragraph()
        p_row.text = f"• {name}  [{reg}]"
        p_row.font.name = FONT_FAMILY
        p_row.font.size = Pt(11)
        p_row.font.color.rgb = TEXT_DARK
        p_row.space_after = Pt(3)

    p_note = tf_s.add_paragraph()
    p_note.text = "(B.Tech CSE with Specialization in AI & ML)"
    p_note.font.name = FONT_FAMILY
    p_note.font.size = Pt(9.5)
    p_note.font.color.rgb = TEXT_MUTED
    p_note.space_before = Pt(4)

    # Right Card: Institutional & Guide
    card_inst = create_card(slide1, Inches(6.8), Inches(3.6), Inches(5.3), Inches(2.9))
    tf_i = card_inst.text_frame
    tf_i.word_wrap = True
    tf_i.margin_left = tf_i.margin_top = Inches(0.3)
    
    p = tf_i.paragraphs[0]
    p.text = "PROJECT SUPERVISION & INSTITUTION"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = FOREST_MED
    p.space_after = Pt(8)

    inst_items = [
        ("Project Guide:", "[Guide Name / Faculty Designation]"),
        ("Department:", "Department of Computational Intelligence"),
        ("Faculty / School:", "School of Computing"),
        ("Institution:", "SRM Institute of Science and Technology"),
        ("Academic Year:", "2025 – 2026")
    ]
    for lbl, val in inst_items:
        p_r = tf_i.add_paragraph()
        p_r.text = f"{lbl} {val}"
        p_r.font.name = FONT_FAMILY
        p_r.font.size = Pt(11)
        p_r.font.color.rgb = TEXT_DARK
        p_r.space_after = Pt(3)

    add_footer(slide1, 1, 7)

    # ----------------------------------------------------
    # SLIDE 2: Problem Statement, Challenges & Motivation
    # ----------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "Problem Statement, Context & Motivation", "Context & Foundation")

    col_w = Inches(3.7)
    gap = Inches(0.3)
    top_pos = Inches(1.6)
    card_h = Inches(5.1)

    # Col 1: Current Waste Management Crisis
    c1 = create_card(slide2, Inches(0.8), top_pos, col_w, card_h)
    tf1 = c1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_top = tf1.margin_right = Inches(0.28)
    
    p = tf1.paragraphs[0]
    p.text = "1. Global Waste Crisis"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(10)

    bullets1 = [
        ("Exponential Growth", "Rapid urbanization and consumption generate over 2.01 billion tons of municipal solid waste annually worldwide."),
        ("Improper Segregation", "Over 70% of recyclable material ends up in landfills or incinerators due to contaminated source sorting."),
        ("Environmental Degradation", "Unsegregated waste leads to toxic leachate, greenhouse gas emissions (methane), and marine pollution.")
    ]
    for b_title, b_desc in bullets1:
        p_t = tf1.add_paragraph()
        p_t.text = f"• {b_title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf1.add_paragraph()
        p_d.text = f"  {b_desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(8)

    # Col 2: The Core Problem Statement
    c2 = create_card(slide2, Inches(0.8) + col_w + gap, top_pos, col_w, card_h, bg_color=LIGHT_MINT, border_color=ACCENT_MINT)
    tf2 = c2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = Inches(0.28)
    
    p = tf2.paragraphs[0]
    p.text = "2. Core Problem Statement"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = FOREST_MED
    p.space_after = Pt(10)

    bullets2 = [
        ("Manual Identification", "Traditional manual sorting is hazardous, labor-intensive, error-prone, and economically unviable at scale."),
        ("Visual Ambiguity", "Visually similar materials (e.g., clear PET plastic vs. glass, foil-coated paper) confuse public users."),
        ("Absence of Disposal Guidance", "Conventional trash cans lack immediate feedback telling users exactly which bin to utilize."),
        ("Zero Analytics Visibility", "Facility managers have no telemetry on waste composition, segregation accuracy, or recycling volumes.")
    ]
    for b_title, b_desc in bullets2:
        p_t = tf2.add_paragraph()
        p_t.text = f"• {b_title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_GREEN
        p_d = tf2.add_paragraph()
        p_d.text = f"  {b_desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_DARK
        p_d.space_after = Pt(6)

    # Col 3: Research Motivation
    c3 = create_card(slide2, Inches(0.8) + (col_w + gap)*2, top_pos, col_w, card_h)
    tf3 = c3.text_frame
    tf3.word_wrap = True
    tf3.margin_left = tf3.margin_top = tf3.margin_right = Inches(0.28)
    
    p = tf3.paragraphs[0]
    p.text = "3. Motivation & SDGs"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(10)

    bullets3 = [
        ("AI for Environmental Good", "Leveraging state-of-the-art Computer Vision & Deep Learning to remove human guesswork at the disposal point."),
        ("Circular Economy Acceleration", "High-purity source segregation drastically enhances material reclaim value and recycling economics."),
        ("Sustainable Development Goals", "Directly targets UN SDG 11 (Sustainable Cities) and SDG 12 (Responsible Consumption & Production)."),
        ("Campus & Smart City Ready", "Providing an accessible, low-latency software & analytics layer suitable for universities and municipal hubs.")
    ]
    for b_title, b_desc in bullets3:
        p_t = tf3.add_paragraph()
        p_t.text = f"• {b_title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf3.add_paragraph()
        p_d.text = f"  {b_desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    add_footer(slide2, 2, 7)

    # ----------------------------------------------------
    # SLIDE 3: Project Objectives & System Architecture
    # ----------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "System Architecture & Engineering Objectives", "Proposed Architecture")

    # Objectives Banner at top
    obj_box = create_card(slide3, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.4))
    tf_ob = obj_box.text_frame
    tf_ob.word_wrap = True
    tf_ob.margin_left = tf_ob.margin_top = Inches(0.2)
    
    p = tf_ob.paragraphs[0]
    p.text = "CORE PROJECT OBJECTIVES"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = FOREST_MED
    p.space_after = Pt(4)

    # 4 objective bullet columns in text
    p_objs = tf_ob.add_paragraph()
    p_objs.text = "1. Automated Deep Classification: Real-time image recognition into 7 distinct waste categories with high confidence."
    p_objs.font.name = FONT_FAMILY
    p_objs.font.size = Pt(10.5)
    p_objs.font.color.rgb = TEXT_DARK

    p_objs2 = tf_ob.add_paragraph()
    p_objs2.text = "2. Intelligent Bin Recommendation: Instant visual mapping of predicted class to standard color-coded disposal bins."
    p_objs2.font.name = FONT_FAMILY
    p_objs2.font.size = Pt(10.5)
    p_objs2.font.color.rgb = TEXT_DARK

    p_objs3 = tf_ob.add_paragraph()
    p_objs3.text = "3. Prediction Telemetry & Analytics: Persistent audit logging of disposals with dynamic aggregate analytics & charts."
    p_objs3.font.name = FONT_FAMILY
    p_objs3.font.size = Pt(10.5)
    p_objs3.font.color.rgb = TEXT_DARK

    # Architecture Flowchart (8 Steps horizontally)
    flow_title = slide3.shapes.add_textbox(Inches(0.8), Inches(3.1), Inches(11.733), Inches(0.4))
    p_ft = flow_title.text_frame.paragraphs[0]
    p_ft.text = "END-TO-END DATAFLOW & SYSTEM ARCHITECTURE"
    p_ft.font.name = FONT_FAMILY
    p_ft.font.size = Pt(12)
    p_ft.font.bold = True
    p_ft.font.color.rgb = DARK_GREEN

    # 8 Steps in 2 rows of 4 for maximum readability and visual impact
    steps = [
        ("Step 1: User Input", "User uploads image or captures waste sample via web/mobile interface."),
        ("Step 2: Frontend Client", "React/HTML5 UI validates file, renders preview, transmits multipart/form payload."),
        ("Step 3: Backend API", "REST API endpoint (Flask/FastAPI) ingests image, manages authentication & session."),
        ("Step 4: Preprocessing", "OpenCV resizes to 224x224, scales pixel values [0,1], applies tensor normalization."),
        ("Step 5: DL Inference", "Transfer Learning backbone (MobileNetV2/EfficientNet) executes inference."),
        ("Step 6: Bin Recommendation", "Rule-engine correlates top-1 class with color-coded waste bin specifications."),
        ("Step 7: Database Logging", "Prediction record (timestamp, class, confidence, metadata) persisted in DB."),
        ("Step 8: Analytics Dashboard", "Aggregates historical logs into interactive charts, category ratios, and metrics.")
    ]

    card_w = Inches(2.75)
    gap_x = Inches(0.24)
    card_h2 = Inches(1.5)
    
    # Row 1 (Steps 1-4)
    for i in range(4):
        x = Inches(0.8) + i * (card_w + gap_x)
        y = Inches(3.55)
        st_card = create_card(slide3, x, y, card_w, card_h2, bg_color=CARD_BG, border_color=ACCENT_MINT if i==3 else BORDER_GREY)
        tf = st_card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = Inches(0.18)
        p = tf.paragraphs[0]
        p.text = steps[i][0]
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = FOREST_MED
        p.space_after = Pt(4)
        p_desc = tf.add_paragraph()
        p_desc.text = steps[i][1]
        p_desc.font.name = FONT_FAMILY
        p_desc.font.size = Pt(9.5)
        p_desc.font.color.rgb = TEXT_DARK

    # Row 2 (Steps 5-8)
    for i in range(4):
        x = Inches(0.8) + i * (card_w + gap_x)
        y = Inches(5.25)
        st_card = create_card(slide3, x, y, card_w, card_h2, bg_color=LIGHT_MINT if i in (0, 1) else CARD_BG, border_color=FOREST_MED if i in (0,1) else BORDER_GREY)
        tf = st_card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = Inches(0.18)
        p = tf.paragraphs[0]
        p.text = steps[i+4][0]
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK_GREEN if i in (0,1) else FOREST_MED
        p.space_after = Pt(4)
        p_desc = tf.add_paragraph()
        p_desc.text = steps[i+4][1]
        p_desc.font.name = FONT_FAMILY
        p_desc.font.size = Pt(9.5)
        p_desc.font.color.rgb = TEXT_DARK

    add_footer(slide3, 3, 7)

    # ----------------------------------------------------
    # SLIDE 4: Dataset, Preprocessing & Deep Learning Model
    # ----------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "Dataset Engineering & Deep Learning Architecture", "Methodology & Modeling")

    # Left Column: Dataset & Preprocessing Pipeline (Width: 5.7)
    c_left = create_card(slide4, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = Inches(0.28)
    
    p = tf_l.paragraphs[0]
    p.text = "DATASET CORPUS & AUGMENTATION PIPELINE"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(8)

    data_bullets = [
        ("Benchmark Data Sources", "Synthesis of benchmark datasets including TrashNet, Kaggle Garbage Classification Dataset, supplemented with real-world collected imagery."),
        ("Seven Waste Categories", "Formulated around 7 primary waste classes: [Plastic, Paper, Cardboard, Glass, Metal, Organic/Biodegradable, Non-Recyclable/Trash]."),
        ("Preprocessing Pipeline", "Standardization to 224x224 RGB dimensions; Min-Max Channel Normalization (rescaling pixel intensity from [0, 255] to [0.0, 1.0])."),
        ("Data Augmentation", "Random horizontal/vertical flips, rotation range (+/- 25 deg), zoom range (0.2), shear, and brightness shifts to mitigate overfitting."),
        ("Partitioning Strategy", "Stratified dataset splitting: Training Set (70%), Validation Set (15%), and Unseen Test Holdout Set (15%).")
    ]
    for b_title, b_desc in data_bullets:
        p_t = tf_l.add_paragraph()
        p_t.text = f"• {b_title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_l.add_paragraph()
        p_d.text = f"  {b_desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    # Right Column: Deep Learning Model Architecture
    c_right = create_card(slide4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = Inches(0.28)

    p = tf_r.paragraphs[0]
    p.text = "TRANSFER LEARNING & CNN BACKBONE"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(8)

    dl_bullets = [
        ("Transfer Learning Rationale", "Leverages ImageNet pre-trained representations, significantly reducing convergence time and preventing overfitting on localized datasets."),
        ("Candidate Architectures", "Evaluated MobileNetV2 (inverted residuals & depthwise separable convolutions) and EfficientNet (compound scaling of depth, width & resolution)."),
        ("Feature Extraction", "Initial convolutional layers extract low-level edges/textures, while deeper layers capture invariant material geometric features."),
        ("Custom Classification Head", "Global Average Pooling 2D -> Dense Layer (128 units, ReLU) -> Dropout (p=0.3-0.5 for regularization) -> Dense Output (7 units, Softmax)."),
        ("Optimization & Loss", "Trained using Adam Optimizer (lr=1e-4) with Categorical Cross-Entropy Loss and early stopping triggers.")
    ]
    for b_title, b_desc in dl_bullets:
        p_t = tf_r.add_paragraph()
        p_t.text = f"• {b_title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_r.add_paragraph()
        p_d.text = f"  {b_desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    add_footer(slide4, 4, 7)

    # ----------------------------------------------------
    # SLIDE 5: Bin Recommendation Module & Analytics Dashboard
    # ----------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5)
    add_header(slide5, "Smart Bin Recommendation & Analytics Dashboard", "Core Deliverables & Features")

    # Left Section: Bin Recommendation Logic (Width: 5.7)
    c_bin = create_card(slide5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    tf_b = c_bin.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = Inches(0.28)

    p = tf_b.paragraphs[0]
    p.text = "AUTOMATED BIN RECOMMENDATION ENGINE"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(6)

    p_sub = tf_b.add_paragraph()
    p_sub.text = "Translates model output into clear disposal instructions based on municipal waste segregation norms:"
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(10)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_after = Pt(10)

    # 4 Bin Rule Cards inside left section
    bin_rules = [
        ("BLUE BIN (Dry Recyclables)", "Plastic bottles, Containers, Metal cans, Clean Glass containers.", BIN_BLUE),
        ("GREEN BIN (Wet / Biodegradable)", "Organic food waste, Fruit peels, Leaves, Compostable scraps.", BIN_GREEN),
        ("YELLOW BIN (Paper & Cardboard)", "Office paper, Books, Cardboard packaging, Clean cartons.", BIN_YELLOW),
        ("RED / GREY BIN (Special / Hazardous)", "E-waste, Chemical containers, Contaminated non-recyclable items.", BIN_RED)
    ]
    for b_name, b_items, b_color in bin_rules:
        p_bn = tf_b.add_paragraph()
        p_bn.text = f"■ {b_name}"
        p_bn.font.name = FONT_FAMILY
        p_bn.font.size = Pt(10.5)
        p_bn.font.bold = True
        p_bn.font.color.rgb = b_color
        p_bi = tf_b.add_paragraph()
        p_bi.text = f"   Items: {b_items}"
        p_bi.font.name = FONT_FAMILY
        p_bi.font.size = Pt(9.5)
        p_bi.font.color.rgb = TEXT_DARK
        p_bi.space_after = Pt(6)

    # Right Section: Prediction History & Analytics Dashboard (Width: 5.7)
    c_dash = create_card(slide5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    tf_d = c_dash.text_frame
    tf_d.word_wrap = True
    tf_d.margin_left = tf_d.margin_top = tf_d.margin_right = Inches(0.28)

    p = tf_d.paragraphs[0]
    p.text = "PREDICTION TELEMETRY & ANALYTICS DASHBOARD"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(6)

    dash_features = [
        ("Real-time History Audit Log", "Every classified image is recorded with timestamp, model confidence percentage, predicted class, and allocated bin."),
        ("Category Composition Chart", "Dynamic interactive doughnut/bar charts displaying the real-time ratio of sorted materials across the facility."),
        ("Segregation Accuracy Telemetry", "Monitors user adherence and identifies high-contamination zones across campus disposal points."),
        ("Exportable Environmental Metrics", "Calculates estimated carbon offset and recycled material tonnage for institutional sustainability audits."),
        ("Responsive Visualization Stack", "Built with modern Chart.js / Matplotlib components seamlessly integrated with a responsive web interface.")
    ]
    for d_title, d_desc in dash_features:
        p_t = tf_d.add_paragraph()
        p_t.text = f"• {d_title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_d.add_paragraph()
        p_d.text = f"  {d_desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    add_footer(slide5, 5, 7)

    # ----------------------------------------------------
    # SLIDE 6: Implementation Stack & Performance Evaluation
    # ----------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6)
    add_header(slide6, "System Implementation & Experimental Results", "Evaluation & Results")

    # Left Column: Technology Stack Breakdown
    c_tech = create_card(slide6, Inches(0.8), Inches(1.6), Inches(5.5), Inches(5.1))
    tf_t = c_tech.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = Inches(0.28)

    p = tf_t.paragraphs[0]
    p.text = "TECHNOLOGY STACK ARCHITECTURE"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(8)

    stack_rows = [
        ("Core Language:", "Python 3.10+ (Data engineering, pipeline, modeling)"),
        ("Deep Learning Framework:", "TensorFlow 2.x / Keras / PyTorch"),
        ("Computer Vision & Image Ops:", "OpenCV (cv2) & Pillow (PIL)"),
        ("Transfer Learning Backbone:", "MobileNetV2 / EfficientNet-B0 (Pre-trained on ImageNet)"),
        ("Backend Web Services:", "Flask / FastAPI REST Architecture"),
        ("Frontend & UI Dashboard:", "React.js / HTML5 / Modern Tailwind CSS"),
        ("Database / Persistence:", "SQLite / MySQL / Firebase Realtime DB"),
        ("Data Visualization:", "Chart.js / Matplotlib / Seaborn")
    ]
    for comp, tech in stack_rows:
        p_c = tf_t.add_paragraph()
        p_c.text = f"• {comp} "
        p_c.font.name = FONT_FAMILY
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = TEXT_DARK
        p_v = tf_t.add_paragraph()
        p_v.text = f"   {tech}"
        p_v.font.name = FONT_FAMILY
        p_v.font.size = Pt(9.5)
        p_v.font.color.rgb = FOREST_MED
        p_v.space_after = Pt(4)

    # Right Column: Performance Evaluation Metrics & Table
    c_eval = create_card(slide6, Inches(6.6), Inches(1.6), Inches(5.9), Inches(5.1))
    tf_e = c_eval.text_frame
    tf_e.word_wrap = True
    tf_e.margin_left = tf_e.margin_top = tf_e.margin_right = Inches(0.28)

    p = tf_e.paragraphs[0]
    p.text = "EXPERIMENTAL RESULTS & EVALUATION METRICS"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(4)

    p_note = tf_e.add_paragraph()
    p_note.text = "Model performance benchmarked against unseen test holdout partition across all 7 classes:"
    p_note.font.name = FONT_FAMILY
    p_note.font.size = Pt(9.5)
    p_note.font.color.rgb = TEXT_MUTED
    p_note.space_after = Pt(8)

    # 4 Quick Metric Cards
    metrics = [
        ("ACCURACY", "[XX.X%]", "Overall validation accuracy"),
        ("PRECISION", "[XX.X%]", "Macro weighted precision"),
        ("RECALL", "[XX.X%]", "Sensitivity across classes"),
        ("F1-SCORE", "[XX.X%]", "Harmonic mean of P & R")
    ]
    for m_label, m_val, m_desc in metrics:
        p_m = tf_e.add_paragraph()
        p_m.text = f"■ {m_label}: {m_val}  –  {m_desc}"
        p_m.font.name = FONT_FAMILY
        p_m.font.size = Pt(10.5)
        p_m.font.bold = True
        p_m.font.color.rgb = TEXT_DARK
        p_m.space_after = Pt(4)

    p_div = tf_e.add_paragraph()
    p_div.text = "Confusion Matrix & Error Analysis:"
    p_div.font.name = FONT_FAMILY
    p_div.font.size = Pt(11)
    p_div.font.bold = True
    p_div.font.color.rgb = FOREST_MED
    p_div.space_before = Pt(6)
    p_div.space_after = Pt(4)

    eval_points = [
        ("Confusion Matrix Verification", "Evaluated cross-class confusion; lowest false-positive rates observed between organic and recyclable streams."),
        ("Inference Latency", "Model achieves lightweight inference speed ([XX ms] per frame), enabling deployment on resource-constrained devices."),
        ("Academic Integrity Note", "Experimental metrics marked with [XX.X%] are project validation placeholders pending final training run verification.")
    ]
    for e_title, e_desc in eval_points:
        p_t = tf_e.add_paragraph()
        p_t.text = f"• {e_title}: {e_desc}"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(9.5)
        p_t.font.color.rgb = TEXT_MUTED
        p_t.space_after = Pt(4)

    add_footer(slide6, 6, 7)

    # ----------------------------------------------------
    # SLIDE 7: Future Scope, Project Impact & Conclusion
    # ----------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7)
    add_header(slide7, "Future Roadmap, Conclusion & Acknowledgements", "Summary & Next Steps")

    # Left Column: Future Scope & Roadmap (Width: 5.7)
    c_future = create_card(slide7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    tf_f = c_future.text_frame
    tf_f.word_wrap = True
    tf_f.margin_left = tf_f.margin_top = tf_f.margin_right = Inches(0.28)

    p = tf_f.paragraphs[0]
    p.text = "FUTURE DEVELOPMENT ROADMAP"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.space_after = Pt(8)

    future_items = [
        ("Real-Time Embedded Cameras", "Integration with low-cost edge microcomputers (Raspberry Pi 4 / NVIDIA Jetson Nano) for automated hopper scanning."),
        ("YOLOv8 Multi-Object Detection", "Upgrading from single-item classification to multi-object localization and real-time bounding box tracking."),
        ("IoT-Automated Motorized Bins", "Microcontroller-driven (ESP32/Arduino) pneumatic/servo bin lids that automatically open upon classification."),
        ("Cross-Platform Mobile App", "Flutter / React Native mobile client enabling citizen crowdsourcing and campus recycling reward gamification."),
        ("Edge-to-Cloud Analytics Mesh", "Federated dashboard uniting multi-building smart disposal hubs into a centralized campus sustainability monitor.")
    ]
    for f_title, f_desc in future_items:
        p_t = tf_f.add_paragraph()
        p_t.text = f"• {f_title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK
        p_d = tf_f.add_paragraph()
        p_d.text = f"  {f_desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_after = Pt(6)

    # Right Column: Conclusion, Acknowledgements & Q&A
    c_conc = create_card(slide7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), bg_color=LIGHT_MINT, border_color=ACCENT_MINT)
    tf_c = c_conc.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = Inches(0.28)

    p = tf_c.paragraphs[0]
    p.text = "PROJECT SUMMARY & CONCLUSION"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = FOREST_MED
    p.space_after = Pt(8)

    conc_points = [
        ("End-to-End System Integration", "Successfully demonstrated a closed-loop framework bridging deep learning vision, bin recommendation heuristics, and dynamic telemetry."),
        ("Environmental Sustainability", "Eliminates sorting ambiguity, boosting recyclability rates while generating actionable municipal intelligence."),
        ("Scalable & Modular", "Modular REST API architecture ensures effortless deployment on edge appliances or cloud infrastructures.")
    ]
    for c_title, c_desc in conc_points:
        p_t = tf_c.add_paragraph()
        p_t.text = f"✓ {c_title}:"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_GREEN
        p_d = tf_c.add_paragraph()
        p_d.text = f"   {c_desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_DARK
        p_d.space_after = Pt(6)

    # Thank you box inside bottom right
    p_ty = tf_c.add_paragraph()
    p_ty.text = "THANK YOU!"
    p_ty.font.name = FONT_FAMILY
    p_ty.font.size = Pt(16)
    p_ty.font.bold = True
    p_ty.font.color.rgb = DARK_GREEN
    p_ty.space_before = Pt(8)

    p_qa = tf_c.add_paragraph()
    p_qa.text = "Open for Questions, Evaluation & Suggestions from Faculty Members."
    p_qa.font.name = FONT_FAMILY
    p_qa.font.size = Pt(10)
    p_qa.font.color.rgb = TEXT_DARK

    p_dept = tf_c.add_paragraph()
    p_dept.text = "SRM Institute of Science and Technology | Dept. of Computational Intelligence"
    p_dept.font.name = FONT_FAMILY
    p_dept.font.size = Pt(9)
    p_dept.font.bold = True
    p_dept.font.color.rgb = FOREST_MED
    p_dept.space_before = Pt(4)

    add_footer(slide7, 7, 7)

    prs.save(filename)
    print(f"Successfully generated {filename} (7 slides)")

if __name__ == "__main__":
    build_7_slide_presentation()
