import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# === SETUP ===
load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

st.set_page_config(
    page_title="Study Squad Bot 🤓",
    page_icon="📚",
    layout="centered",
)

DATA_FILE = "progress.json"

# === UTILITY ===
def load_progress():
    if not os.path.exists(DATA_FILE):
        return {"sessions": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_progress(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_session(topic, score):
    data = load_progress()
    data["sessions"].append({
        "topic": topic,
        "score": score,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_progress(data)

# === HEADER ===
st.title("🤓 Study Squad Bot")
st.caption("Temen belajar santai, nyentil dikit tapi bikin pinter 💪")

# === STATE ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hai bro! Mau belajar apa hari ini? 😎"}
    ]
if "mode" not in st.session_state:
    st.session_state.mode = "chat"
if "score" not in st.session_state:
    st.session_state.score = 0

# === MOOD SELECTOR ===
mood = st.selectbox(
    "Mood belajar lo hari ini:",
    ["🔥 Semangat", "😩 Capek", "😎 Santai"],
    index=2
)

# === QUIZ BUTTON ===
col1, col2 = st.columns(2)
with col1:
    if st.button("🎓 Coba Quiz Mini"):
        st.session_state.mode = "quiz"
        st.session_state.messages.append(
            {"role": "user", "content": "Kasih gua soal latihan dong"}
        )
        st.rerun()

with col2:
    if st.button("💬 Mode Chat Biasa"):
        st.session_state.mode = "chat"
        st.session_state.messages.append(
            {"role": "assistant", "content": "Oke bro, kita balik ngobrol biasa aja 😁"}
        )
        st.rerun()

# === DISPLAY CHAT HISTORY ===
for msg in st.session_state.messages:
    role_label = "Lo" if msg["role"] == "user" else "Bot"
    st.chat_message(msg["role"]).markdown(f"**{role_label}:** {msg['content']}")

# === HANDLE CHAT INPUT ===
user_input = st.chat_input("Tulis pertanyaan lo...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(f"**Lo:** {user_input}")

    # System prompt dinamis berdasarkan mood
    system_prompt = f"""
    Kamu adalah Study Squad Bot — tutor belajar chill, jujur, tapi supportive.
    Mood user hari ini: {mood}.
    Kalau user lagi '😩 Capek', jawab lebih lembut & kasih motivasi ringan.
    Kalau '🔥 Semangat', kasih tantangan lebih seru.
    Kalau '😎 Santai', gunakan gaya ngobrol ringan dan humor.
    
    Kalau user di mode 'quiz', buat 1 pertanyaan (pilihan ganda atau short answer),
    evaluasi jawabannya, kasih skor + penjelasan.
    Kalau user di mode 'chat', bantu jelasin materi belajar dengan santai dan ga ngebosenin.
    """

    mode = st.session_state.mode

    # === PANGGIL API ===
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages
        ],
        temperature=0.9,
    )

    reply = response.choices[0].message.content.strip()

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(f"**Bot:** {reply}")

    # === SKOR HANDLING SEDERHANA ===
    if "benar" in reply.lower() or "mantap" in reply.lower():
        st.session_state.score += 1

# === SHOW SCORE & PROGRESS ===
st.divider()
st.subheader("📊 Progress Belajar Lo")
st.write(f"Total Skor: **{st.session_state.score}**")

progress_data = load_progress()
if progress_data["sessions"]:
    st.write("Riwayat sesi:")
    for s in progress_data["sessions"]:
        st.write(f"- {s['timestamp']}: {s['topic']} (Skor: {s['score']})")
else:
    st.caption("Belum ada progress tersimpan.")

# === SAVE SESSION BUTTON ===
topic = st.text_input("Masukin nama topik sesi ini biar disimpan:")
if st.button("💾 Simpan Progress"):
    if topic.strip():
        add_session(topic, st.session_state.score)
        st.success("Progress berhasil disimpan ✅")
    else:
        st.warning("Isi dulu topiknya, bro 😅")
