import sys
import os
import json
import time
import requests
import tempfile
import subprocess
from io import BytesIO
from PIL import Image as PILImage
import streamlit as st
from openai import OpenAI

# Ép hệ thống nhận diện thư mục gốc để tránh lỗi ModuleNotFoundError
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_factory.config.settings import settings

# --- API & UTILS ---
def get_secret(secret_field):
    return secret_field.get_secret_value() if secret_field else ""

def call_groq(messages, model="llama-3.3-70b-versatile", max_tokens=1024):
    api_key = get_secret(settings.groq_api_key)
    if not api_key:
        return "⚠️ Cần cấu hình GROQ_API_KEY trong file .env để sử dụng AI này."
    try:
        client = OpenAI(api_key=api_key, base_url=settings.groq_base_url)
        resp = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens)
        return resp.choices.message.content
    except Exception as e:
        return f"Lỗi API: {e}"

def download_image(url):
    try:
        return PILImage.open(BytesIO(requests.get(url, timeout=10).content))
    except:
        return PILImage.new('RGB', (1080, 1920), color=(50, 50, 50))

# --- MOCK & AUTO VIDEO FUNCTIONS ---
def generate_script(topic):
    api_key = get_secret(settings.groq_api_key)
    if not api_key:
        # Fallback Mock Data nếu chưa có API Key
        return {
            "hook": f"Bí mật về {topic} mà bạn chưa biết!",
            "scenes": [
                {"text": f"Mọi người thường nghĩ {topic} rất khó.", "visual": "Người suy nghĩ", "duration": 3},
                {"text": "Nhưng AI có thể giải quyết trong 1 nốt nhạc.", "visual": "Robot AI mỉm cười", "duration": 3}
            ],
            "caption": f"Khám phá {topic} cùng AI #AI"
        }
    system_prompt = f"""Tạo kịch bản TikTok (30s) chủ đề: {topic}. Trả về JSON: {{"hook": "...", "scenes": [{{"text": "...", "visual": "mô tả ảnh tĩnh", "duration": 3}}], "caption": "..."}}"""
    try:
        res = call_groq([{"role": "system", "content": system_prompt}], max_tokens=500).strip()
        if res.startswith("```json"): res = res.split("```json")[1].split("```")
        return json.loads(res.strip())
    except Exception:
        return {"hook": "Lỗi tạo kịch bản", "scenes": [{"text": topic, "visual": topic, "duration": 5}], "caption": topic}

# --- CẤU HÌNH GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="AI Factory", page_icon="🎬", layout="wide")
st.markdown("""
<style>
[data-testid="stHeader"], footer {visibility: hidden;}
.stApp {margin: 0; padding: 0;}
* {font-family: 'Inter', 'Segoe UI', sans-serif;}
.hero {padding: 3rem; background: linear-gradient(135deg, #0B0E17, #1A1F35); border-radius: 15px; text-align: center; color: white;}
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_msgs" not in st.session_state: st.session_state.chat_msgs = [{"role": "system", "content": "Bạn là AI."}]
if "workflows" not in st.session_state: st.session_state.workflows = []
if "auto_script" not in st.session_state: st.session_state.auto_script = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🎬 AI Factory</h2>", unsafe_allow_html=True)
    pages = {"🏠 Trang chủ": "Home", "🧩 Dịch vụ AI": "Features", "🎬 Auto Video": "AutoVideo", "📋 Workflow": "Workflow", "🤖 Telegram": "Telegram"}
    sel = st.radio("Điều hướng", list(pages.keys()), index=0)
    st.session_state.page = pages[sel]

# --- RENDER PAGES ---
if st.session_state.page == "Home":
    st.markdown("<div class='hero'><h1>🚀 AI Content Factory</h1><p>Clone. Create. Scale.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Video Tự Động", "⚡ 1 phút", "Render nhanh")
    c2.metric("Mô hình AI", "🤖 12+", "Miễn phí")
    c3.metric("Chi phí", "💰 0$", "Mã nguồn mở")

elif st.session_state.page == "Features":
    st.markdown("### 🧩 Trung Tâm AI")
    t1, t2, t3 = st.tabs(["💬 Chat", "🎨 Tạo Ảnh", "🔗 Phân Tích Web"])
    with t1:
        for m in st.session_state.chat_msgs:
            if m["role"] != "system":
                with st.chat_message(m["role"]): st.markdown(m["content"])
        if p := st.chat_input("Hỏi AI..."):
            st.session_state.chat_msgs.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            with st.chat_message("assistant"):
                ans = call_groq(st.session_state.chat_msgs)
                st.markdown(ans)
                st.session_state.chat_msgs.append({"role": "assistant", "content": ans})
    with t2:
        img_p = st.text_input("Mô tả ảnh:", "A futuristic cyberpunk city")
        if st.button("Tạo Ảnh (Pollinations)"):
            with st.spinner("Đang vẽ..."):
                img = download_image(f"https://image.pollinations.ai/prompt/{requests.utils.quote(img_p)}")
                st.image(img, use_container_width=True)
    with t3:
        st.info("Tính năng trích xuất nội dung web. Dán URL vào để AI tóm tắt.")

elif st.session_state.page == "AutoVideo":
    st.markdown("### 🎬 Auto Video Generator")
    topic = st.text_input("Chủ đề video:", "Lịch sử trí tuệ nhân tạo")
    if st.button("🚀 1. Tạo Kịch Bản"):
        st.session_state.auto_script = generate_script(topic)
    
    if st.session_state.auto_script:
        st.json(st.session_state.auto_script)
        if st.button("🎬 2. Tạo Ảnh (Demo Render)"):
            with st.spinner("Đang sinh ảnh từ kịch bản..."):
                for s in st.session_state.auto_script["scenes"]:
                    img = download_image(f"https://image.pollinations.ai/prompt/{requests.utils.quote(s['visual'])}")
                    st.image(img, caption=s['text'], width=300)
            st.success("Tạo hình ảnh và video thành công (Mock Pipeline)!")

elif st.session_state.page == "Workflow":
    st.markdown("### 📋 Quản lý Chiến Dịch")
    seed = st.text_input("Tên chiến dịch:")
    if st.button("Lưu Workflow"):
        st.session_state.workflows.append({"name": seed, "status": "Pending"})
        st.success("Đã lưu!")
    for w in st.session_state.workflows:
        st.write(f"- **{w['name']}**: {w['status']}")

elif st.session_state.page == "Telegram":
    st.markdown("### 🤖 Cấu hình Telegram Bot")
    st.text_input("Bot Token", settings.telegram_bot_token or "", disabled=True)
    st.text_input("Chat ID", settings.telegram_chat_id or "", disabled=True)
    st.info("Cập nhật các biến này trong file .env để kích hoạt điều khiển từ xa qua Telegram.")