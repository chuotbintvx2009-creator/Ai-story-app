import google.generativeai as genai
import streamlit as st

st.set_page_config(page_title="AI Storyteller Ultra", layout="wide")
st.title("🧙‍♂️ Trợ Lý Kể Chuyện Bộ Nhớ Trượt 700.000 Từ")

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

# 3. Khởi tạo danh sách lưu trữ tất cả các phần truyện cũ
# Khác với bản cũ, bản này lưu truyện theo từng đoạn để dễ đếm từ và xóa đoạn cũ xa nhất
if "story_segments" not in st.session_state:
    st.session_state.story_segments = ["TÓM TẮT DIỄN BIẾN TRUYỆN ĐÃ QUA:\n- Câu chuyện bắt đầu."]

if "messages" not in st.session_state: 
    st.session_state.messages = []

# --- KHU VỰC CÁC NÚT ĐIỀU KHIỂN & BỘ ĐẾM CHỮ ---
st.sidebar.header("🛠️ Quản lý cuộc trò chuyện")

# Nút Xóa lịch sử đoạn chat trên màn hình hiển thị chính
if st.sidebar.button("🗑️ Xóa màn hình chat hiện tại"):
    st.session_state.messages = []
    st.toast("Đã xóa sạch màn hình chat! Cốt truyện ngầm vẫn giữ nguyên.", icon="🧹")
    st.rerun()

# Thuật toán đếm tổng số từ đang lưu trong bộ nhớ cốt truyện
def count_words(text_list):
    full_text = " ".join(text_list)
    return len(full_text.split())

total_words = count_words(st.session_state.story_segments)

# Hiển thị thanh đo dung lượng bộ nhớ truyện trên Sidebar
st.sidebar.subheader("📊 Dung lượng bộ nhớ truyện:")
st.sidebar.progress(min(total_words / 700000, 1.0))
st.sidebar.write(f"Đang nhớ: **{total_words:,} / 700.000 từ**")

# Hiển thị vùng xem bộ nhớ hiện tại
st.sidebar.subheader("🧠 Kho ký ức hiện tại của AI:")
all_current_lore = "\n\n".join(st.session_state.story_segments)
st.sidebar.info(all_current_lore[:2000] + ("..." if len(all_current_lore) > 2000 else ""))

# Nút Xóa hẳn toàn bộ cốt truyện về số 0
if st.sidebar.button("⚠️ Xóa Sạch Toàn Bộ Cốt Truyện"):
    st.session_state.story_segments = ["TÓM TẮT DIỄN BIẾN TRUYỆN ĐÃ QUA:\n- Câu chuyện bắt đầu."]
    st.session_state.messages = []
    st.toast("Đã xóa sạch bộ nhớ về số 0!", icon="🧠")
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

        # Gộp tất cả các phân đoạn ký ức chưa bị xóa làm ngữ cảnh gửi đi
        history_context = "\n\n".join(st.session_state.story_segments)

        # Đóng gói dữ liệu siêu ngữ cảnh gửi cho Gemini
        full_prompt = f"""
        HƯỚNG DẪN HỆ THỐNG (SYSTEM INSTRUCTION):
        {system_instruction}
        
        TOÀN BỘ KÝ ỨC CỐT TRUYỆN QUÁ KHỨ (BẮT BUỘC PHẢI NHỚ):
        {history_context}
        
        TÌNH TIẾT MỚI: {user_input}
        Hãy viết tiếp câu chuyện một cách mượt mà, logic và hấp dẫn.
        """

        with st.chat_message("assistant"):
            with st.spinner("AI đang viết tiếp truyện..."):
                model = genai.GenerativeModel('gemini-2.5-pro') 
                response = model.generate_content(full_prompt)
                ai_response = response.text
                st.markdown(ai_response)
                
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        # 5. THUẬT TOÁN ĐỆM TRƯỢT: Thêm phần mới, nếu vượt 700k từ thì xóa phần xa nhất
        new_segment = f"[Diễn biến]: {user_input} -> {ai_response}"
        st.session_state.story_segments.append(new_segment)
        
        # Vòng lặp kiểm tra: Cứ vượt quá 700.000 từ là tự động xóa phần tử đầu tiên (xa nhất)
        while count_words(st.session_state.story_segments) > 700000:
            if len(st.session_state.story_segments) > 1:
                st.session_state.story_segments.pop(1) # Giữ lại dòng tiêu đề [0], xóa phần cũ nhất ở vị trí [1]
            else:
                break
                
        st.rerun()
