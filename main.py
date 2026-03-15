import streamlit as st
import math

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
                gene.append("L")

        return gene


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
    # GENE ENTROPY
    # ======================

    def gene_entropy(self,gene):

        total=len(gene)

        counts=[
            gene.count("X")/total,
            gene.count("S")/total,
            gene.count("M")/total,
            gene.count("L")/total
        ]

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

        if len(gene)<vision+10:
            return []

        current=gene[-vision:]

        sims=[]

        for i in range(len(gene)-vision-1):

            past=gene[i:i+vision]

            sim=self.similarity(current,past)

            sims.append((sim,i))

        sims.sort(reverse=True)

        # match rộng hơn để tăng sample
        filtered=[x for x in sims if x[0]>0.48]

        top=filtered[:50]

        return top


    # ======================
    # FORECAST CORE
    # ======================

    def run_forecast(self,seq,vision):

        streaks=self.get_streaks(seq)

        gene=self.encode_gene(streaks)

        history=self.search_history(gene,vision)

        long_score=0
        short_score=0

        long_cases=0
        short_cases=0

        total_similarity=0

        for sim,h in history:

            pos=0
            for i in range(h+vision):
                pos+=streaks[i]

            future=seq[pos:pos+100]

            if len(future)<50:
                continue

            fs=self.get_streaks(future)

            E_future,_=self.calculate_E(fs)

            if E_future is None:
                continue

            total_similarity+=sim

            if E_future<2:

                long_score+=sim
                long_cases+=1

            else:

                short_score+=sim
                short_cases+=1


        total_score=long_score+short_score

        # FIX CRASH
        if total_score==0:
            return 0.5,0,0,(0,0)

        long_rate=long_score/total_score

        matches=long_cases+short_cases

        return long_rate,matches,total_similarity,(long_cases,short_cases)


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

        r40,m40,s40,c40=self.run_forecast(seq,40)
        r80,m80,s80,c80=self.run_forecast(seq,80)
        r120,m120,s120,c120=self.run_forecast(seq,120)

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

            "E_now":round(E_now,2) if E_now else 0,
            "E_sample":E_sample,
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

            "gene":" ".join(gene[-40:])
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
    st.metric("Entropy",r1["entropy"])
    st.metric("Entropy Trend",r1["entropy_trend"])
    st.metric("Reliability",f'{r1["reliability"]}%')

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
    st.metric("Entropy",r2["entropy"])
    st.metric("Entropy Trend",r2["entropy_trend"])
    st.metric("Reliability",f'{r2["reliability"]}%')

    st.write("Gene gần:",r2["gene"])

    st.write("Tỷ lệ cầu dài:",r2["long_rate"],"%")
    st.write("Tỷ lệ cầu ngắn:",r2["short_rate"],"%")

    st.write("Long cases:",r2["long_cases"])
    st.write("Short cases:",r2["short_cases"])

    st.write("Gene matches:",r2["matches"])

    st.write("Similarity score:",r2["score"])
    st.write("Average similarity:",r2["avg_similarity"])

    st.success(r2["decision"])
