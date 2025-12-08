import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Flowable
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from io import BytesIO
from datetime import datetime

# ---------------------------
# STREAMLIT PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="iStar Smart Kids & Spacebot Receipt", page_icon="🧾")

# ---------------------------
# SESSION STATE INITIALIZATION
# ---------------------------
if "receipt_items" not in st.session_state:
    st.session_state.receipt_items = []

# ---------------------------
# HEADER + TWO LOGOS (close together + aligned left)
# ---------------------------

col1, col2 = st.columns([1, 1])  # Reduced spacing
with col1:
    st.image("iStar_logo.png", width=120)   # CHANGE NAME IF NEEDED
with col2:
    st.image("istar_logo2.png", width=120)  # CHANGE NAME IF NEEDED

st.title("🧾 iStar Smart Kids & Spacebot Ltd - Receipt Generator")
st.write("Generate professional PDF receipts for student program enrollment.")


# ---------------------------
# INPUT FIELDS
# ---------------------------
student_name = st.text_input("Student Name")

age_group = st.selectbox("Age Category", ["Below 13", "13 and Above"])

program = st.selectbox("Program Selected", [
    "Python", "Arduino", "Scratch", "Data Analysis", "C++", "AI", "Space Technology"
])

payment_method = st.selectbox("Payment Method", [
    "Cash", "Mobile Money", "Bank Transfer", "Cheque"
])

# Pricing logic
price = 1000 if age_group == "Below 13" else 1500
st.write(f"### 💵 Program Fee: **GHS {price}**")


# Add item
if st.button("Add Program to Receipt"):
    st.session_state.receipt_items.append({
        "name": program,
        "qty": 1,
        "price": price,
        "total": price
    })
    st.success(f"{program} added to receipt!")


# ---------------------------
# DISPLAY ITEMS
# ---------------------------
st.write("## 📋 Receipt Items")

if len(st.session_state.receipt_items) > 0:
    df = pd.DataFrame(st.session_state.receipt_items)
    st.table(df)
else:
    st.info("No items added yet.")


# ---------------------------
# FLOWABLE CLASS FOR SIDE-BY-SIDE PDF LOGOS
# ---------------------------
class TwoLogos(Flowable):
    def __init__(self, logo1_path, logo2_path, width=80, height=80, padding=20):
        Flowable.__init__(self)
        self.logo1 = logo1_path
        self.logo2 = logo2_path
        self.width = width
        self.height = height
        self.padding = padding

    def draw(self):
        self.canv.drawImage(self.logo1, 0, 0, width=self.width, height=self.height)
        self.canv.drawImage(self.logo2, self.width + self.padding, 0, width=self.width, height=self.height)


# ---------------------------
# PDF GENERATION
# ---------------------------
def generate_pdf(student, payment, items, amount_paid):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    story = []

    # Side-by-side logos
    try:
        story.append(TwoLogos("iStar_logo.png", "istar_logo2.png", width=80, height=80, padding=15))
        story.append(Spacer(1, 16))
    except:
        story.append(Paragraph("<b>[LOGOS MISSING]</b>", styles["Normal"]))

    # Title block
    story.append(Paragraph("<b>iStar Smart Kids & Spacebot Ltd</b>", styles["Title"]))
    story.append(Paragraph("Robotics • Coding • Space Technology", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Receipt Information
    story.append(Paragraph(f"<b>Student:</b> {student}", styles["Normal"]))
    story.append(Paragraph(f"<b>Payment Method:</b> {payment}", styles["Normal"]))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d %B %Y')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Receipt ID:</b> R-{datetime.now().strftime('%Y%m%d%H%M%S')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Table
    table_data = [["Program", "Qty", "Price (GHS)", "Total (GHS)"]]
    grand_total = 0

    for item in items:
        table_data.append([
            item["name"],
            str(item["qty"]),
            f"{item['price']:.2f}",
            f"{item['total']:.2f}"
        ])
        grand_total += item["total"]

    # Calculate Balance and Status
    balance = grand_total - amount_paid
    if balance <= 0:
        balance = 0.0
        status_text = "Fully Paid"
    else:
        status_text = "Part Payment"

    # Append totals and status to table
    table_data.append(["", "", "Grand Total", f"GHS {grand_total:.2f}"])
    table_data.append(["", "", "Amount Paid", f"GHS {amount_paid:.2f}"])
    table_data.append(["", "", "Balance", f"GHS {balance:.2f}"])
    table_data.append(["", "", "Status", status_text])

    table = Table(table_data, colWidths=[60*mm, 20*mm, 35*mm, 35*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        # Bold the Total/Status rows at the bottom
        ('FONTNAME', (2, -4), (-1, -1), 'Helvetica-Bold'),
    ]))

    story.append(table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Thank you for choosing iStar Smart Kids & Spacebot Ltd!</b>", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ---------------------------
# GENERATE PDF BUTTON
# ---------------------------
if len(st.session_state.receipt_items) > 0:
    
    # Calculate current total for default input value
    current_total = sum(item['total'] for item in st.session_state.receipt_items)
    
    # NEW INPUT: Amount Paid
    amount_paid = st.number_input("Amount Paid (GHS)", min_value=0.0, value=float(current_total), step=50.0)

    if st.button("Generate PDF Receipt"):
        pdf = generate_pdf(student_name, payment_method, st.session_state.receipt_items, amount_paid)
        st.download_button(
            "📥 Download Receipt PDF",
            data=pdf,
            file_name=f"receipt_{student_name}.pdf"
        )
else:
    st.warning("Add at least one program before generating a receipt.")


# ---------------------------
# RESET BUTTON
# ---------------------------
if st.button("Clear Receipt"):
    st.session_state.receipt_items = []
    st.success("Receipt cleared!")
