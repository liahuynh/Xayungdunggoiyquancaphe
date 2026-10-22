import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns

# Import các hàm xử lý và gợi ý từ file model.py của bạn
from model import load_and_process_data, get_recommendations

# Cấu hình giao diện trang web rộng rãi, chuyên nghiệp
st.set_page_config(
    page_title="HUIT Coffee Finder & Recommender",
    page_icon="☕",
    layout="wide"
)

# Load dữ liệu đã qua xử lý và phân cụm K-Means từ model.py
@st.cache_data
def get_data():
    return load_and_process_data("DL_lamsach.csv")

df = get_data()

# --- TIÊU ĐỀ TRANG WEB ---
st.title("☕ Ứng Dụng Gợi Ý Quán Cà Phê Học Bài Cho Sinh Viên HUIT")
st.markdown("Hệ thống hỗ trợ lọc quán thông minh và gợi ý quán phù hợp nhất.")

# --- SIDEBAR: CÁC Ô NHẬP LIỆU BỘ LỌC (Interactive Filters) ---
st.sidebar.header("🔍 Bộ Lọc Tìm Kiếm Quán")

max_dist = st.sidebar.slider("Bán kính tối đa từ HUIT (km):", 0.5, 5.0, 3.0, 0.5)
max_price = st.sidebar.slider("Mức giá trung bình tối đa (VNĐ):", 20000, 100000, 50000, 5000)
min_rating = st.sidebar.slider("Điểm đánh giá tối thiểu (Rating):", 3.0, 5.0, 4.0, 0.1)

has_socket = st.sidebar.checkbox("Bắt buộc có ổ cắm điện 🔌", value=False)
has_wifi = st.sidebar.checkbox("Bắt buộc có Wifi mạnh 📶", value=False)

# Lọc dữ liệu theo các tiêu chí trên sidebar
filtered_df = df[
    (df['Khoang_cach_HUIT_km'] <= max_dist) & 
    (df['Gia_trung_binh'] <= max_price) &
    (df['Diem_danh_gia(Rating)'] >= min_rating)
]

if has_socket:
    filtered_df = filtered_df[filtered_df['Co_o_cam_dien'] == 1]
if has_wifi:
    filtered_df = filtered_df[filtered_df['Co_wifi'] == 1]


# --- TẠO CÁC TAB NỘI DUNG CHÍNH TRÊN WEB ---
tab1, tab2, tab3 = st.tabs(["🗺️ Bản đồ & Danh sách quán", "🤖 Hệ thống gợi ý thông minh", "📊 Phân tích & Biểu đồ dữ liệu"])

# --- TAB 1: BẢN ĐỒ TRỰC QUAN & DANH SÁCH ---
with tab1:
    st.subheader(f"📍 Bản đồ vị trí quán quanh HUIT (Tìm thấy: {len(filtered_df)} quán phù hợp)")
    
    col1, col2 = st.columns([1.3, 1])
    
    with col1:
        # Khởi tạo bản đồ Folium tập trung quanh khu vực HUIT
        map_center = [10.7900, 106.6280] # Tọa độ trung tâm mẫu
        m = folium.Map(location=map_center, zoom_start=14)
        
        # Đánh dấu trường HUIT (màu đỏ)
        folium.Marker(
            [10.7900, 106.6280], 
            popup="<b>Trường Đại học Công Thương TP.HCM (HUIT)</b>",
            icon=folium.Icon(color="red", icon="university", prefix="fa")
        ).add_to(m)

        # Đánh dấu các quán cà phê thỏa mãn bộ lọc (màu xanh dương)
        for _, row in filtered_df.iterrows():
            folium.Marker(
                [row['Vi_do'], row['Kinh_do']],
                popup=f"<b>{row['Ten_quan']}</b><br>Giá: {row['Gia_trung_binh']}đ<br>Rating: {row['Diem_danh_gia(Rating)']}⭐<br>Cách trường: {row['Khoang_cach_HUIT_km']:.2f} km",
                icon=folium.Icon(color="blue", icon="coffee", prefix="fa")
            ).add_to(m)
        
        # Hiển thị bản đồ lên Streamlit
        st_folium(m, width=700, height=500)

    with col2:
        st.markdown("##### Danh sách chi tiết:")
        # Hiển thị bảng dạng DataFrame 
        st.dataframe(
            filtered_df[['Ten_quan', 'Gia_trung_binh', 'Diem_danh_gia(Rating)', 'Khoang_cach_HUIT_km']],
            height=500
        )

# --- TAB 2: HỆ THỐNG GỢI Ý (Content-based Filtering) ---
with tab2:
    st.subheader("🤖 Gợi ý quán cà phê tương tự")
    st.markdown("Chọn một quán bạn đã từng đi hoặc yêu thích, hệ thống sẽ dùng thuật toán **Cosine Similarity** để tìm ra các quán có phong cách và tiêu chí tương tự.")
    
    selected_cafe = st.selectbox("Chọn tên quán:", df['Ten_quan'].values)
    
    if st.button("🚀 Chạy thuật toán gợi ý"):
        rec_result = get_recommendations(df, selected_cafe, top_n=5)
        if rec_result is not None:
            st.success(f"Dựa trên quán **{selected_cafe}**, đây là top 5 quán phù hợp nhất dành cho bạn:")
            st.dataframe(rec_result[['Ten_quan', 'Dia_chi', 'Gia_trung_binh', 'Diem_danh_gia(Rating)', 'Khoang_cach_HUIT_km', 'Cluster']])
        else:
            st.error("Không tìm thấy quán tương tự phù hợp.")

# --- TAB 3: TRỰC QUAN HÓA & PHÂN TÍCH DỮ LIỆU ---
with tab3:
    st.subheader("📊 Biểu đồ phân tích dữ liệu khai thác")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("##### Biểu đồ phân bố mức giá trung bình các quán")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(df['Gia_trung_binh'], kde=True, color='skyblue', ax=ax)
        ax.set_xlabel("Giá trung bình (VNĐ)")
        ax.set_ylabel("Mật độ quán")
        st.pyplot(fig)
        
    with col_b:
        st.markdown("##### Biểu đồ phân bố khoảng cách từ HUIT đến các quán")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.histplot(df['Khoang_cach_HUIT_km'], kde=True, color='salmon', ax=ax2)
        ax2.set_xlabel("Khoảng cách (km)")
        ax2.set_ylabel("Mật độ quán")
        st.pyplot(fig2)