import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
import time
import re
import calendar
from datetime import date, datetime
import zipfile

CSV_FILE = "student-dataset.csv"
EVENTS_FILE = "events.csv"

COLUMNS = [
    "id",
    "student_id",
    "name",
    "gender",
    "place",
    "age",
    "rank",
    "physics",
    "chemistry",
    "maths",
    "total",
    "average",
    "attendance",
]

# Initialize session state variables
if "lang" not in st.session_state:
    st.session_state.lang = "English"

# --- URL Parameter Routing Sync (?page=...) ---
VALID_PAGES = ["analytics", "register", "records", "events", "chat"]
url_page = st.query_params.get("page", None)

if url_page in VALID_PAGES:
    st.session_state.active_tab_id = url_page
elif "active_tab_id" not in st.session_state:
    st.session_state.active_tab_id = "analytics"
    st.query_params["page"] = "analytics"

# --- Translation Dictionary ---
TRANSLATIONS = {
    "English": {
        "settings": "⚙️ Settings",
        "language": "🌐 Language",
        "dark_mode": "🌙 Dark Mode",
        "navigation": "Navigation",
        "alerts_title": "⚠️ Needs Attention",
        "pass_rates_title": "🎯 Subject Pass Rates",
        "att_alert": "students Attendance < 75%",
        "att_ok": "Attendance rates healthy (≥ 75%)",
        "fail_alert": "students failing (< 40% avg)",
        "fail_ok": "All students passing (≥ 40%)",
        "physics": "Physics",
        "chemistry": "Chemistry",
        "maths": "Maths",
        "nav_analytics": "📊 Analytics Dashboard",
        "nav_register": "📝 Register New Student",
        "nav_records": "📁 View All Records",
        "nav_events": "📅 Academic Calendar & Events",
        "nav_chat": "💬 Student AI Assistant",
        "events_title": "📅 Academic Events & Calendar",
        "add_event_title": "➕ Add New Event",
        "event_name": "Event Title",
        "event_date": "Event Date",
        "save_event": "Save Event to Calendar",
        "upcoming_events": "Upcoming Scheduled Events",
        "no_events": "No events scheduled yet.",
        "dashboard_title": "Student Performance Dashboard 🎓",
        "total_students": "Total Students",
        "class_average": "Class Average",
        "avg_attendance": "Avg Attendance",
        "highest_total": "Highest Total",
        "class_topper": "Class Topper",
        "top_score": "Top Score",
        "no_records": "No records loaded.",
        "no_student_data": "No student data available yet. Please add students using 'Register New Student'.",
        "chart_box": "<b>Subject Score Spread & Difficulty</b>",
        "chart_top10": "<b>Top 10 High Achievers (Rank Order)</b>",
        "chart_scatter": "<b>Attendance vs. Academic Average</b>",
        "chart_gender_subj": "<b>Average Marks by Gender</b>",
        "chart_gender": "<b>Overall Gender Distribution</b>",
        "chart_geo": "<b>Student Geographical Distribution</b>",
        "chart_heatmap": "Metric & Subject Correlation Heatmap",
        "chart_line": "Score Progression Across Cohort",
        "leaderboard": "🏆 Class Leaderboard",
        "enrollment_form": "📝 Enrollment Form",
        "general_info": "General Info",
        "internal_id": "Internal ID",
        "student_id": "Student ID",
        "full_name": "Full Name",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "demographics": "Demographics",
        "place": "Place / Location",
        "age": "Age",
        "attendance_pct": "Attendance Percentage (%)",
        "academic_marks": "Academic Marks",
        "physics_marks": "Physics Marks",
        "chemistry_marks": "Chemistry Marks",
        "maths_marks": "Maths Marks",
        "calculated_rank": "Calculated Rank (Live)",
        "calculated_total": "Calculated Total",
        "calculated_avg": "Calculated Average",
        "projected_rank": "Projected Rank",
        "save_student": "Save Student Record",
        "view_records_title": "🗂️ Student Records",
        "download_csv": "📥 Download CSV",
        "download_excel": "📊 Download Excel (.xlsx)",
        "empty_dataset": "The dataset is currently empty.",
        "attendance_axis": "Attendance Rate (%)",
        "academic_avg_axis": "Academic Average (%)",
        "cohort_order": "Student Cohort Order",
        "total_score_label": "Total Score",
        "chat_title": "💬 Student Data Assistant",
        "chat_placeholder": "Ask anything (e.g., 'Who is the topper?', 'List students from Brazil', 'Lowest marks in maths')",
        "chat_welcome": "Hello! I can answer questions about students, marks, rankings, and attendance. How can I help?",
        "filter_location": "Filter by Location",
        "all_locations": "All Locations",
        "filter_gender": "Filter by Gender",
        "all_genders": "All Genders",
        "filter_attendance": "Attendance % Range",
        "reset_filters": "🔄 Reset Filters",
        "no_filter_match": "No students match the selected filter criteria."
    },
    "العربية": {
        "settings": "⚙️ الإعدادات",
        "language": "🌐 اللغة",
        "dark_mode": "🌙 الوضع الداكن",
        "navigation": "التنقل",
        "alerts_title": "⚠️ تنبيهات المتابعة",
        "pass_rates_title": "🎯 نسب النجاح في المواد",
        "att_alert": "طلاب بنسبة حضور أقل من 75%",
        "att_ok": "نسب الحضور ممتازة (≥ 75%)",
        "fail_alert": "طلاب دون درجة النجاح (< 40%)",
        "fail_ok": "جميع الطلاب ناجحون (≥ 40%)",
        "physics": "الفيزياء",
        "chemistry": "الكيمياء",
        "maths": "الرياضيات",
        "nav_analytics": "📊 لوحة التحليلات",
        "nav_register": "📝 تسجيل طالب جديد",
        "nav_records": "📁 عرض جميع السجلات",
        "nav_events": "📅 التقويم والفعاليات الأكاديمية",
        "nav_chat": "💬 المساعد الذكي للطلاب",
        "events_title": "📅 التقويم والفعاليات المدرسية",
        "add_event_title": "➕ إضافة فعالية جديدة",
        "event_name": "اسم الفعالية",
        "event_date": "تاريخ الفعالية",
        "save_event": "حفظ الفعالية في التقويم",
        "upcoming_events": "الفعاليات القادمة المجدولة",
        "no_events": "لا توجد فعاليات مجدولة بعد.",
        "dashboard_title": "🎓 لوحة متابعة أداء الطلاب",
        "total_students": "إجمالي الطلاب",
        "class_average": "متوسط الفصل",
        "avg_attendance": "متوسط الحضور",
        "highest_total": "أعلى مجموع",
        "class_topper": "الأول على الفصل",
        "top_score": "أعلى درجة",
        "no_records": "لا توجد سجلات محملة.",
        "no_student_data": "لا تتوفر بيانات للطلاب بعد. يرجى إضافة طلاب باستخدام 'تسجيل طالب جديد'.",
        "chart_box": "<b>توزيع درجات المواد ومستوى الصعوبة</b>",
        "chart_top10": "<b>أفضل 10 طلاب متفوقين (حسب الترتيب)</b>",
        "chart_scatter": "<b>نسبة الحضور مقابل المعدل الأكاديمي</b>",
        "chart_gender_subj": "<b>متوسط الدرجات حسب الجنس</b>",
        "chart_gender": "<b>توزيع الطلاب حسب الجنس</b>",
        "chart_geo": "<b>التوزيع الجغرافي للطلاب</b>",
        "chart_heatmap": "خريطة الارتباط بين المواد والمقاييس",
        "chart_line": "تدرج الدرجات عبر دفعة الطلاب",
        "leaderboard": "🏆 قائمة أوائل الفصل",
        "enrollment_form": "📝 نموذج تسجيل الطالب",
        "general_info": "المعلومات العامة",
        "internal_id": "الرقم التعريفي الداخلي",
        "student_id": "رقم الطالب",
        "full_name": "الاسم الكامل",
        "gender": "الجنس",
        "male": "ذكر",
        "female": "أنثى",
        "other": "آخر",
        "demographics": "البيانات الديموغرافية",
        "place": "المكان / المدينة",
        "age": "العمر",
        "attendance_pct": "نسبة الحضور (%)",
        "academic_marks": "الدرجات الأكاديمية",
        "physics_marks": "درجات الفيزياء",
        "chemistry_marks": "درجات الكيمياء",
        "maths_marks": "درجات الرياضيات",
        "calculated_rank": "الترتيب المحسوب (مباشر)",
        "calculated_total": "المجموع المحسوب",
        "calculated_avg": "المتوسط المحسوب",
        "projected_rank": "الترتيب المتوقع",
        "save_student": "حفظ سجل الطالب",
        "view_records_title": "🗂️ سجلات الطلاب",
        "download_csv": "📥 تحميل CSV",
        "download_excel": "📊 تحميل Excel (.xlsx)",
        "empty_dataset": "مجموعة البيانات فارغة حالياً.",
        "attendance_axis": "معدل الحضور (%)",
        "academic_avg_axis": "المعدل الأكاديمي (%)",
        "cohort_order": "ترتيب الطلاب في الدفعة",
        "total_score_label": "المجموع الكلي",
        "chat_title": "💬 المساعد الذكي لبيانات الطلاب",
        "chat_placeholder": "اسأل أي شيء (مثال: 'من هو الأول؟', 'طلاب من البرازيل', 'أقل درجة في الرياضيات')",
        "chat_welcome": "مرحباً! يمكنني الإجابة عن استفساراتك حول درجات الطلاب، الترتيب، والغياب. كيف يمكنني مساعدتك؟",
        "filter_location": "تصفية حسب المنطقة",
        "all_locations": "جميع المناطق",
        "filter_gender": "تصفية حسب الجنس",
        "all_genders": "جميع الفئات",
        "filter_attendance": "نطاق نسبة الحضور (%)",
        "reset_filters": "🔄 إعادة تعيين التصفية",
        "no_filter_match": "لا يوجد طلاب يطابقون معايير التصفية المحددة."
    }
}

t = TRANSLATIONS[st.session_state.lang]

def load_data():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)
        return df
    df = pd.read_csv(CSV_FILE)
    numeric_cols = ["id", "age", "rank", "physics", "chemistry", "maths", "total", "average", "attendance"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def recalculate_ranks(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty and "total" in df.columns:
        df["rank"] = df["total"].rank(ascending=False, method="min").astype(int)
    return df

def save_data(df):
    df = recalculate_ranks(df)
    try:
        df.to_csv(CSV_FILE, index=False)
        return df, True
    except PermissionError:
        return df, False

# --- Events Data Persistence (CSV) ---
def load_events():
    # If file doesn't exist or is 0 bytes (empty)
    if not os.path.exists(EVENTS_FILE) or os.path.getsize(EVENTS_FILE) == 0:
        df_ev = pd.DataFrame(columns=["id", "event", "Date"])
        df_ev.to_csv(EVENTS_FILE, index=False)
        return df_ev

    try:
        if EVENTS_FILE.endswith(".xlsx"):
            df_ev = pd.read_excel(EVENTS_FILE, engine="openpyxl")
        else:
            df_ev = pd.read_csv(EVENTS_FILE)
    except (zipfile.BadZipFile, pd.errors.EmptyDataError, ValueError, Exception):
        # Fallback & self-heal if the file was corrupted or empty
        df_ev = pd.DataFrame(columns=["id", "event", "Date"])
        df_ev.to_csv(EVENTS_FILE, index=False)
        return df_ev

    df_ev.columns = [str(c).strip() for c in df_ev.columns]
    
    # Ensure required columns exist
    for col in ["id", "event", "Date"]:
        if col not in df_ev.columns:
            df_ev[col] = None

    if "Date" in df_ev.columns:
        df_ev["Date"] = pd.to_datetime(df_ev["Date"], errors="coerce").dt.date

    return df_ev


def save_event(event_name: str, event_date: date):
    df_ev = load_events()
    next_id = 1 if df_ev.empty or df_ev["id"].isna().all() else int(df_ev["id"].max()) + 1
    new_row = pd.DataFrame([{"id": next_id, "event": event_name.strip(), "Date": event_date}])
    df_ev = pd.concat([df_ev, new_row], ignore_index=True)
    
    if EVENTS_FILE.endswith(".xlsx"):
        df_ev.to_excel(EVENTS_FILE, index=False, engine="openpyxl")
    else:
        df_ev.to_csv(EVENTS_FILE, index=False)
        
    return next_id

def query_student_bot(prompt: str, df: pd.DataFrame, lang: str = "English"):
    q = prompt.lower().strip()
    
    if df.empty:
        return ("لا توجد بيانات للطلاب بعد." if lang == "العربية" else "No student records found in the dataset."), None

    # 1. Total Student Count
    if any(k in q for k in ["how many student", "student count", "total student", "number of student", "عدد الطلاب", "كم طالب", "كم عدد الطلاب", "إجمالي الطلاب"]):
        count = len(df)
        if lang == "العربية":
            return f"📊 إجمالي عدد الطلاب المسجلين هو **{count}** طالباً.", None
        return f"📊 The total number of registered students is **{count}**.", None

    # 2. Highest / Top Mark in a Specific Subject
    for sub in ["physics", "chemistry", "maths"]:
        sub_ar = {"physics": "الفيزياء", "chemistry": "الكيمياء", "maths": "الرياضيات"}[sub]
        if sub in q or sub_ar in q:
            if any(k in q for k in ["highest", "max", "top", "best", "أعلى", "اعلى", "أفضل"]):
                max_score = df[sub].max()
                top_students = df[df[sub] == max_score]
                names = ", ".join(top_students["name"].dropna().astype(str).tolist())
                if lang == "العربية":
                    msg = f"🌟 أعلى درجة في مادة **{sub_ar}** هي **{max_score}** وحققها: **{names}**."
                else:
                    msg = f"🌟 The highest mark in **{sub.capitalize()}** is **{max_score}**, achieved by: **{names}**."
                return msg, top_students[["rank", "name", sub, "total"]]
            
            elif any(k in q for k in ["lowest", "min", "worst", "fail", "أقل", "اقل", "ضعيف", "راسب"]):
                min_score = df[sub].min()
                low_students = df[df[sub] == min_score]
                names = ", ".join(low_students["name"].dropna().astype(str).tolist())
                if lang == "العربية":
                    msg = f"📉 أقل درجة في مادة **{sub_ar}** هي **{min_score}** لدى: **{names}**."
                else:
                    msg = f"📉 The lowest mark in **{sub.capitalize()}** is **{min_score}**, scored by: **{names}**."
                return msg, low_students[["rank", "name", sub, "total"]]

    # 3. Overall Class Topper
    if any(k in q for k in ["topper", "rank 1", "highest mark", "highest score", "الأول", "الاول", "المتفوق"]):
        top_row = df.loc[df['total'].idxmax()]
        name = top_row['name']
        score = top_row['total']
        rank = top_row['rank']
        if lang == "العربية":
            msg = f"🏆 **الأول على الفصل** هو **{name}** بمجموع **{score:.0f}/300** والترتيب **#{rank}**."
        else:
            msg = f"🏆 The **Class Topper** is **{name}** with a total score of **{score:.0f}/300** (Rank **#{rank}**)."
        return msg, df[df['name'] == name]

    # 4. Attendance Queries
    if any(k in q for k in ["attendance", "حضور", "غياب"]):
        low_att = df[df['attendance'] < 75].sort_values(by="attendance")
        if any(k in q for k in ["low", "below", "less", "اقل", "أقل", "ضعيف", "غياب"]):
            if lang == "العربية":
                msg = f"⚠️ تم العثور على **{len(low_att)}** طلاب بنسبة حضور أقل من 75%:"
            else:
                msg = f"⚠️ Found **{len(low_att)}** students with attendance below 75%:"
            return msg, low_att
        else:
            avg_att = df['attendance'].mean()
            if lang == "العربية":
                return f"متوسط الحضور العام للفصل هو **{avg_att:.1f}%**.", None
            return f"The overall class average attendance is **{avg_att:.1f}%**.", None

    # 5. Place / Country Search
    places = df['place'].dropna().unique()
    matched_place = next((p for p in places if str(p).lower() in q), None)
    if matched_place:
        place_df = df[df['place'].str.lower() == matched_place.lower()]
        if lang == "العربية":
            msg = f"📍 تم العثور على **{len(place_df)}** طلاب من **{matched_place}**:"
        else:
            msg = f"📍 Found **{len(place_df)}** students from **{matched_place}**:"
        return msg, place_df

    # 6. Specific Student Lookup
    for _, row in df.iterrows():
        student_name = str(row['name']).strip()
        parts = [p.lower() for p in student_name.split() if len(p) > 2]
        if student_name.lower() in q or any(re.search(rf"\b{re.escape(p)}\b", q) for p in parts):
            if lang == "العربية":
                msg = f"📋 بيانات الطالب **{row['name']}**: الترتيب: **#{row['rank']}** | المجموع: **{row['total']:.0f}/300** | الحضور: **{row['attendance']}%** | المكان: **{row['place']}**"
            else:
                msg = f"📋 Details for **{row['name']}**: Rank: **#{row['rank']}** | Total: **{row['total']:.0f}/300** | Attendance: **{row['attendance']}%** | Location: **{row['place']}**"
            return msg, df[df['name'] == row['name']]

    # 7. Fallback
    if lang == "العربية":
        return "لم أتمكن من العثور على نتيجة دقيقة. يمكنك السؤال عن: 'كم عدد الطلاب؟'، 'أعلى درجة في الفيزياء'، 'الأول على الفصل'، أو نسبة الحضور.", None
    return "I couldn't quite find what you're looking for. You can ask: 'How many students are there?', 'Highest mark in physics', 'Who is the topper?', or 'Attendance below 75%'.", None

st.set_page_config(page_title="Student Management & Analytics", layout="wide")

df = load_data()

# -------------------------------------------------------------
# SIDEBAR (Logo + Settings + Unified Navigation + Actionable Alerts)
# -------------------------------------------------------------
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "akumen_logo.svg")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(__file__), "akumen_logo.png")
    
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("## 🎓 **AKUMEN**")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Collapsible Settings
    current_t = TRANSLATIONS[st.session_state.lang]
    with st.expander(current_t["settings"], expanded=False):
        selected_lang = st.selectbox(
            label=current_t["language"],
            options=["English", "العربية"],
            index=0 if st.session_state.lang == "English" else 1,
            key="lang_selector",
        )

        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            st.rerun()

        dark_mode = st.toggle(current_t["dark_mode"], value=False)

    st.markdown("<br>", unsafe_allow_html=True)

    # Placed 'events' directly above 'chat'
    tab_mapping = [
        ("analytics", t["nav_analytics"]),
        ("register", t["nav_register"]),
        ("records", t["nav_records"]),
        ("events", t["nav_events"]),
        ("chat", t["nav_chat"]),
    ]

    st.markdown(f"### {t['navigation']}")
    for tab_id, tab_label in tab_mapping:
        is_active = st.session_state.active_tab_id == tab_id
        if st.button(
            tab_label,
            key=f"nav_btn_{tab_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.active_tab_id = tab_id
            st.query_params["page"] = tab_id
            st.rerun()

    st.markdown("---")

    # --- ACTIONABLE SIDEBAR PANELS ---
    st.markdown(f"### {t['alerts_title']}")
    if not df.empty:
        low_att_count = len(df[df["attendance"] < 75])
        low_marks_count = len(df[df["average"] < 40])

        if low_att_count > 0:
            st.warning(f"**{low_att_count}** {t['att_alert']}")
        else:
            st.success(t["att_ok"])

        if low_marks_count > 0:
            st.error(f"**{low_marks_count}** {t['fail_alert']}")
        else:
            st.success(t["fail_ok"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"### {t['pass_rates_title']}")
        for sub_key in ["physics", "chemistry", "maths"]:
            if sub_key in df.columns:
                pass_pct = float((df[sub_key] >= 40).mean())
                st.write(f"**{t[sub_key]}**: {pass_pct * 100:.0f}%")
                st.progress(pass_pct)
    else:
        st.info(t["no_records"])

# --- RTL Layout Injection for Arabic ---
if st.session_state.lang == "العربية":
    st.markdown(
        """
        <style>
        [data-testid="stMainBlockContainer"], 
        [data-testid="stSidebarContent"],
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        h1, h2, h3, h4, p, label {
            direction: rtl !important;
            text-align: right !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- Dynamic CSS Injection for Cards & Theme ---
theme_css = f"""
<style>
    .stApp {{
        background-color: {"#0e1117" if dark_mode else "#ffffff"};
        color: {"#f0f6fc" if dark_mode else "#31333F"};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {"#161b22" if dark_mode else "#f0f2f6"};
    }}
    h1, h2, h3, h4, h5, h6, label {{
        color: {"#f0f6fc" if dark_mode else "#1e293b"} !important;
    }}
    p, span {{
        color: {"#f0f6fc" if dark_mode else "#31333F"};
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {"#161b22" if dark_mode else "#ffffff"} !important;
        border: 1px solid {"#30363d" if dark_mode else "#e2e8f0"} !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: {"0 4px 14px rgba(0,0,0,0.3)" if dark_mode else "0 2px 8px rgba(0,0,0,0.04)"} !important;
    }}

    [data-testid="stExpander"] {{
        background-color: transparent !important;
        border: none !important;
    }}
    [data-testid="stExpander"] details {{
        background-color: {"#161b22" if dark_mode else "#ffffff"} !important;
        border: 1px solid {"#30363d" if dark_mode else "#e2e8f0"} !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }}
    [data-testid="stExpander"] summary {{
        background-color: {"#21262d" if dark_mode else "#f8fafc"} !important;
        color: {"#f0f6fc" if dark_mode else "#1e293b"} !important;
        border-radius: 8px !important;
        border: none !important;
    }}
    [data-testid="stExpander"] summary:hover {{
        background-color: {"#30363d" if dark_mode else "#f1f5f9"} !important;
    }}
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {{
        color: {"#f0f6fc" if dark_mode else "#1e293b"} !important;
        fill: {"#f0f6fc" if dark_mode else "#1e293b"} !important;
    }}
    [data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
        background-color: {"#161b22" if dark_mode else "#ffffff"} !important;
    }}

    button[kind="secondary"] {{
        background-color: {"#21262d" if dark_mode else "#ffffff"} !important;
        color: {"#f0f6fc" if dark_mode else "#24292f"} !important;
        border: 1px solid {"#30363d" if dark_mode else "#d0d7de"} !important;
    }}
    button[kind="secondary"] p,
    button[kind="secondary"] span {{
        color: {"#f0f6fc" if dark_mode else "#24292f"} !important;
    }}
    button[kind="secondary"]:hover {{
        background-color: {"#30363d" if dark_mode else "#f3f4f6"} !important;
        border-color: {"#8b949e" if dark_mode else "#cbd5e1"} !important;
    }}

    div[data-testid="stChatMessage"] {{
        background-color: {"#161b22" if dark_mode else "#f8fafc"} !important;
        border: 1px solid {"#30363d" if dark_mode else "#e2e8f0"} !important;
        border-radius: 10px !important;
    }}
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] span {{
        color: {"#f0f6fc" if dark_mode else "#1e293b"} !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: {"#58a6ff" if dark_mode else "#2563eb"} !important;
        font-weight: 700;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {"#8b949e" if dark_mode else "#64748b"} !important;
    }}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

def style_chart(fig, height=360):
    fig.update_layout(
        template="plotly_dark" if dark_mode else "plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f0f6fc" if dark_mode else "#334155"),
        margin=dict(l=20, r=20, t=45, b=25),
        height=height
    )
    return fig

# -------------------------------------------------------------
# 1. ANALYTICS DASHBOARD (WITH REAL-TIME CROSS-FILTERING)
# -------------------------------------------------------------
if not df.empty:
    low_att = len(df[df["attendance"] < 75])
    failing = len(df[df["average"] < 40])
    
    if st.session_state.lang == "العربية":
        ticker_text = (
            f"🚨 تنبيه عاجل: {failing} طالب دون درجة النجاح (< 40%) & {low_att} طالب بنسبة حضور حرجة (< 75%)! "
            f"&nbsp;&nbsp;&nbsp;&nbsp;📢 فتح باب التسجيل والقبول للعام الدراسي الجديد! "
            f"&nbsp;&nbsp;&nbsp;&nbsp;📅 آخر موعد لتسليم التقارير الأكاديمية هو الجمعة القادمة."
        )
    else:
        ticker_text = (
            f"🚨 Urgent Alert: {failing} student(s) below passing mark (< 40%) & {low_att} student(s) with critical attendance (< 75%)! "
            f"&nbsp;&nbsp;&nbsp;&nbsp;📢 New Admissions for 2026–2027 are now open! "
            f"&nbsp;&nbsp;&nbsp;&nbsp;📅 Term assessment reports due this Friday."
        )

    st.markdown(
        f"""
        <div style="width: 100%; overflow: hidden; white-space: nowrap; margin-bottom: 8px;">
            <marquee direction="left" scrollamount="7" style="
                color: #ef4444; 
                font-weight: 700; 
                font-size: 1.05rem; 
                letter-spacing: 0.3px;
                background: transparent;
            ">
                {ticker_text}
            </marquee>
        </div>
        """,
        unsafe_allow_html=True
    )

if st.session_state.active_tab_id == "analytics":
    st.title(t["dashboard_title"])
    st.write("")

    if df.empty:
        st.info(t["no_student_data"])
    else:
        if "filter_version" not in st.session_state:
            st.session_state.filter_version = 0

        with st.container(border=True):
            f1, f2, f3, f4 = st.columns([2, 2, 2, 1])

            all_places = sorted([str(p) for p in df["place"].dropna().unique().tolist()])
            selected_places = f1.multiselect(
                t["filter_location"],
                options=all_places,
                default=[],
                placeholder=t["all_locations"],
                key=f"filter_place_{st.session_state.filter_version}"
            )

            all_genders = sorted([str(g) for g in df["gender"].dropna().unique().tolist()])
            selected_genders = f2.multiselect(
                t["filter_gender"],
                options=all_genders,
                default=[],
                placeholder=t["all_genders"],
                key=f"filter_gender_{st.session_state.filter_version}"
            )

            min_att = float(df["attendance"].min()) if not df["attendance"].isna().all() else 0.0
            max_att = float(df["attendance"].max()) if not df["attendance"].isna().all() else 100.0
            att_range = f3.slider(
                t["filter_attendance"],
                min_value=0.0,
                max_value=100.0,
                value=(min_att, max_att),
                step=1.0,
                key=f"filter_att_{st.session_state.filter_version}"
            )

            with f4:
                st.write("")
                st.write("")
                if st.button(t["reset_filters"], use_container_width=True):
                    st.session_state.filter_version += 1
                    st.rerun()

        filtered_df = df.copy()
        if selected_places:
            filtered_df = filtered_df[filtered_df["place"].astype(str).isin(selected_places)]
        if selected_genders:
            filtered_df = filtered_df[filtered_df["gender"].astype(str).isin(selected_genders)]
        filtered_df = filtered_df[
            (filtered_df["attendance"] >= att_range[0]) & 
            (filtered_df["attendance"] <= att_range[1])
        ]

        if filtered_df.empty:
            st.warning(t["no_filter_match"])
        else:
            topper_row = filtered_df.loc[filtered_df['total'].idxmax()]
            topper_name = topper_row.get('name', topper_row.get('student_name', 'Topper'))

            k1, k2, k3, k4, k5 = st.columns(5)
            with k1:
                with st.container(border=True):
                    st.metric(t["total_students"], len(filtered_df))
            with k2:
                with st.container(border=True):
                    st.metric(t["class_average"], f"{filtered_df['average'].mean():.1f}%")
            with k3:
                with st.container(border=True):
                    st.metric(t["avg_attendance"], f"{filtered_df['attendance'].mean():.1f}%")
            with k4:
                with st.container(border=True):
                    st.metric(t["highest_total"], f"{filtered_df['total'].max():.0f} / 300")
            with k5:
                with st.container(border=True):
                    st.html("""
                        <style>
                        div[data-testid="stMetricValue"] > div {
                            font-size: 1.15rem !important;
                            white-space: normal !important;
                            word-break: break-word !important;
                            line-height: 1.25 !important;
                        }
                        </style>
                    """)
                    st.metric(
                        label=t["class_topper"],
                        value=f"🏆 {topper_name}",
                        help=f"{t['highest_total']}: {filtered_df['total'].max():.0f} / 300"
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            r1_c1, r1_c2 = st.columns(2)
            with r1_c1:
                with st.container(border=True):
                    subject_melt = filtered_df.melt(
                        value_vars=["physics", "chemistry", "maths"],
                        var_name="Subject",
                        value_name="Score"
                    )
                    subject_melt["Subject"] = subject_melt["Subject"].str.capitalize()
                    
                    fig_box = px.box(
                        subject_melt,
                        x="Subject",
                        y="Score",
                        color="Subject",
                        title=t["chart_box"],
                        points="outliers"
                    )
                    fig_box.update_layout(showlegend=False, yaxis_range=[0, 105])
                    style_chart(fig_box)
                    st.plotly_chart(fig_box, use_container_width=True)

            with r1_c2:
                with st.container(border=True):
                    top_10 = filtered_df.sort_values(by="total", ascending=False).head(10).sort_values(by="total", ascending=True)
                    fig_top10 = px.bar(
                        top_10,
                        x="total",
                        y="name",
                        orientation="h",
                        title=t["chart_top10"],
                        text="total",
                        color="total",
                        color_continuous_scale=[[0.0, "#38bdf8"], [1.0, "#1e3a5f"]]
                    )
                    fig_top10.update_layout(yaxis_title=None, xaxis_title=t["total_score_label"], coloraxis_showscale=False)
                    style_chart(fig_top10)
                    st.plotly_chart(fig_top10, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            r2_c1, r2_c2 = st.columns(2)
            with r2_c1:
                with st.container(border=True):
                    fig_scatter = px.scatter(
                        filtered_df,
                        x="attendance",
                        y="average",
                        color="gender",
                        size="total",
                        hover_name="name",
                        title=t["chart_scatter"],
                        labels={"attendance": t["attendance_axis"], "average": t["academic_avg_axis"]}
                    )
                    style_chart(fig_scatter)
                    st.plotly_chart(fig_scatter, use_container_width=True)

            with r2_c2:
                with st.container(border=True):
                    gender_perf = filtered_df.groupby("gender")[["physics", "chemistry", "maths"]].mean().reset_index()
                    gender_perf_melted = gender_perf.melt(id_vars="gender", var_name="Subject", value_name="Score")
                    gender_perf_melted["Subject"] = gender_perf_melted["Subject"].str.capitalize()

                    fig_gender_subj = px.bar(
                        gender_perf_melted,
                        x="Subject",
                        y="Score",
                        color="gender",
                        barmode="group",
                        title=t["chart_gender_subj"],
                        text_auto=".1f"
                    )
                    fig_gender_subj.update_layout(yaxis_range=[0, 100])
                    style_chart(fig_gender_subj)
                    st.plotly_chart(fig_gender_subj, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            r3_c1, r3_c2 = st.columns(2)
            with r3_c1:
                with st.container(border=True):
                    fig_gender = px.pie(
                        filtered_df,
                        names="gender",
                        title=t["chart_gender"],
                        hole=0.45
                    )
                    style_chart(fig_gender)
                    st.plotly_chart(fig_gender, use_container_width=True)

            with r3_c2:
                with st.container(border=True):
                    place_counts = filtered_df["place"].value_counts().reset_index()
                    place_counts.columns = ["Place", "Count"]
                    fig_place = px.bar(
                        place_counts,
                        x="Count",
                        y="Place",
                        orientation="h",
                        title=t["chart_geo"],
                        color="Count",
                        color_continuous_scale=[[0.0, "#93c5fd"], [1.0, "#0f172a"]]
                    )
                    fig_place.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
                    style_chart(fig_place)
                    st.plotly_chart(fig_place, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            r4_c1, r4_c2 = st.columns(2)
            with r4_c1:
                with st.container(border=True):
                    numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns
                    corr_matrix = filtered_df[numeric_cols].corr()

                    fig_heatmap = px.imshow(
                        corr_matrix,
                        text_auto=".2f",
                        aspect="auto",
                        color_continuous_scale=[[0.0, "#93c5fd"], [0.5, "#3b82f6"], [1.0, "#1e3a8a"]],
                        title=t["chart_heatmap"]
                    )
                    fig_heatmap.update_layout(
                        margin=dict(l=20, r=20, t=40, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        coloraxis_showscale=False
                    )
                    style_chart(fig_heatmap)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with r4_c2:
                with st.container(border=True):
                    df_sorted = filtered_df.sort_values(by="total", ascending=True).reset_index(drop=True)
                    df_sorted["Student_Index"] = df_sorted.index + 1

                    fig_line = px.line(
                        df_sorted,
                        x="Student_Index",
                        y="total",
                        markers=True,
                        title=t["chart_line"],
                        labels={"Student_Index": t["cohort_order"], "total": t["total_score_label"]}
                    )

                    fig_line.update_traces(
                        line=dict(color="#1e40af", width=3),
                        marker=dict(size=6, color="#2563eb", symbol="circle")
                    )

                    fig_line.add_hline(
                        y=filtered_df['total'].mean(),
                        line_dash="dash",
                        line_color="#ef4444",
                        annotation_text=f"Avg: {filtered_df['total'].mean():.1f}",
                        annotation_position="bottom right"
                    )

                    fig_line.update_layout(
                        margin=dict(l=20, r=20, t=40, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                        yaxis=dict(showgrid=True, gridcolor="#f1f5f9")
                    )
                    style_chart(fig_line)
                    st.plotly_chart(fig_line, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

            st.subheader(t["leaderboard"])
            top_students = filtered_df.sort_values(by="rank", ascending=True)[
                ["rank", "student_id", "name", "gender", "place", "physics", "chemistry", "maths", "total", "average", "attendance"]
            ]
            with st.container(border=True):
                st.dataframe(top_students.reset_index(drop=True), use_container_width=True)

# -------------------------------------------------------------
# 2. REGISTER NEW STUDENT
# -------------------------------------------------------------
elif st.session_state.active_tab_id == "register":
    st.title(t["enrollment_form"])

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader(t["general_info"])
            next_id = 1 if df.empty else int(df["id"].max()) + 1
            st.text_input(t["internal_id"], value=str(next_id), disabled=True)
            student_id = st.text_input(t["student_id"], value=f"AK-{next_id:03d}", disabled=True)
            name = st.text_input(t["full_name"], placeholder="Enter student name")
            
            gender_display = {
                "Male": t["male"],
                "Female": t["female"],
                "Other": t["other"]
            }
            gender = st.selectbox(
                t["gender"],
                options=["Male", "Female", "Other"],
                format_func=lambda x: gender_display[x]
            )

        with col2:
            st.subheader(t["demographics"])
            place = st.text_input(t["place"], placeholder="City or District")
            age = st.number_input(t["age"], min_value=5, max_value=100, value=17, step=1)
            attendance = st.slider(t["attendance_pct"], min_value=0.0, max_value=100.0, value=85.0, step=0.5)

        with col3:
            st.subheader(t["academic_marks"])
            physics = st.number_input(t["physics_marks"], min_value=0.0, max_value=100.0, value=0.0, step=1.0)
            chemistry = st.number_input(t["chemistry_marks"], min_value=0.0, max_value=100.0, value=0.0, step=1.0)
            maths = st.number_input(t["maths_marks"], min_value=0.0, max_value=100.0, value=0.0, step=1.0)

            total = round(physics + chemistry + maths, 2)
            average = round(total / 3.0, 2)

            if total == 0:
                current_rank = 0
            elif df.empty or df["total"].isna().all():
                current_rank = 1
            else:
                current_rank = int((df["total"] > total).sum() + 1)

            st.text_input(t["calculated_rank"], value=str(current_rank), disabled=True)

        st.markdown("---")

        stat_col1, stat_col2, stat_col3 = st.columns(3)
        stat_col1.metric(t["calculated_total"], f"{total} / 300")
        stat_col2.metric(t["calculated_avg"], f"{average}%")
        stat_col3.metric(t["projected_rank"], f"#{current_rank}" if current_rank > 0 else "0")

        submit_btn = st.button(t["save_student"], type="primary", use_container_width=True)

        if submit_btn:
            if not student_id.strip() or not name.strip():
                st.error("Student ID and Full Name are required.")
            elif not df.empty and str(student_id).strip() in df["student_id"].astype(str).values:
                st.error("A student with this Student ID already exists.")
            else:
                new_entry = {
                    "id": next_id,
                    "student_id": student_id.strip(),
                    "name": name.strip(),
                    "gender": gender,
                    "place": place.strip(),
                    "age": int(age),
                    "rank": int(current_rank),
                    "physics": float(physics),
                    "chemistry": float(chemistry),
                    "maths": float(maths),
                    "total": total,
                    "average": average,
                    "attendance": float(attendance),
                }

                combined_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                updated_df, success = save_data(combined_df)

                if success:
                    final_rank = updated_df.loc[
                        updated_df["student_id"].astype(str) == str(student_id).strip(), "rank"
                    ].values[0]

                    st.success(f"Student **{name}** added successfully with Rank **{final_rank}**!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Permission denied: Please close 'student-dataset.csv' in Excel and try again.")

# -------------------------------------------------------------
# 3. VIEW ALL RECORDS
# -------------------------------------------------------------
elif st.session_state.active_tab_id == "records":
    st.title(t["view_records_title"])

    if df.empty:
        st.info(t["empty_dataset"])
    else:
        sorted_df = df.sort_values(by="rank", ascending=True).reset_index(drop=True)
        with st.container(border=True):
            st.dataframe(sorted_df, use_container_width=True)

        csv_data = sorted_df.to_csv(index=False).encode("utf-8")

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            sorted_df.to_excel(writer, index=False, sheet_name="Students")
        excel_data = excel_buffer.getvalue()

        col_csv, col_excel = st.columns(2)

        with col_csv:
            st.download_button(
                label=t["download_csv"],
                data=csv_data,
                file_name="student-dataset.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col_excel:
            st.download_button(
                label=t["download_excel"],
                data=excel_data,
                file_name="student-dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

# -------------------------------------------------------------
# 4. ACADEMIC CALENDAR & EVENTS
# -------------------------------------------------------------
elif st.session_state.active_tab_id == "events":
    st.title(t["events_title"])
    events_df = load_events()

    today = date.today()
    if "cal_year" not in st.session_state:
        st.session_state.cal_year = today.year
    if "cal_month" not in st.session_state:
        st.session_state.cal_month = today.month

    col_cal, col_form = st.columns([7, 5])

    with col_cal:
        with st.container(border=True):
            m1, m2, m3 = st.columns([1, 4, 1])
            if m1.button("◀ Prev", use_container_width=True):
                if st.session_state.cal_month == 1:
                    st.session_state.cal_month = 12
                    st.session_state.cal_year -= 1
                else:
                    st.session_state.cal_month -= 1
                st.rerun()

            current_month_name = calendar.month_name[st.session_state.cal_month]
            m2.markdown(
                f"<h3 style='text-align: center; margin: 0;'>{current_month_name} {st.session_state.cal_year}</h3>",
                unsafe_allow_html=True,
            )

            if m3.button("Next ▶", use_container_width=True):
                if st.session_state.cal_month == 12:
                    st.session_state.cal_month = 1
                    st.session_state.cal_year += 1
                else:
                    st.session_state.cal_month += 1
                st.rerun()

            event_map = {}
            if not events_df.empty:
                for _, row in events_df.dropna(subset=["Date"]).iterrows():
                    d_key = row["Date"].strftime("%Y-%m-%d")
                    event_map.setdefault(d_key, []).append(str(row["event"]))

            cal_matrix = calendar.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)
            days_header = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

            html_grid = """
            <style>
                .cal-table { width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; margin-top: 10px; }
                .cal-header { text-align: center; font-weight: 600; padding: 8px 2px; color: #64748b; font-size: 0.85rem; }
                .cal-cell { 
                    height: 80px; vertical-align: top; border-radius: 8px; padding: 4px; 
                    background: #f8fafc; border: 1px solid #e2e8f0; font-size: 0.8rem; overflow: hidden;
                }
                .cal-cell.dark { background: #1e293b; border-color: #334155; }
                .cal-cell.empty { background: transparent; border: none; }
                .cal-cell.today { border: 2px solid #3b82f6 !important; font-weight: bold; }
                .cal-num { font-size: 0.85rem; font-weight: bold; margin-bottom: 2px; display: block; }
                .cal-event-badge { 
                    background: #2563eb; color: #ffffff !important; border-radius: 4px; 
                    padding: 2px 5px; margin-top: 2px; font-size: 0.72rem; white-space: nowrap; 
                    overflow: hidden; text-overflow: ellipsis; display: block;
                }
            </style>
            """
            dark_class = "dark" if dark_mode else ""
            html_grid += "<table class='cal-table'><thead><tr>"
            for d in days_header:
                html_grid += f"<th class='cal-header'>{d}</th>"
            html_grid += "</tr></thead><tbody>"

            for week in cal_matrix:
                html_grid += "<tr>"
                for day in week:
                    if day == 0:
                        html_grid += "<td class='cal-cell empty'></td>"
                    else:
                        d_str = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                        is_today = "today" if (d_str == today.strftime("%Y-%m-%d")) else ""
                        day_events = event_map.get(d_str, [])

                        badges_html = "".join([
                            f"<span class='cal-event-badge' title='{ev}'>📌 {ev}</span>"
                            for ev in day_events[:2]
                        ])
                        if len(day_events) > 2:
                            badges_html += f"<span style='font-size:0.65rem; color:#60a5fa;'>+{len(day_events)-2} more</span>"

                        html_grid += f"<td class='cal-cell {dark_class} {is_today}'><span class='cal-num'>{day}</span>{badges_html}</td>"
                html_grid += "</tr>"
            html_grid += "</tbody></table>"

            st.markdown(html_grid, unsafe_allow_html=True)

    with col_form:
        with st.container(border=True):
            st.subheader(t["add_event_title"])
            new_event_name = st.text_input(t["event_name"], placeholder="e.g., Midterm Physics Exam")
            new_event_date = st.date_input(t["event_date"], value=date.today())

            if st.button(t["save_event"], type="primary", use_container_width=True):
                if not new_event_name.strip():
                    st.error("Please enter an event name.")
                else:
                    assigned_id = save_event(new_event_name, new_event_date)
                    st.success(f"Event **{new_event_name.strip()}** (ID: {assigned_id}) added for **{new_event_date}**!")
                    st.session_state.cal_month = new_event_date.month
                    st.session_state.cal_year = new_event_date.year
                    time.sleep(1.2)
                    st.rerun()

        with st.container(border=True):
            st.subheader(t["upcoming_events"])
            if events_df.empty:
                st.info(t["no_events"])
            else:
                display_events = events_df.sort_values(by="Date", ascending=True).reset_index(drop=True)
                st.dataframe(display_events, use_container_width=True, height=260)

# -------------------------------------------------------------
# 5. STUDENT CHATBOT
# -------------------------------------------------------------
elif st.session_state.active_tab_id == "chat":
    st.title(t["chat_title"])
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": t["chat_welcome"], "df": None}
        ]

    st.caption("💡 Quick Prompts:" if st.session_state.lang == "English" else "💡 أسئلة سريعة:")
    c1, c2, c3 = st.columns(3)
    user_prompt = None
    if c1.button("🏆 Class Topper" if st.session_state.lang == "English" else "🏆 الأول على الفصل", use_container_width=True):
        user_prompt = "Who is the topper?" if st.session_state.lang == "English" else "من هو الأول على الفصل؟"
    if c2.button("⚠️ Attendance < 75%" if st.session_state.lang == "English" else "⚠️ نسبة الحضور أقل من 75%", use_container_width=True):
        user_prompt = "Students with attendance below 75" if st.session_state.lang == "English" else "الطلاب بنسبة حضور أقل من 75"
    if c3.button("📉 Lowest in Maths" if st.session_state.lang == "English" else "📉 أقل درجات في الرياضيات", use_container_width=True):
        user_prompt = "Lowest scores in maths" if st.session_state.lang == "English" else "أقل درجات في الرياضيات"

    chat_box_input = st.chat_input(t["chat_placeholder"])
    if chat_box_input:
        user_prompt = chat_box_input

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt, "df": None})
        reply_text, reply_df = query_student_bot(user_prompt, df, lang=st.session_state.lang)
        st.session_state.messages.append({"role": "assistant", "content": reply_text, "df": reply_df})
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("df") is not None and not msg["df"].empty:
                st.dataframe(msg["df"], use_container_width=True)