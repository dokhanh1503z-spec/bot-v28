import streamlit as st

st.set_page_config(page_title="V31 GENE AI", layout="centered")

class UltimateBotV31:

    def __init__(self,data):

        self.data=data

        self.cl_seq=[x%2==0 for x in data]
        self.tn_seq=[x>2 for x in data]


    # ======================
    # STREAK
    # ======================

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


    # ======================
    # GENE ENCODE
    # ======================

    def encode_gene(self,streaks):

        gene=[]

        for s in streaks:

            if s==1:
                gene.append("X")
            elif s<=3:
                gene.append("S")
            else:
                gene.append("L")

        return gene


    # ======================
    # TÍNH E
    # ======================

    def calculate_E(self,streaks):

        s2=sum(1 for s in streaks if s==2)
        s4=sum(1 for s in streaks if s>=4)

        if s4==0:
            return 999

        return s2/s4


    # ======================
    # SIMILARITY
    # ======================

    def similarity(self,a,b):

        match=0

        for i in range(len(a)):

            if a[-i-1]==b[-i-1]:
                match+=1

        return match/len(a)


    # ======================
    # TÌM QUÁ KHỨ
    # ======================

    def search_history(self,gene):

        vision=80

        current=gene[-vision:]

        matches=[]

        for i in range(len(gene)-vision-100):

            past=gene[i:i+vision]

            sim=self.similarity(current,past)

            if sim>0.75:

                matches.append(i)

        return matches


    # ======================
    # DỰ BÁO 100 VÁN
    # ======================

    def forecast(self,seq):

        streaks=self.get_streaks(seq)

        gene=self.encode_gene(streaks)

        vision=80

        current_streaks=streaks[-vision:]

        E_now=self.calculate_E(current_streaks)

        history=self.search_history(gene)

        long_count=0
        short_count=0

        for h in history:

            future=seq[h:h+100]

            fs=self.get_streaks(future)

            E_future=self.calculate_E(fs)

            if E_future<2:
                long_count+=1
            else:
                short_count+=1


        total=max(1,long_count+short_count)

        long_rate=long_count/total
        short_rate=short_count/total


        if long_rate>0.6:
            decision="🎯 ĐU CẦU"
        elif short_rate>0.6:
            decision="🎯 BẺ CẦU"
        else:
            decision="🛡️ CHỜ"


        return {

            "E_now":round(E_now,2),
            "matches":len(history),
            "long_rate":round(long_rate*100,1),
            "short_rate":round(short_rate*100,1),
            "decision":decision,
            "gene":" ".join(gene[-20:])
        }


# ======================
# UI
# ======================

st.title("🧠 V31 GENE FORECAST AI")

raw_input=st.text_area("Dữ liệu 1 2 3 4")

if st.button("Phân tích"):

    data=[int(x) for x in raw_input if x in "1234"]

    bot=UltimateBotV31(data)

    r1=bot.forecast(bot.cl_seq)
    r2=bot.forecast(bot.tn_seq)

    st.subheader("CHẴN / LẺ")

    st.metric("E hiện tại",r1["E_now"])
    st.metric("Match quá khứ",r1["matches"])

    st.write("Gene gần:",r1["gene"])

    st.write("Tỷ lệ cầu dài:",r1["long_rate"],"%")
    st.write("Tỷ lệ cầu ngắn:",r1["short_rate"],"%")

    st.success(r1["decision"])


    st.subheader("TO / NHỎ")

    st.metric("E hiện tại",r2["E_now"])
    st.metric("Match quá khứ",r2["matches"])

    st.write("Gene gần:",r2["gene"])

    st.write("Tỷ lệ cầu dài:",r2["long_rate"],"%")
    st.write("Tỷ lệ cầu ngắn:",r2["short_rate"],"%")

    st.success(r2["decision"])
