import google.generativeai as genai
import streamlit as st

st.set_page_config(page_title="AI Storyteller Ultra Pro", layout="wide")
st.title("🧙‍♂️ Trợ Lý Kể Chuyện Ký Ức Vĩnh Cửu (Uncensored)")

# 1. Quản lý API Key
if "api_key" not in st.session_state: 
    st.session_state.api_key = ""
api_input = st.sidebar.text_input("1. Nhập Gemini API Key:", type="password", value=st.session_state.api_key)

if api_input:
    st.session_state.api_key = api_input
    genai.configure(api_key=api_input)

# 2. Ô System Instructions giống AI Studio - Cơ chế CHO PHÉP tự do sáng tác
st.sidebar.header("⚙️ Cấu hình hệ thống")
system_instruction = st.sidebar.text_area(
    "2. System Instructions (Ghim phong cách, bối cảnh):",
    value="Bạn là một nhà văn giả tưởng đại tài. Hãy kể chuyện cuốn hút và phát triển tình tiết tự nhiên theo nội dung người dùng nhập vào. Bạn ĐƯỢC PHÉP miêu tả chân thực, khốc liệt các trận chiến (bao gồm cả các chi tiết máu me, thương tích) hoặc các cảnh lãng mạn thân mật người lớn NẾU diễn biến và cốt truyện của người dùng yêu cầu, nhưng không cần phải tự ý nhồi nhét nếu tình huống đang diễn ra bình thường. Luôn tuân thủ tuyệt đối logic của các phần trước.",
    height=200
)

# 3. Khởi tạo danh sách lưu trữ cốt truyện (Cơ chế đệm trượt)
if "story_segments" not in st.session_state:
    st.session_state.story_segments = ["TÓM TẤT DIỄN BIẾN TRUYỆN ĐÃ QUA:\n- Câu chuyện bắt đầu."]

if "messages" not in st.session_state: 
    st.session_state.messages = []

# --- KHU VỰC CÁC NÚT ĐIỀU KHIỂN & BỘ ĐẾM CHỮ ---
st.sidebar.header("🛠️ Quản lý cuộc trò chuyện")

# Nút Xóa lịch sử đoạn chat trên màn hình chính
if st.sidebar.button("🗑️ Xóa màn hình chat hiện tại"):
    st.session_state.messages = []
    st.toast("Đã xóa sạch màn hình chat! Cốt truyện ngầm vẫn giữ nguyên.", icon="🧹")
    st.rerun()

# Thuật toán đếm tổng số từ đang lưu trong bộ nhớ
def count_words(text_list):
    full_text = " ".join(text_list)
    return len(full_text.split())

total_words = count_words(st.session_state.story_segments)

# Hiển thị thanh đo dung lượng bộ nhớ truyện trên Sidebar
st.sidebar.subheader("📊 Dung lượng bộ nhớ truyện:")
st.sidebar.progress(min(total_words / 700000, 1.0))
st.sidebar.write(f"Đang nhớ: **{total_words:,} / 700.000 từ**")

# Hiển thị vùng xem bộ nhớ hiện tại (Giới hạn hiển thị 2000 ký tự chống lag giao diện)
st.sidebar.subheader("🧠 Kho ký ức hiện tại của AI:")
all_current_lore = "\n\n".join(st.session_state.story_segments)
st.sidebar.info(all_current_lore[:2000] + ("..." if len(all_current_lore) > 2000 else ""))

# Nút Xóa hẳn toàn bộ cốt truyện về số 0
if st.sidebar.button("⚠️ Xóa Sạch Toàn Bộ Cốt Truyện"):
    st.session_state.story_segments = ["TÓM TẤT DIỄN BIẾN TRUYỆN ĐÃ QUA:\n- Câu chuyện bắt đầu."]
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
                
                # CẤU HÌNH HẠ BỘ LỌC AN TOÀN TOÀN DIỆN CHO TRUYỆN 
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
                
                try:
                    response = model.generate_content(
                        full_prompt,
                        safety_settings=safety_settings
                    )
                    ai_response = response.text
                except Exception as e:
                    # Nếu Google chặn phản hồi, AI sẽ im lặng bỏ qua lỗi hoặc hiển thị trống thay vì ngắt dòng thông báo cũ
                    ai_response = ""

                if ai_response:
                    st.markdown(ai_response)
                else:
                    st.warning("Lượt chat này không tạo được nội dung, hãy thử diễn đạt lại bằng từ ngữ ẩn dụ hơn một chút nhé.")
                
        if ai_response:
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

            # 5. THUẬT TOÁN ĐỆM TRƯỢT: Thêm phần mới, nếu vượt 700k từ thì xóa phần xa nhất
            new_segment = f"[Tình tiết]: {user_input} -> {ai_response}"
            st.session_state.story_segments.append(new_segment)
            
            # Vòng lặp kiểm tra: Cứ vượt quá 700.000 từ là tự động xóa phần tử đầu tiên (xa nhất)
            while count_words(st.session_state.story_segments) > 700000:
                if len(st.session_state.story_segments) > 1:
                    st.session_state.story_segments.pop(1) # Xóa phần cũ nhất ở vị trí 1
                else:
                    break
                
        st.rerun()
