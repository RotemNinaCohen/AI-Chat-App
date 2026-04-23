import requests

BASE_URL = "https://server.iac.ac.il/api/v1/studentapi"

# ==========================================
# חלק 1: טעינת המפתח
# ==========================================
try:
    with open("token.txt", "r") as f:
        api_key = f.read().strip()
    print("המפתח נטען בהצלחה מקובץ הגיבוי.")
except FileNotFoundError:
    print("שגיאה: לא מצאתי את קובץ ה-token.txt.")
    exit()

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# ==========================================
# חלק 2: בחירת מצב הפעולה
# ==========================================
print("\nברוכה הבאה למערכת ה-AI!")
print("0 - צ'אט רגיל (Stateless)")
print("1 - סוכן חכם (Agentic)")

mode = input("הקלידי 0 או 1 ולחצי Enter: ")

if mode == "0":
    api_endpoint = f"{BASE_URL}/chat/completions"
    print("--- נבחר מצב צ'אט רגיל ---")
elif mode == "1":
    api_endpoint = f"{BASE_URL}/responses"
    print("--- נבחר מצב סוכן חכם ---")
else:
    print("בחירה לא חוקית.")
    exit()

# ==========================================
# חלק 3: לולאת הצ'אט
# ==========================================
while True:
    user_message = input("\nאת: ")
    if user_message.lower() == "exit":
        break

    print("המודל חושב...")

    if mode == "0":
        payload = {
            "messages": [{"role": "user", "content": user_message}],
            "max_completion_tokens": 1000
        }
    else:
        # המבנה שעבד לנו מצוין לפי התמונה מהמצגת
        payload = {
            "reasoning": {"effort": "low"},
            "instructions": "ענה בעברית בצורה מקצועית ותמציתית.",
            "input": user_message,
            "tools": [{"type": "web_search"}]
        }

    try:
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=45)

        if response.status_code == 200:
            data = response.json()
            ai_reply = ""

            if mode == "0":
                ai_reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                # חילוץ הטקסט הנקי מתוך רשימת הצעדים במצב 1
                if isinstance(data, list):
                    for item in data:
                        # מחפשים איבר שהוא 'message'
                        if item.get("type") == "message":
                            contents = item.get("content", [])
                            for content in contents:
                                # השרת שלך משתמש ב-output_text
                                ai_reply += content.get("output_text", "") or content.get("text", "")
                elif isinstance(data, dict):
                    ai_reply = data.get("answer") or data.get("output") or str(data)

            if ai_reply:
                print(f"AI Agent: {ai_reply}")
            else:
                # גיבוי למקרה חירום - אם לא הצלחנו לחלץ, נדפיס את הכל כדי שלא תהיה תשובה ריקה
                print(f"AI (Raw): {data}")
        else:
            print(f"שגיאת שרת {response.status_code}: {response.text}")

    except Exception as e:
        print(f"שגיאה בתקשורת: {e}")