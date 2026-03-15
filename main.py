import streamlit as st
import math

st.set_page_config(page_title="SYSTEM BEHAVIOR AI V35", layout="centered")

class UltimateBotV35:

    def __init__(self,data):

        self.data=data

        self.cl_seq=[x%2==0 for x in data]
        self.tn_seq=[x>2 for x in data]


    # ======================
    # STREAK
    # ======================

    def get_streaks(self,seq):

        streaks=[]
        positions=[]

        count=1
        pos=0

        for i in range(1,len(seq)):

            if seq[i]==seq[i-1]:
                count+=1
            else:
                streaks.append(count)
                positions.append(pos)
                pos+=count
                count=1

        streaks.append(count)
        positions.append(pos)

        return streaks,positions


    # ======================
    # GENE ENCODE (4 LEVEL)
    # ======================

    def encode_gene(self,streaks):

        gene=[]

        for s in streaks:

            if s==1:
                gene.append("X")
            elif s<=3:
                gene.append("S")
            elif s<=6:
                gene.append("M")
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

        counts=[gene.count(x)/total for x in ["X","S","M","L"]]

        entropy=0

        for p in counts:
            if p>0:
                entropy-=p*math.log2(p)

        return entropy


    # ======================
    # ENTROPY TREND
    # ======================

    def entropy_trend(self,gene):

        windows=[30,40,50,60]

        values=[]

        for w in windows:

            if len(gene)>w:
                values.append(self.gene_entropy(gene[-w:]))

        if len(values)<2:
            return 0

        return values[0]-values[-1]


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

        filtered=[x for x in sims if x[0]>0.6]

        top=filtered[:50]

        return [x[1] for x in top]


    # ======================
    # FORECAST CORE
    # ======================

    def run_forecast(self,seq,vision):

        streaks,positions=self.get_streaks(seq)

        gene=self.encode_gene(streaks)

        history=self.search_history(gene,vision)

        long_count=0
        short_count=0

        for h in history:

            if h+vision>=len(positions):
                continue

            start=positions[h+vision]

            future=seq[start:start+100]

            if len(future)<50:
                continue

            fs,_=self.get_streaks(future)

            E_future=self.calculate_E(fs)

            if E_future is None:
                continue

            if E_future<2:
                long_count+=1
            else:
                short_count+=1

        total=long_count+short_count

        if total==0:
            return 0.5,0,0,0

        return long_count/total,long_count,short_count,total


    # ======================
    # FINAL FORECAST
    # ======================

    def forecast(self,seq):

        streaks,positions=self.get_streaks(seq)

        gene=self.encode_gene(streaks)

        entropy=self.gene_entropy(gene[-60:])

        entropy_move=self.entropy_trend(gene)

        r40,l40,s40,t40=self.run_forecast(seq,40)
        r80,l80,s80,t80=self.run_forecast(seq,80)
        r120,l120,s120,t120=self.run_forecast(seq,120)

        long_rate=(r40+r80+r120)/3
        short_rate=1-long_rate

        total_match=t40+t80+t120
        long_match=l40+l80+l120
        short_match=s40+s80+s120

        current_streaks=streaks[-120:]

        E_now=self.calculate_E(current_streaks)

        approx_rounds=sum(current_streaks)

        confidence=0
        if total_match>0:
            confidence=min(100,(long_match+short_match)/150*100)

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
            "E_rounds":approx_rounds,
            "entropy": round(entropy,3),
            "entropy_trend": round(entropy_move,3),

            "long_rate": round(long_rate*100,1),
            "short_rate": round(short_rate*100,1),

            "long_match":long_match,
            "short_match":short_match,
            "total_match":total_match,

            "confidence":round(confidence,1),

            "decision": decision,

            "gene":" ".join(gene[-40:])
        }


# ======================
# UI
# ======================

st.title("🧠 SYSTEM BEHAVIOR AI V35")

raw_input=st.text_area("Nhập dữ liệu 1 2 3 4")

if st.button("Phân tích"):

    data=[int(x) for x in raw_input if x in "1234"]

    if len(data)<300:
        st.warning("Cần ít nhất 300 dữ liệu")
        st.stop()

    bot=UltimateBotV35(data)

    r1=bot.forecast(bot.cl_seq)
    r2=bot.forecast(bot.tn_seq)


    st.subheader("CHẴN / LẺ")

    st.metric("E hiện tại",f'{r1["E_now"]}  ({r1["E_rounds"]} ván)')

    st.metric("Entropy",r1["entropy"])
    st.metric("Entropy Trend",r1["entropy_trend"])

    st.write("Gene gần:",r1["gene"])

    st.write(f'Tỷ lệ cầu dài: {r1["long_rate"]}%')
    st.write(f'Tỷ lệ cầu ngắn: {r1["short_rate"]}%')

    st.write(f'Pattern match: {r1["total_match"]} ván')
    st.write(f'Long: {r1["long_match"]}  |  Short: {r1["short_match"]}')

    st.write(f'Confidence: {r1["confidence"]}%')

    st.success(r1["decision"])


    st.subheader("TO / NHỎ")

    st.metric("E hiện tại",f'{r2["E_now"]} ({r2["E_rounds"]} ván)')

    st.metric("Entropy",r2["entropy"])
    st.metric("Entropy Trend",r2["entropy_trend"])

    st.write("Gene gần:",r2["gene"])

    st.write(f'Tỷ lệ cầu dài: {r2["long_rate"]}%')
    st.write(f'Tỷ lệ cầu ngắn: {r2["short_rate"]}%')

    st.write(f'Pattern match: {r2["total_match"]} ván')
    st.write(f'Long: {r2["long_match"]}  |  Short: {r2["short_match"]}')

    st.write(f'Confidence: {r2["confidence"]}%')

    st.success(r2["decision"])
