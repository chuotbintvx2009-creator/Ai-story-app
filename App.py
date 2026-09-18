import google.generativeai as genai
import streamlit as st

st.set_page_config(page_title="AI Storyteller", layout="wide")
st.title("🧙‍♂️ Trợ Lý Kể Chuyện Ký Ức Vĩnh Cửu")

# 1. Quản lý API Key
if "api_key" not in st.session_state: 
    st.session_state.api_key = ""
api_input = st.sidebar.text_input("1. Nhập Gemini API Key:", type="password", value=st.session_state.api_key)

if api_input:
    st.session_state.api_key = api_input
    genai.configure(api_key=api_input)

# 2. Ô System Instructions giống AI Studio
st.sidebar.header("⚙️ Cấu hình hệ thống")
system_instruction = st.sidebar.text_area(
    "2. System Instructions (Ghim phong cách, bối cảnh):",
    value="Bạn là một nhà văn giả tưởng đại tài. Hãy kể chuyện cuốn hút. Luôn tuân thủ logic các phần trước.",
    height=150
)

# 3. Khởi tạo bộ nhớ (Cơ chế chống quên)
if "story_lore" not in st.session_state:
    st.session_state.story_lore = "TÓM TẮT DIỄN BIẾN TRUYỆN ĐÃ QUA:\n- Câu chuyện bắt đầu."

if "messages" not in st.session_state: 
    st.session_state.messages = []

# --- KHU VỰC CÁC NÚT ĐIỀU KHIỂN & QUẢN LÝ BỘ NHỚ ---
st.sidebar.header("🛠️ Quản lý cuộc trò chuyện")

# Nút Xóa lịch sử đoạn chat trên màn hình chính
if st.sidebar.button("🗑️ Xóa đoạn chat hiện tại"):
    st.session_state.messages = []
    st.toast("Đã xóa sạch màn hình chat! Bạn có thể bắt đầu lại.", icon="🧹")
    st.rerun()

# Hiển thị và cho phép sửa đổi Ký ức cốt lõi
st.sidebar.subheader("🧠 Ký ức cốt lõi của AI:")
edited_lore = st.sidebar.text_area("Bạn có thể sửa lại ký ức ngầm của AI tại đây nếu nó tóm tắt sai:", value=st.session_state.story_lore, height=150)
st.session_state.story_lore = edited_lore

# Nút Xóa hẳn ký ức cốt lõi về số 0
if st.sidebar.button("⚠️ Xóa toàn bộ ký ức cốt lõi"):
    st.session_state.story_lore = "TÓM TẮT DIỄN BIẾN TRUYỆN ĐÃ QUA:\n- Câu chuyện bắt đầu."
    st.toast("Đã xóa sạch bộ nhớ cốt truyện!", icon="🧠")
    st.rerun()

# 4. Giao diện vùng Chat chính
for message in st.session_state.messages:
    with st.chat_message(message["role"]): 
        st.markdown(message["content"])

if user_input := st.chat_input("Nhập diễn biến tiếp theo của câu chuyện..."):
    if not st.session_state.api_key:
        st.error("Vui lòng nhập API Key ở thanh bên trái!")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): 
            st.markdown(user_input)

        # Đóng gói dữ liệu siêu ngữ cảnh gửi cho Gemini
        full_prompt = f"""
        HƯỚNG DẪN HỆ THỐNG (SYSTEM INSTRUCTION):
        {system_instruction}
        
        TOÀN BỘ KÝ ỨC CỐT TRUYỆN QUÁ KHỨ (KHÔNG ĐƯỢC PHÉP QUÊN):
        {st.session_state.story_lore}
        
        TÌNH TIẾT MỚI: {user_input}
        Hãy viết tiếp câu chuyện một cách mượt mà, logic và hấp dẫn.
        """

        with st.chat_message("assistant"):
            with st.spinner("AI đang viết tiếp truyện..."):
                # Sử dụng gemini-2.5-pro để có tư duy logic truyện dài tập tốt nhất
                model = genai.GenerativeModel('gemini-2.5-pro') 
                response = model.generate_content(full_prompt)
                ai_response = response.text
                st.markdown(ai_response)
                
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        # CƠ CHẾ TỰ ĐỘNG KHẮC SÂU KÝ ỨC NGẦM (Chạy sau mỗi câu chat)
        summary_prompt = f"""
        Bạn là bộ nhớ ngầm của hệ thống. Hãy cập nhật lại bản tóm tắt cốt truyện bằng cách tích hợp diễn biến mới vào ký ức cũ. 
        Giữ lại toàn bộ các cột mốc, chi tiết, nhân vật quan trọng để câu chuyện dài cũng không bị quên chi tiết cũ.
        
        [Ký ức cũ]: {st.session_state.story_lore}
        [Diễn biến mới]: Người dùng nhập '{user_input}' và AI đã viết '{ai_response}'
        
        Hãy xuất ra bản tóm tắt mới đã cập nhật đầy đủ thông tin:
        """
        update_response = model.generate_content(summary_prompt)
        st.session_state.story_lore = update_response.text
        st.rerun()
  
