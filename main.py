import streamlit as st

st.set_page_config(page_title="V30 STRUCTURE AI", layout="centered")

st.markdown("""
<style>
.main { background-color: #121212; color: white; }
.stButton>button {
    width:100%;
    height:3.5em;
    border-radius:10px;
    font-size:18px;
    background:#0984e3;
    color:white;
}
</style>
""", unsafe_allow_html=True)


class UltimateBotV30:

    def __init__(self,data):

        self.data=data

        self.cl_seq=[x%2==0 for x in data]
        self.tn_seq=[x>2 for x in data]


    # =========================
    # TÍNH STREAK
    # =========================

    def get_streaks(self,seq):

        streaks=[]
        count=1

        for i in range(1,len(seq)):

            if seq[i]==seq[i-1]:
                count+=1
            else:
                streaks.append(count)
                count=1

        streaks.append(count)

        return streaks


    # =========================
    # ENCODE GENE
    # =========================

    def encode_gene(self,streaks):

        gene=[]

        for s in streaks:

            if s==1:
                gene.append("X")
            elif s<4:
                gene.append("S")
            else:
                gene.append("L")

        return gene


    # =========================
    # TÍNH E
    # =========================

    def calculate_E(self,streaks):

        s2=sum(1 for s in streaks if s==2)
        s4=sum(1 for s in streaks if s>=4)

        if s4==0:
            return 999

        return s2/s4


    # =========================
    # PHÂN BỐ STREAK
    # =========================

    def streak_distribution(self,streaks):

        s2=sum(1 for s in streaks if s==2)
        s3=sum(1 for s in streaks if s==3)
        s4=sum(1 for s in streaks if s>=4)

        return s2,s3,s4


    # =========================
    # PHASE DETECTOR
    # =========================

    def detect_phase(self,E):

        if E>2:
            return "⚡ CẦU NGẮN (BẺ)"
        elif E<2:
            return "🌊 CẦU DÀI (ĐU)"
        else:
            return "🧊 TRUNG TÍNH"


    # =========================
    # TÌM CẤU TRÚC QUÁ KHỨ
    # =========================

    def find_structures(self,gene):

        window=80
        structures=[]

        for i in range(len(gene)-window):

            structures.append(gene[i:i+window])

        return structures


    # =========================
    # SO KHỚP GENE
    # =========================

    def similarity(self,current,past):

        match=0
        min_len=min(len(current),len(past))

        for i in range(min_len):

            if current[-i-1]==past[-i-1]:
                match+=1

        return (match/min_len)*100


    # =========================
    # PHÂN TÍCH HỆ
    # =========================

    def analyze(self,seq,name):

        streaks=self.get_streaks(seq)

        gene=self.encode_gene(streaks)

        E=self.calculate_E(streaks)

        s2,s3,s4=self.streak_distribution(streaks)

        phase=self.detect_phase(E)

        vision=80
        current=gene[-vision:]

        structures=self.find_structures(gene)

        max_sim=0

        for p in structures:

            sim=self.similarity(current,p)

            if sim>max_sim:
                max_sim=sim


        if E>2:
            decision="🎯 BẺ CẦU"
        elif E<2:
            decision="🎯 ĐU CẦU"
        else:
            decision="🛡️ CHỜ"


        return {

            "name":name,
            "E":round(E,2),
            "phase":phase,
            "decision":decision,
            "sim":round(max_sim,1),
            "gene":" ".join(gene[-12:]),
            "s2":s2,
            "s3":s3,
            "s4":s4
        }



# =========================
# GIAO DIỆN
# =========================

st.title("🧠 V30 STRUCTURE AI")

st.markdown("---")

raw_input=st.text_area(
"Dán dữ liệu (1 2 3 4)",
height=150,
placeholder="123412341234..."
)

if st.button("🔍 PHÂN TÍCH"):

    data=[int(x) for x in raw_input if x in "1234"]

    if len(data)<60:
        st.warning("⚠️ Cần ít nhất 60 ván")

    else:

        bot=UltimateBotV30(data)

        results=[

            bot.analyze(bot.cl_seq,"HỆ CHẴN / LẺ"),
            bot.analyze(bot.tn_seq,"HỆ TO / NHỎ")

        ]

        for r in results:

            st.subheader(r["name"])

            col1,col2,col3=st.columns(3)

            col1.metric("E",r["E"])
            col2.metric("Khớp gene",str(r["sim"])+"%")
            col3.metric("Streak4+",r["s4"])

            st.write("Gene gần:",r["gene"])

            st.info(r["phase"])

            st.success(r["decision"])

            st.markdown("---")
