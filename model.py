import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

def load_and_process_data(file_path="dkktdl_sach.csv"):
    df = pd.read_csv(file_path)
    features = ['Gia_trung_binh', 'Diem_danh_gia(Rating)', 'Do_yen_tinh', 'Khoang_cach_HUIT_km']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])
    
    # Chạy K-Means
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    return df

def get_recommendations(df, target_quan, top_n=5):
    rec_features = ['Gia_trung_binh', 'Diem_danh_gia(Rating)', 'So_luong_review', 
                    'Co_wifi', 'Co_o_cam_dien', 'Do_yen_tinh', 'Phu_hop_hoc_nhom', 'Khoang_cach_HUIT_km']
    scaler = StandardScaler()
    X_rec_scaled = scaler.fit_transform(df[rec_features])
    
    cosine_sim = cosine_similarity(X_rec_scaled, X_rec_scaled)
    
    if target_quan not in df['Ten_quan'].values:
        return None
    
    idx = df[df['Ten_quan'] == target_quan].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]
    
    quan_indices = [i[0] for i in sim_scores]
    return df.iloc[quan_indices]