import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# הגדרת עיצוב בסיסי לאפליקציה
st.set_page_config(page_title="GS1 Security", page_icon="⏰", layout="centered")

# --- קוד ליישור המערכת לימין (עברית) ---
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
    }
    div[data-testid="stTextInput"] label {
        text-align: right;
        display: block;
    }
    input {
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

# --- הוספת הלוגו לתפריט הצד ---
st.sidebar.image("logo.jpg", use_container_width=True)

# פונקציה לחיבור מאובטח ל-Google Sheets
def get_sheet():
# ... (מכאן והלאה השאר את שאר הקוד שלך בדיוק כפי שהוא)
sheet = get_sheet()

# תפריט ניווט צדדי
menu = ["תצוגת עובד", "תצוגת מנהל"]
choice = st.sidebar.selectbox("ניווט במערכת", menu)

if choice == "תצוגת עובד":
    st.title("⏰ מערכת החתמת שעות - עובד")
    st.write("---")
    
    name = st.text_input("שם ושם משפחה")
    emp_id = st.text_input("מספר עובד")
    today = datetime.now().strftime("%d/%m/%Y")
    
    st.info(f"📅 תאריך דיווח: {today}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("החתם כניסה 🟢", use_container_width=True):
            if not name or not emp_id:
                st.error("חובה למלא שם ומספר עובד!")
            elif sheet:
                now_time = datetime.now().strftime("%H:%M")
                # עמודות: תאריך, שם, מספר עובד, כניסה, יציאה, סה"כ
                sheet.append_row([today, name, emp_id, now_time, "", ""])
                st.success(f"נרשמה כניסה בשעה {now_time}!")

    with col2:
        if st.button("החתם יציאה 🔴", use_container_width=True):
            if not name or not emp_id:
                st.error("חובה למלא שם ומספר עובד!")
            elif sheet:
                now_time = datetime.now().strftime("%H:%M")
                records = sheet.get_all_records()
                
                # חיפוש דיווח כניסה פתוח מהיום עבור העובד הזה
                found_row_idx = -1
                for idx, row in enumerate(records):
                    if str(row.get('מספר עובד')) == str(emp_id) and row.get('תאריך') == today and not row.get('שעת יציאה'):
                        found_row_idx = idx + 2  # +2 כי gspread מבוסס 1 והשורה הראשונה היא כותרת
                        break
                
                if found_row_idx != -1:
                    # עדכון שעת יציאה בגיליון
                    sheet.update_cell(found_row_idx, 5, now_time)
                    
                    # חישוב שעות אוטומטי
                    in_time_str = records[found_row_idx - 2]['שעת כניסה']
                    try:
                        fmt = "%H:%M"
                        tdelta = datetime.strptime(now_time, fmt) - datetime.strptime(in_time_str, fmt)
                        total_hours = round(tdelta.total_seconds() / 3600, 2)
                        sheet.update_cell(found_row_idx, 6, total_hours)
                        st.success(f"נרשמה יציאה בשעה {now_time}. סה\"כ שעות: {total_hours}")
                    except:
                        st.success(f"נרשמה יציאה בשעה {now_time}.")
                else:
                    # אם לא נמצאה כניסה תואמת, פשוט רושמים שורת יציאה
                    sheet.append_row([today, name, emp_id, "", now_time, ""])
                    st.warning(f"נרשמה יציאה בשעה {now_time} (לא נמצאה כניסה תואמת להיום).")

elif choice == "תצוגת מנהל":
    st.title("🔒 פאנל ניהול ומעקב")
    st.write("---")
    
    password = st.text_input("הכנס סיסמת מנהל", type="password")
    
    if password == "0945":
        st.success("הגישה אושרה!")
        if sheet:
            data = sheet.get_all_records()
            if data:
                df = pd.DataFrame(data)
                st.subheader("נתוני נוכחות עובדים")
                st.dataframe(df, use_container_width=True)
                
                # כפתור הורדה ישירה לאקסל (CSV)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 הורד דוח באקסל (CSV)",
                    data=csv,
                    file_name=f"attendance_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("אין עדיין נתונים בגיליון.")
    elif password != "":
        st.error("סיסמה שגויה! הגישה חסומה.")
