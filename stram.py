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
st.set_page_config(page_title="iStar Smart Kids", page_icon="🎓", layout="wide")
BASE_DIR = Path(__file__).parent
STUDENTS_FILE = BASE_DIR / "students.csv"
CONTACTS_FILE = BASE_DIR / "contacts.csv"
ANALYTICS_LOG = BASE_DIR / "analytics.log"

LOCAL_TZ = pytz.timezone("Africa/Accra")

# --- GMAIL CONFIGURATION ---
SENDER_EMAIL = "istarsmartrobotics@gmail.com"
# The password you provided (spaces removed automatically for safety)
APP_PASSWORD = "fdqz bspu bqxc qiiu".replace(" ", "")

# -------------------- HELPERS --------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def ensure_files():
    if not STUDENTS_FILE.exists():
        pd.DataFrame(columns=["StudentID","Name","Email","PasswordHash","Program","RegisteredAt"]).to_csv(STUDENTS_FILE, index=False)
    if not CONTACTS_FILE.exists():
        pd.DataFrame(columns=["Name","Email","Message","SubmittedAt"]).to_csv(CONTACTS_FILE, index=False)
    if not ANALYTICS_LOG.exists():
        with open(ANALYTICS_LOG, "w", encoding="utf-8") as f:
            f.write("timestamp,event,meta\n")

def log_event(event: str, meta=""):
    now = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    with open(ANALYTICS_LOG, "a", encoding="utf-8") as f:
        f.write(f"{now},{event},{meta}\n")

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
    return f"ISTAR{year}-{count:03d}"

def send_email_plain(to_email: str, subject: str, body: str, attachment=None, filename=""):
    """
    Send email (with optional CSV attachment) via Gmail SMTP_SSL.
    """
    if not APP_PASSWORD:
        st.error("Email configuration error: Password missing.")
        return False

    msg = EmailMessage()
    msg["From"] = f"iStar Smart Kids <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach CSV if provided
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
        # Gmail requires SSL on port 465
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
        "outline": ["Intro to robotics & components", "Sensors & actuators", "Microcontrollers (Arduino / MicroPython)", "Mobile/line-following robot project", "Final autonomous challenge"],
        # KEPT: Your local image path
        "image": "iStar 2.jpg"
    },
    "Python Programming": {
        "tag": "From basics to project-based coding",
        "outline": ["Python basics: variables, loops, functions", "Lists, dicts & files", "Mini apps (calculator, quiz)", "Intro to Pandas & data handling", "Build a Streamlit app"],
        "image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"
    },
    "Data Analysis": {
        "tag": "Collect, clean, visualize and tell data stories",
        "outline": ["Intro to data & statistics", "Pandas basics & cleaning", "Visualization with Matplotlib", "Simple analyses & reporting", "Project: data storytelling"],
        # KEPT: New Data Analysis Image
        "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71"
    },
    "Electronics": {
        "tag": "Circuits, sensors, and physical computing",
        "outline": ["Basic electronics & components", "Breadboard projects", "Microcontroller interfacing", "Simple IoT concepts", "Final interactive device"],
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475"
    },
    "Space Technology": {
        "tag": "Astronomy and practical space concepts",
        "outline": ["Intro to space science & astronomy", "Satellites & orbits", "Rockets & propulsion basics", "Space missions & history", "Design a small model rocket"],
        "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa"
    }
}

# -------------------- NAVIGATION --------------------
st.sidebar.title("Navigate")
menu = st.sidebar.radio("", ["Home", "Programs", "Contact"])

# -------------------- HOME --------------------
if menu == "Home":
    log_event("view_home")
    
    # --- UPDATED HEADER WITH ROBOT BESIDE TEXT ---
    col_text, col_robot = st.columns([2.5, 1]) # Text takes more space, Robot takes less
    
    with col_text:
        st.markdown("""
        <div style='padding-top: 20px;'>
            <h1 style='color:#2F80ED;'>🌟 Welcome to <b>iStar Smart Kids</b></h1>
            <h3 style='color:#117A65;'>Inspiring Young Innovators in Robotics, Coding & Space Tech 🚀</h3>
        </div>
        """, unsafe_allow_html=True)
        
    with col_robot:
        # The new Cute Robot image
        st.image("https://img.freepik.com/premium-vector/robot-emoji-white-background_889056-45647.jpg?w=2000", width=200)

    st.markdown("---")

    # --- REST OF HOME PAGE (Original Layout) ---
    col1, col2 = st.columns([1.1, 1])
    with col1:
        st.image("https://images.unsplash.com/photo-1519389950473-47ba0277781c", caption="Team Projects in Action", use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1521790797524-b2497295b8a0", caption="Exploring Innovation", use_container_width=True)
    
    st.markdown("### 💡 Our Mission")
    st.write("At iStar, we nurture creativity, curiosity, and innovation in kids through **hands-on STEM learning**.")
    st.markdown("### 🌠 Vision")
    st.info("To empower every child to think critically, innovate boldly, and impact the world through science and technology.")

# -------------------- PROGRAMS + REGISTRATION --------------------
elif menu == "Programs":
    log_event("view_programs")
    st.header("🎓 Explore Our Programs")

    params = st.query_params
    selected_program = params.get("program", None)

    for name, meta in PROGRAMS.items():
        # Using columns to control image size
        col1, col2 = st.columns([1, 2])
        with col1:
            try:
                st.image(meta["image"], use_container_width=True)
            except:
                st.error(f"Image not found: {meta['image']}")
        with col2:
            st.subheader(name)
            st.write(f"_{meta['tag']}_")
            with st.expander(f"📘 View {name} Outline"):
                for i, item in enumerate(meta["outline"], start=1):
                    st.write(f"{i}. {item}")
            
            if st.button(f"Register for {name}", key=name):
                st.query_params.update({"program": name})

        # Registration Form (Appears below the selected program)
        if selected_program == name:
            st.divider()
            st.markdown(f"### 📝 Register for {name}")
            with st.form(f"register_form_{name}"):
                r_name = st.text_input("Full Name", key=f"name_{name}")
                r_email = st.text_input("Email Address", key=f"email_{name}")
                r_password = st.text_input("Create Password", type="password", key=f"pass_{name}")
                submitted = st.form_submit_button("Register Now")
            
            if submitted:
                if not (r_name and r_email and r_password):
                    st.error("❌ Please fill in all fields.")
                else:
                    # 1. Check duplicate
                    df = pd.read_csv(STUDENTS_FILE)
                    if r_email in df["Email"].astype(str).tolist():
                        st.warning("⚠️ Email already registered.")
                    else:
                        # 2. Save to CSV
                        student_id = generate_student_id()
                        registered_at = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
                        row = {
                            "StudentID": student_id, 
                            "Name": r_name, 
                            "Email": r_email,
                            "PasswordHash": hash_password(r_password), 
                            "Program": name,
                            "RegisteredAt": registered_at
                        }
                        append_csv(STUDENTS_FILE, row)
                        
                        st.success(f"🎉 Registration complete! Student ID: {student_id}")
                        st.balloons()

                        # 3. Email Student
                        student_msg = f"Hello {r_name},\n\nWelcome to iStar Smart Kids!\nYou have successfully registered for {name}.\nStudent ID: {student_id}\n\nSee you in class!"
                        send_email_plain(r_email, "Registration Confirmed - iStar", student_msg)

                        # 4. Email Admin (YOU) with Database Attachment
                        st.info("📨 Syncing database to admin email...")
                        
                        # Read the FRESH file including the new user
                        df_updated = pd.read_csv(STUDENTS_FILE)
                        csv_buffer = io.StringIO()
                        df_updated.to_csv(csv_buffer, index=False)
                        
                        admin_msg = f"New Registration Alert!\n\nName: {r_name}\nProgram: {name}\n\nAttached is the updated student database."
                        
                        sent_admin = send_email_plain(
                            SENDER_EMAIL, # Send TO yourself
                            f"New Sign-up: {r_name}", 
                            admin_msg, 
                            attachment=csv_buffer, 
                            filename="students_database.csv"
                        )

                        if sent_admin:
                            st.toast("Database emailed to admin successfully!", icon="✅")
                        else:
                            st.error("Could not email database to admin.")

                        log_event("register", meta=r_email)
        st.divider()

# -------------------- CONTACT --------------------
elif menu == "Contact":
    log_event("view_contact")
    st.header("📬 Contact Us")
    st.markdown("""
    ### 📱 Reach Out to Us  
    Have questions or want to learn more?  
    👉 **Contact us on WhatsApp at [📞 +233 20 477 6107](https://wa.me/233204776107)**  
    We’ll be happy to assist you!
    """)
    st.markdown("---")
    st.markdown(f"""
    <p style='text-align:center; color:gray;'>
    © {datetime.now().year} iStar Smart Kids | Inspiring Young Innovators 🌠<br>
    <small>Built with ❤️ using Streamlit — Local time: {datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")}</small>
    </p>

    """, unsafe_allow_html=True)
