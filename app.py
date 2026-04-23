import streamlit as st
import requests

# 1. הגדרות דף - חייב להיות השורה הראשונה בקוד
st.set_page_config(page_title="IAC AI Assistant", page_icon="🤖", layout="wide")


# 2. הזרקת CSS מודרני שמתאים ל-Dark ו-Light Mode
@st.cache_data
def load_modern_css():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700&display=swap');

    /* הגדרות גופן וכיווניות */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Heebo', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* כותרת גרדיאנט מודרנית */
    .main-title {
        font-weight: 800;
        background: linear-gradient(90deg, #4A90E2, #9013FE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        text-align: center;
        margin-top: -40px;
        padding-bottom: 20px;
    }

    /* בועות צ'אט עם צל עדין */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }

    /* כרטיס סטטוס שקוף למחצה - עובד מעולה ב-Dark Mode */
    .status-card {
        padding: 15px;
        border-radius: 12px;
        background-color: rgba(128, 128, 128, 0.1);
        border-right: 5px solid #4A90E2;
        margin: 10px 0;
    }

    /* אנימציית פעימה לחלונית ה"מעבד..." */
    @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
    .thinking-container { 
        display: flex; 
        align-items: center; 
        color: #9013FE; 
        animation: pulse 1.5s infinite; 
        font-weight: bold;
        padding: 10px;
    }
    </style>
    """


st.markdown(load_modern_css(), unsafe_allow_html=True)

# 3. ניהול זיכרון ו-API Key
if 'api_key' not in st.session_state:
    try:
        with open("token.txt", "r") as f:
            st.session_state.api_key = f.read().strip()
    except:
        st.session_state.api_key = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. סרגל צידי (Sidebar)
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # לוגו המכללה (או אייקון גנרי)
    st.image("https://iac.ac.il/landingnew/wp-content/uploads/2025/03/Untitled-design.png",
             width=60)
    st.title("ניהול שיחה")

    # החלפת מצב עבודה
    is_agent = st.toggle("🚀 מצב סוכן חכם (Agentic)", value=False)

    # תצוגת סטטוס ויזואלית
    status_color = "#9013FE" if is_agent else "#4A90E2"
    status_name = "סוכן חכם" if is_agent else "צ'אט רגיל"

    st.markdown(f"""
        <div class="status-card" style="border-right-color: {status_color};">
            <span style="font-size: 0.8rem; opacity: 0.8;">סטטוס מערכת:</span><br>
            <strong style="color: {status_color};">{status_name} פעיל</strong>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # כפתור איפוס
    if st.button("🗑️ איפוס שיחה", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 5. ממשק ראשי
st.markdown('<h1 class="main-title">IAC Smart AI</h1>', unsafe_allow_html=True)

# הצגת היסטוריית ההודעות
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# תיבת קלט מהמשתמש
if user_input := st.chat_input("איך אפשר לעזור היום?"):
    # שמירה והצגה של הודעת המשתמש
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # יצירת תגובת ה-AI
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(
            '<div class="thinking-container"><span>●</span>&nbsp;הסוכן מעבד את הבקשה שלך...</div>',
            unsafe_allow_html=True
        )

        try:
            BASE_URL = "https://server.iac.ac.il/api/v1/studentapi"
            headers = {
                "Authorization": f"Bearer {st.session_state.api_key}",
                "Content-Type": "application/json"
            }

            if not is_agent:
                # מצב 0: צ'אט רגיל
                url = f"{BASE_URL}/chat/completions"
                payload = {"messages": [{"role": "user", "content": user_input}]}
            else:
                # מצב 1: סוכן חכם
                url = f"{BASE_URL}/responses"
                payload = {
                    "input": user_input,
                    "tools": [{"type": "web_search"}],
                    "reasoning": {"effort": "low"}
                }

            response = requests.post(url, headers=headers, json=payload, timeout=45)
            data = response.json()

            # חילוץ התשובה לפי סוג ה-API
            ai_reply = ""
            if not is_agent:
                ai_reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                if isinstance(data, list):
                    for item in data:
                        if item.get("type") == "message":
                            content_list = item.get("content", [])
                            if content_list:
                                ai_reply += content_list[0].get("output_text", "") or content_list[0].get("text", "")

            # הסרת האנימציה והצגת הטקסט הסופי
            thinking_placeholder.empty()
            if ai_reply:
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            else:
                st.error("השרת החזיר תשובה ריקה. ודאי שה-API תקין.")

        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"שגיאה בתקשורת: {e}")