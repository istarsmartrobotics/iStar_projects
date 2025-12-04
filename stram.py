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
st.set_page_config(page_title="Spacebot Ltd", page_icon="🚀", layout="wide")
BASE_DIR = Path(__file__).parent
STUDENTS_FILE = BASE_DIR / "students.csv"
CONTACTS_FILE = BASE_DIR / "contacts.csv"

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
    msg["From"] = f"Spacebot Ltd <{SENDER_EMAIL}>"
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
        "image": "iStar 2.jpg" 
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
        "image": "https://images.unsplash.com/photo-1603732551681-2e91159b9dc2" 
    },
    "Space Technology": {
        "tag": "Astronomy and practical space concepts",
        "outline": ["Space science", "Satellites & orbits", "Rockets", "Space missions", "Model rocket design"],
        "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa"
    }
}

# -------------------- NAVIGATION (Tabs FIRST) --------------------
tab_home, tab_programs, tab_contact = st.tabs(["🏠 Home", "🎓 Programs", "📬 Contact Us"])

# -------------------- HOME TAB --------------------
with tab_home:
    # --- LOGO & HEADER ---
    col_spacer1, col_logo, col_spacer2 = st.columns([1, 1, 1])
    with col_logo:
        try:
            st.image("iStar_logo.png", width=150) 
        except:
            pass 

    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='color:#2F80ED; margin:0;'>Spacebot Limited</h1>
        <p style='color:gray;'><i>Innovating the Future with STEM</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- CONTENT ---
    st.markdown("### 🚀 Welcome to Spacebot")
    st.write("We nurture creativity, curiosity, and innovation in kids through **hands-on STEM learning**.")
    
    st.write("") 
    
    # IMAGES: Thumbnails side by side
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**🤝 Teamwork**")
        try:
            st.image("Teamwork.jpeg", width=300, caption="Building Together")
        except:
            st.info("Image not found: Teamwork.jpeg")
            
    with c2:
        st.markdown("**💡 Innovation**")
        try:
            st.image("Innovation.jpeg", width=300, caption="Creative Solutions")
        except:
            st.info("Image not found: Innovation.jpeg")

    st.markdown("---")
    st.markdown("### 🌠 Our Vision")
    st.info("To empower every child to think critically, innovate boldly, and impact the world through science and technology.")

# -------------------- PROGRAMS TAB --------------------
with tab_programs:
    st.subheader("🎓 Explore Our Programs")
    
    for name, meta in PROGRAMS.items():
        st.markdown("---")
        p_col1, p_col2 = st.columns([1, 3])
        
        with p_col1:
            try:
                st.image(meta["image"], width=200) 
            except:
                st.error("Image missing")
        
        with p_col2:
            st.markdown(f"### {name}")
            st.write(f"_{meta['tag']}_")
            
            with st.expander("View Outline"):
                for item in meta["outline"]:
                    st.write(f"- {item}")
            
            # Registration Popup
            with st.popover(f"Register for {name}"):
                st.markdown(f"**Join {name}**")
                with st.form(f"reg_{name}"):
                    r_name = st.text_input("Name")
                    r_email = st.text_input("Email")
                    r_pass = st.text_input("Password", type="password")
                    sub = st.form_submit_button("Submit")
                
                if sub:
                    if r_name and r_email:
                        # Check duplicate
                        df = pd.read_csv(STUDENTS_FILE)
                        if r_email in df["Email"].astype(str).tolist():
                            st.warning("Email taken.")
                        else:
                            sid = generate_student_id()
                            reg_at = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
                            row = {"StudentID": sid, "Name": r_name, "Email": r_email, 
                                   "PasswordHash": hash_password(r_pass), "Program": name, "RegisteredAt": reg_at}
                            append_csv(STUDENTS_FILE, row)
                            st.success(f"Registered! ID: {sid}")
                            
                            send_email_plain(r_email, "Welcome to Spacebot", f"Welcome {r_name} to {name}!\nID: {sid}")
                            
                            csv_io = io.StringIO()
                            pd.read_csv(STUDENTS_FILE).to_csv(csv_io, index=False)
                            send_email_plain(SENDER_EMAIL, f"New: {r_name}", "New student.", attachment=csv_io, filename="db.csv")

# -------------------- CONTACT TAB (Final) --------------------
with tab_contact:
    st.header("📬 Get in Touch")
    st.write("We are excited to have you visit us or reach out online!")
    st.markdown("---")

    # Using columns to create a "Grid" look for the colorful boxes
    col1, col2 = st.columns(2)

    with col1:
        # Blue Box
        st.info("""
        **📍 Visit Our Center:**  
        Spacebot Limited  
        Kasoa, Timber Market Road  
        Accra, Ghana
        """)
        
        # Yellow Box
        st.warning("""
        **📞 WhatsApp & Calls:**  
        [Tap to Chat: +233 20 477 6107](https://wa.me/233204776107)
        """)

    with col2:
        # Green Box
        st.success("""
        **🇬🇭 Digital Address:**  
        CX-042-4188
        """)

        # Red Box
        st.error("""
        **📧 Email Us:**  
        istarsmartrobotics@gmail.com
        """)

    st.markdown("---")
    st.caption(f"© {datetime.now().year} Spacebot Limited | Built with Streamlit")
