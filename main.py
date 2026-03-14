import streamlit as st
import math

st.set_page_config(page_title="V34 SYSTEM BEHAVIOR AI", layout="centered")

class UltimateBotV34:

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
    # E RATIO
    # ======================

    def calculate_E(self,streaks):

        s2=sum(1 for s in streaks if s==2)
        s4=sum(1 for s in streaks if s>=4)

        if s4==0:
            return None

        return s2/s4


    # ======================
    # GENE ENTROPY
    # ======================

    def gene_entropy(self,gene):

        total=len(gene)

        px=gene.count("X")/total
        ps=gene.count("S")/total
        pl=gene.count("L")/total

        entropy=0

        for p in [px,ps,pl]:
            if p>0:
                entropy-=p*math.log2(p)

        return entropy


    # ======================
    # ENTROPY TIMELINE
    # ======================

    def entropy_trend(self,gene):

        windows=[30,40,50,60]

        values=[]

        for w in windows:

            if len(gene)>w:

                segment=gene[-w:]

                values.append(self.gene_entropy(segment))

        if len(values)<2:
            return 0

        trend=values[0]-values[-1]

        return trend


    # ======================
    # SIMILARITY
    # ======================

    def similarity(self,a,b):

        score=0
        total=0

        for i in range(len(a)):

            weight=(i+1)**1.5

            if a[i]==b[i]:
                score+=weight

            total+=weight

        return score/total


    # ======================
    # HISTORY SEARCH
    # ======================

    def search_history(self,gene,vision):

        current=gene[-vision:]

        sims=[]

        for i in range(len(gene)-vision-1):

            past=gene[i:i+vision]

            sim=self.similarity(current,past)

            sims.append((sim,i))

        sims.sort(reverse=True)

        filtered=[x for x in sims if x[0]>0.55]

        top=filtered[:50]

        return [x[1] for x in top]


    # ======================
    # FORECAST CORE
    # ======================

    def run_forecast(self,seq,vision):

        streaks=self.get_streaks(seq)

        gene=self.encode_gene(streaks)

        history=self.search_history(gene,vision)

        long_count=0
        short_count=0

        for h in history:

            start=sum(streaks[:h+vision])

            future=seq[start:start+100]

            if len(future)<50:
                continue

            fs=self.get_streaks(future)

            E_future=self.calculate_E(fs)

            if E_future is None:
                continue

            if E_future<2:
                long_count+=1
            else:
                short_count+=1

        total=long_count+short_count

        if total==0:
            return 0.5

        return long_count/total


    # ======================
    # CYCLE DETECTOR
    # ======================

    def cycle_hint(self,seq):

        streaks=self.get_streaks(seq)

        indexes=[]

        for i in range(len(streaks)):

            if streaks[i]>=6:
                indexes.append(i)

        if len(indexes)<3:
            return 0

        gaps=[indexes[i+1]-indexes[i] for i in range(len(indexes)-1)]

        avg_gap=sum(gaps)/len(gaps)

        return avg_gap


    # ======================
    # FINAL FORECAST
    # ======================

    def forecast(self,seq):

        streaks=self.get_streaks(seq)

        gene=self.encode_gene(streaks)

        entropy=self.gene_entropy(gene[-60:])

        entropy_move=self.entropy_trend(gene)

        r40=self.run_forecast(seq,40)
        r80=self.run_forecast(seq,80)
        r120=self.run_forecast(seq,120)

        votes=[r40,r80,r120]

        long_rate=sum(votes)/len(votes)
        short_rate=1-long_rate

        current_streaks=streaks[-120:]

        E_now=self.calculate_E(current_streaks)

        cycle=self.cycle_hint(seq)

        if entropy<1.2 and entropy_move>0.05 and long_rate>0.6:
            decision="🔥 SIÊU CẦU DÀI"
        elif long_rate>0.65:
            decision="🎯 CẦU DÀI"
        elif short_rate>0.65:
            decision="🎯 CẦU NGẮN"
        elif entropy>1.45:
            decision="🌪 NHIỄU"
        else:
            decision="🛡️ KHÔNG RÕ"

        return {

            "E_now": round(E_now,2) if E_now else 0,
            "entropy": round(entropy,3),
            "entropy_trend": round(entropy_move,3),
            "cycle_gap": round(cycle,1),
            "long_rate": round(long_rate*100,1),
            "short_rate": round(short_rate*100,1),
            "decision": decision,
            "gene":" ".join(gene[-40:])
        }


# ======================
# UI
# ======================

st.title("🧠 V34 SYSTEM BEHAVIOR AI")

raw_input=st.text_area("Nhập dữ liệu 1 2 3 4")

if st.button("Phân tích"):

    data=[int(x) for x in raw_input if x in "1234"]

    if len(data)<300:
        st.warning("Cần ít nhất 300 dữ liệu")
        st.stop()

    bot=UltimateBotV34(data)

    r1=bot.forecast(bot.cl_seq)
    r2=bot.forecast(bot.tn_seq)

    st.subheader("CHẴN / LẺ")

    st.metric("E hiện tại",r1["E_now"])
    st.metric("Entropy",r1["entropy"])
    st.metric("Entropy Trend",r1["entropy_trend"])

    st.write("Gene gần:",r1["gene"])

    st.write("Tỷ lệ cầu dài:",r1["long_rate"],"%")
    st.write("Tỷ lệ cầu ngắn:",r1["short_rate"],"%")

    st.success(r1["decision"])


    st.subheader("TO / NHỎ")

    st.metric("E hiện tại",r2["E_now"])
    st.metric("Entropy",r2["entropy"])
    st.metric("Entropy Trend",r2["entropy_trend"])

    st.write("Gene gần:",r2["gene"])

    st.write("Tỷ lệ cầu dài:",r2["long_rate"],"%")
    st.write("Tỷ lệ cầu ngắn:",r2["short_rate"],"%")

    st.success(r2["decision"])
