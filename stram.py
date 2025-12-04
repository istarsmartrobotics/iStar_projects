import streamlit as st
import pandas as pd
from pathlib import Path
import hashlib
from datetime import datetime
import pytz
import smtplib
from email.message import EmailMessage
import io

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Spacbot Ltd", page_icon="🚀", layout="wide")
BASE_DIR = Path(__file__).parent
STUDENTS_FILE = BASE_DIR / "students.csv"
CONTACTS_FILE = BASE_DIR / "contacts.csv"
ANALYTICS_LOG = BASE_DIR / "analytics.log"

LOCAL_TZ = pytz.timezone("Africa/Accra")

# --- GMAIL CONFIGURATION ---
SENDER_EMAIL = "istarsmartrobotics@gmail.com"
APP_PASSWORD = "fdqz bspu bqxc qiiu".replace(" ", "")

# -------------------- HELPERS --------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def ensure_files():
    if not STUDENTS_FILE.exists():
        pd.DataFrame(columns=["StudentID","Name","Email","PasswordHash","Program","RegisteredAt"]).to_csv(STUDENTS_FILE, index=False)
    if not CONTACTS_FILE.exists():
        pd.DataFrame(columns=["Name","Email","Message","SubmittedAt"]).to_csv(CONTACTS_FILE, index=False)

def append_csv(path: Path, row: dict):
    df = pd.read_csv(path) if path.exists() else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)

def generate_student_id():
    if STUDENTS_FILE.exists():
        df = pd.read_csv(STUDENTS_FILE)
        count = len(df) + 1
    else:
        count = 1
    year = datetime.now().year
    return f"SPAC{year}-{count:03d}"

def send_email_plain(to_email: str, subject: str, body: str, attachment=None, filename=""):
    if not APP_PASSWORD:
        st.error("Email configuration error: Password missing.")
        return False
    msg = EmailMessage()
    msg["From"] = f"Spacbot Ltd <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment:
        try:
            if isinstance(attachment, bytes):
                data_bytes = attachment
            elif isinstance(attachment, str):
                data_bytes = attachment.encode("utf-8")
            else:
                data_bytes = attachment.getvalue().encode("utf-8")
            msg.add_attachment(data_bytes, maintype="text", subtype="csv", filename=filename or "attachment.csv")
        except Exception as e:
            print(f"Attachment error: {e}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

ensure_files()

# -------------------- PROGRAM DATA --------------------
PROGRAMS = {
    "Robotics": {
        "tag": "Hands-on robotics & mechatronics",
        "outline": ["Intro to robotics", "Sensors & actuators", "Microcontrollers", "Mobile robot project", "Autonomous challenge"],
        "image": "iStar 2.jpg" # Your uploaded file
    },
    "Python Programming": {
        "tag": "From basics to project-based coding",
        "outline": ["Python basics", "Lists, dicts & files", "Mini apps", "Intro to Pandas", "Build a Streamlit app"],
        "image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"
    },
    "Data Analysis": {
        "tag": "Collect, clean, visualize and tell data stories",
        "outline": ["Intro to data", "Pandas basics", "Visualization", "Simple analyses", "Data storytelling project"],
        "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71"
    },
    "Electronics": {
        "tag": "Circuits, sensors, and physical computing",
        "outline": ["Basic electronics", "Breadboard projects", "Microcontrollers", "IoT concepts", "Interactive device"],
        # UPDATED: Real, high-quality electronics image
        "image": "https://images.unsplash.com/photo-1563770095-39d468f9a51d" 
    },
    "Space Technology": {
        "tag": "Astronomy and practical space concepts",
        "outline": ["Space science", "Satellites & orbits", "Rockets", "Space missions", "Model rocket design"],
        "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa"
    }
}

# -------------------- HEADER & LOGO --------------------
# Center the Logo
col_l, col_c, col_r = st.columns([1, 1, 1])
with col_c:
    try:
        st.image("iStar_logo.png", use_container_width=True)
    except:
        pass # If logo fails to load, just show title

st.markdown("""
<h1 style='text-align: center; color:#2F80ED;'>Spacbot Ltd</h1>
<p style='text-align: center; color:gray;'><i>Innovating the Future with Robotics, Coding & Space Tech</i></p>
""", unsafe_allow_html=True)

# -------------------- TOP NAVIGATION (Tabs) --------------------
# Replaces the sidebar slider with clickable tabs
tab_home, tab_programs, tab_contact = st.tabs(["🏠 Home", "🎓 Programs", "📬 Contact"])

# -------------------- HOME TAB --------------------
with tab_home:
    st.write("") # Spacer
    st.markdown("### 💡 Our Mission")
    st.write("At Spacbot Ltd, we nurture creativity, curiosity, and innovation in kids through **hands-on STEM learning**.")
    
    st.write("---")
    
    # IMAGES: Side by side, controlled size
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Teamwork & Collaboration**")
        try:
            st.image("Teamwork.jpeg", use_container_width=True, caption="Building Together")
        except:
            st.info("Image not found: Teamwork.jpeg")
            
    with c2:
        st.markdown("**Innovation & Creativity**")
        try:
            st.image("Innovation.jpeg", use_container_width=True, caption="Creative Solutions")
        except:
            st.info("Image not found: Innovation.jpeg")

    st.write("---")
    st.markdown("### 🌠 Vision")
    st.info("To empower every child to think critically, innovate boldly, and impact the world through science and technology.")

# -------------------- PROGRAMS TAB --------------------
with tab_programs:
    st.header("Explore Our Programs")
    st.write("Select a program below to see details and register.")

    # Loop through programs
    for name, meta in PROGRAMS.items():
        st.markdown("---")
        p_col1, p_col2 = st.columns([1, 2])
        
        with p_col1:
            try:
                st.image(meta["image"], use_container_width=True)
            except:
                st.error(f"Image missing: {meta['image']}")
        
        with p_col2:
            st.subheader(name)
            st.write(f"_{meta['tag']}_")
            
            with st.expander(f"📘 View {name} Course Outline"):
                for item in meta["outline"]:
                    st.write(f"- {item}")
            
            # Registration embedded directly here
            with st.popover(f"📝 Register for {name}"):
                st.markdown(f"**Join the {name} Class**")
                with st.form(f"reg_{name}"):
                    r_name = st.text_input("Full Name")
                    r_email = st.text_input("Email")
                    r_pass = st.text_input("Password", type="password")
                    sub = st.form_submit_button("Register Now")
                
                if sub:
                    if r_name and r_email and r_pass:
                        # Check duplicate
                        df = pd.read_csv(STUDENTS_FILE)
                        if r_email in df["Email"].astype(str).tolist():
                            st.warning("Email already registered.")
                        else:
                            # Save
                            sid = generate_student_id()
                            reg_at = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
                            row = {"StudentID": sid, "Name": r_name, "Email": r_email, 
                                   "PasswordHash": hash_password(r_pass), "Program": name, "RegisteredAt": reg_at}
                            append_csv(STUDENTS_FILE, row)
                            
                            st.success(f"Welcome, {r_name}! ID: {sid}")
                            
                            # Email Student
                            send_email_plain(r_email, "Welcome to Spacbot Ltd", 
                                             f"Hi {r_name},\n\nYou are registered for {name}.\nID: {sid}\n\nWelcome aboard!")
                            
                            # Email Admin
                            df_new = pd.read_csv(STUDENTS_FILE)
                            csv_io = io.StringIO()
                            df_new.to_csv(csv_io, index=False)
                            send_email_plain(SENDER_EMAIL, f"New Sign-up: {r_name}", 
                                             f"New student in {name}.", attachment=csv_io, filename="database.csv")
                    else:
                        st.error("Please fill all fields.")

# -------------------- CONTACT TAB --------------------
with tab_contact:
    st.header("📬 Get in Touch")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 📍 Visit Us
        We are located in Accra, Ghana.
        Open for visits: Mon-Fri, 9am - 5pm.
        """)
    with c2:
        st.markdown("""
        ### 📱 Contact Info
        Have questions?  
        👉 **WhatsApp:** [📞 +233 20 477 6107](https://wa.me/233204776107)  
        👉 **Email:** istarsmartrobotics@gmail.com
        """)
    
    st.markdown("---")
    st.markdown(f"<p style='text-align:center; color:gray;'>© {datetime.now().year} Spacbot Ltd</p>", unsafe_allow_html=True)
