import streamlit as st

# --- CẤU HÌNH GIAO DIỆN MOBILE ---
st.set_page_config(page_title="V28 STRATEGIC VISION", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #121212; color: #ffffff; }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background-color: #0984e3; 
        color: white; 
        font-weight: bold; 
        font-size: 18px;
        border: none;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    .stTextArea>div>div>textarea { background-color: #2d3436; color: white; font-family: 'Consolas', monospace; }
    .metric-container { background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

class UltimateBotV28:
    def __init__(self, data):
        self.raw_data = data
        self.cl_seq = [x % 2 == 0 for x in data]
        self.tn_seq = [x > 2 for x in data]

    def get_filtered_streaks(self, sequence):
        if not sequence: return []
        streaks = []
        count = 1
        for i in range(1, len(sequence)):
            if sequence[i] == sequence[i-1]:
                count += 1
            else:
                if count >= 2: streaks.append(count)
                count = 1
        if count >= 2: streaks.append(count)
        return streaks

    def get_sl_pattern(self, streaks):
        return ['S' if s < 4 else 'L' for s in streaks]

    def find_golden_regimes(self, sequence):
        regimes_structures = []
        streaks = self.get_filtered_streaks(sequence)
        encoded = self.get_sl_pattern(streaks)
        window_scan = 20 
        for i in range(len(encoded) - window_scan):
            sub = encoded[i:i+window_scan]
            if sub.count('L') >= 5: 
                pre_pattern = encoded[max(0, i-30):i]
                if pre_pattern: regimes_structures.append(pre_pattern)
        return regimes_structures

    def get_similarity(self, current, past):
        if not current or not past: return 0
        match = 0
        min_len = min(len(current), len(past))
        for i in range(1, min_len + 1):
            if current[-i] == past[-i]: match += 1
        return (match / 30) * 100 

    def analyze(self, sequence, name):
        filtered_streaks = self.get_filtered_streaks(sequence)
        encoded = self.get_sl_pattern(filtered_streaks)
        
        # Áp suất S (Đo nén)
        s_streaks = [s for s in filtered_streaks if s < 4]
        recent_s = s_streaks[-20:] 
        avg_s = sum(recent_s) / len(recent_s) if recent_s else 0
        
        # So khớp mã gene 30 cụm
        golden_pre = self.find_golden_regimes(sequence)
        max_sim = 0
        current_pre = encoded[-30:] 
        for gp in golden_pre:
            sim = self.get_similarity(current_pre, gp)
            if sim > max_sim: max_sim = sim

        pressure_msg = "Ổn định"
        color = "#ecf0f1"
        if avg_s > 2.7: 
            pressure_msg = "🔥 RẤT CĂNG"
            color = "#e74c3c"
        elif avg_s > 2.45: 
            pressure_msg = "⚠️ Đang nén"
            color = "#f1c40f"

        if max_sim > 65 and avg_s > 2.6:
            horizon = "🔭 TẦM NHÌN 100 VÁN: Cấu trúc vững chắc, khớp mạnh Tiền Bão."
            decision = "🎯 CHIẾN THUẬT: ĐU MẠNH"
        elif len(filtered_streaks) > 0 and filtered_streaks[-1] >= 4:
            horizon = "🌊 ĐANG TRONG BÃO: Cấu trúc bệt đang duy trì."
            decision = "🎯 ĐU MẠNH (Tay 2-4)"
        else:
            horizon = "🧊 Cầu ngắn/nhảy chiếm ưu thế."
            decision = "🛡️ CHỜ / BẺ NHẸ"

        return {
            "name": name,
            "avg_s": avg_s,
            "pressure": pressure_msg,
            "pattern": " -> ".join(encoded[-8:]),
            "sim": max_sim,
            "horizon": horizon,
            "decision": decision,
            "color": color
        }

# --- GIAO DIỆN WEB ---
st.title("🛡️ V28: STRATEGIC VISION")
st.markdown("---")

raw_input = st.text_area("Dán dữ liệu (Cần >500 ván):", height=150, placeholder="Ví dụ: 123412314...")

if st.button("🔍 PHÂN TÍCH CHIẾN LƯỢC"):
    data = [int(s) for s in raw_input if s in "1234"]
    
    if len(data) < 500:
        st.warning("⚠️ Hệ thống cần tối thiểu 500 ván để kích hoạt Tầm nhìn 30 cụm!")
    else:
        bot = UltimateBotV28(data)
        cl_res = bot.analyze(bot.cl_seq, "HỆ CHẴN / LẺ")
        tn_res = bot.analyze(bot.tn_seq, "HỆ TO / NHỎ")
        
        for r in [cl_res, tn_res]:
            with st.container():
                st.markdown(f"### 【 {r['name']} 】")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"<div class='metric-container'><b>Áp suất S:</b><br><span style='font-size:24px; color:{r['color']}'>{r['avg_s']:.2f}</span></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='metric-container'><b>Khớp Tiền Bão:</b><br><span style='font-size:24px; color:#00cec9'>{r['sim']:.1f}%</span></div>", unsafe_allow_html=True)
                
                st.write(f"**Trạng thái:** {r['pressure']}")
                st.write(f"**Gene gần nhất:** `{r['pattern']}`")
                st.info(f"{r['horizon']}")
                st.success(f"➔ {r['decision']}")
                st.markdown("---")


st.caption("Phiên bản V28 tối ưu cho thiết bị di động. Chúc ông giáo rực rỡ!")
