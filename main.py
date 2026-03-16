import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="V36 SYSTEM BEHAVIOR AI", layout="centered")

class UltimateBotV36:

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
            elif s==2:
                gene.append("S")
            elif s==3:
                gene.append("M")
            else:
                if s>10:
                    s=10
                gene.append(f"L{s}")
        return gene

    # ======================
    # SAME FAMILY
    # ======================
    def same_family(self,a,b):
        return a[0]==b[0]

    # ======================
    # E RATIO
    # ======================
    def calculate_E(self,streaks):
        s2=sum(1 for s in streaks if s==2)
        s4=sum(1 for s in streaks if s>=4)

        if s4==0:
            return None,0

        return s2/s4,len(streaks)

    # ======================
    # E VARIATION SERIES (NEW)
    # ======================
    def E_variation_series(self,seq):

        window=500

        if len(seq)<window:
            return None

        sub=seq[-window:]

        streaks=self.get_streaks(sub)

        values=[]

        for i in range(20,len(streaks)):

            part=streaks[:i]

            e,_=self.calculate_E(part)

            if e is not None:
                values.append(e)

        return values

    # ======================
    # GENE ENTROPY
    # ======================
    def gene_entropy(self,gene):

        total=len(gene)
        types=set(gene)

        entropy=0

        for t in types:

            p=gene.count(t)/total

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

            elif self.same_family(a[i],b[i]):
                score+=weight*0.5

            total+=weight

        return score/total

    # ======================
    # HISTORY SEARCH
    # ======================
    def search_history(self,gene,vision):

        if len(gene)<vision+10:
            return []

        current=gene[-vision:]

        sims=[]

        for i in range(len(gene)-vision-1):

            past=gene[i:i+vision]

            sim=self.similarity(current,past)

            sims.append((sim,i))

        sims.sort(reverse=True)

        return sims[:40]

    # ======================
    # FORECAST CORE
    # ======================
    def run_forecast(self,seq,vision):

        streaks=self.get_streaks(seq)

        gene=self.encode_gene(streaks)

        history=self.search_history(gene,vision)

        long_score=0
        short_score=0
        total_similarity=0

        weighted_E=0

        long_cases=0
        short_cases=0

        for sim,h in history:

            pos=0

            for i in range(h+vision):
                pos+=streaks[i]

            future=seq[pos:pos+30]

            if len(future)<20:
                continue

            fs=self.get_streaks(future)

            E_future,_=self.calculate_E(fs)

            if E_future is None:
                continue

            total_similarity+=sim
            weighted_E+=sim*E_future

            if E_future<2:
                long_score+=sim
                long_cases+=1
            else:
                short_score+=sim
                short_cases+=1

        if total_similarity==0:
            return 0.5,0,0,(0,0),0

        E_pred=weighted_E/total_similarity

        total_score=long_score+short_score

        long_rate=long_score/total_score

        matches=long_cases+short_cases

        return long_rate,matches,total_similarity,(long_cases,short_cases),E_pred

    # ======================
    # RELIABILITY
    # ======================
    def reliability(self,avg_sim,matches,entropy):

        sim_factor=min(avg_sim/0.8,1)
        match_factor=min(matches/80,1)
        entropy_factor=max(0,1-(entropy-1.3))

        score=(sim_factor*0.4+match_factor*0.4+entropy_factor*0.2)

        return round(score*100,1)

    # ======================
    # FINAL FORECAST
    # ======================
    def forecast(self,seq):

        streaks=self.get_streaks(seq)

        gene=self.encode_gene(streaks)

        entropy=self.gene_entropy(gene[-60:])
        entropy_move=self.entropy_trend(gene)

        r40,m40,s40,c40,e40=self.run_forecast(seq,40)
        r80,m80,s80,c80,e80=self.run_forecast(seq,80)
        r120,m120,s120,c120,e120=self.run_forecast(seq,120)

        votes=[r40,r80,r120]

        long_rate=sum(votes)/len(votes)
        short_rate=1-long_rate

        matches=m40+m80+m120
        score=s40+s80+s120

        avg_similarity=score/matches if matches>0 else 0

        reliability=self.reliability(avg_similarity,matches,entropy)

        long_cases=c40[0]+c80[0]+c120[0]
        short_cases=c40[1]+c80[1]+c120[1]

        current_streaks=streaks[-120:]

        E_now,E_sample=self.calculate_E(current_streaks)

        E_future=(e40+e80+e120)/3

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

        E_series=self.E_variation_series(seq)

        return {
            "E_now":round(E_now,2) if E_now else 0,
            "E_sample":E_sample,
            "E_future":round(E_future,2),
            "entropy":round(entropy,3),
            "entropy_trend":round(entropy_move,3),
            "long_rate":round(long_rate*100,1),
            "short_rate":round(short_rate*100,1),
            "matches":matches,
            "score":round(score,2),
            "avg_similarity":round(avg_similarity,3),
            "reliability":reliability,
            "long_cases":long_cases,
            "short_cases":short_cases,
            "decision":decision,
            "gene":" ".join(gene[-40:]),
            "E_series":E_series
        }

# ======================
# UI
# ======================

st.title("🧠 V36 SYSTEM BEHAVIOR AI")

raw_input=st.text_area("Nhập dữ liệu 1 2 3 4")

if st.button("Phân tích"):

    data=[int(x) for x in raw_input if x in "1234"]

    if len(data)<300:
        st.warning("Cần ít nhất 300 dữ liệu")
        st.stop()

    bot=UltimateBotV36(data)

    r1=bot.forecast(bot.cl_seq)
    r2=bot.forecast(bot.tn_seq)

    st.subheader("CHẴN / LẺ")

    st.metric("E hiện tại",f'{r1["E_now"]} ({r1["E_sample"]} streak)')
    st.metric("E dự đoán",r1["E_future"])
    st.metric("Entropy",r1["entropy"])
    st.metric("Entropy Trend",r1["entropy_trend"])
    st.metric("Reliability",f'{r1["reliability"]}%')

    if r1["E_series"]:
        df=pd.DataFrame({"E":r1["E_series"]})
        df["E=2"]=2
        st.subheader("Biểu đồ biến thiên E (500 ván)")
        st.line_chart(df)

    st.write("Gene gần:",r1["gene"])
    st.write("Tỷ lệ cầu dài:",r1["long_rate"],"%")
    st.write("Tỷ lệ cầu ngắn:",r1["short_rate"],"%")

    st.write("Long cases:",r1["long_cases"])
    st.write("Short cases:",r1["short_cases"])

    st.write("Gene matches:",r1["matches"])
    st.write("Similarity score:",r1["score"])
    st.write("Average similarity:",r1["avg_similarity"])

    st.success(r1["decision"])

    st.subheader("TO / NHỎ")

    st.metric("E hiện tại",f'{r2["E_now"]} ({r2["E_sample"]} streak)')
    st.metric("E dự đoán",r2["E_future"])
    st.metric("Entropy",r2["entropy"])
    st.metric("Entropy Trend",r2["entropy_trend"])
    st.metric("Reliability",f'{r2["reliability"]}%')

    if r2["E_series"]:
        df=pd.DataFrame({"E":r2["E_series"]})
        df["E=2"]=2
        st.subheader("Biểu đồ biến thiên E (500 ván)")
        st.line_chart(df)

    st.write("Gene gần:",r2["gene"])
    st.write("Tỷ lệ cầu dài:",r2["long_rate"],"%")
    st.write("Tỷ lệ cầu ngắn:",r2["short_rate"],"%")

    st.write("Long cases:",r2["long_cases"])
    st.write("Short cases:",r2["short_cases"])

    st.write("Gene matches:",r2["matches"])
    st.write("Similarity score:",r2["score"])
    st.write("Average similarity:",r2["avg_similarity"])

    st.success(r2["decision"])
