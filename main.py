import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="V36 SYSTEM BEHAVIOR AI", layout="centered")

class UltimateBotV36:

    def __init__(self,data):
        self.data=data
        self.cl_seq=[x%2==0 for x in data]
        self.tn_seq=[x>2 for x in data]
        self.pred_history=[]

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

    def encode_gene(self,streaks):
        gene=[]
        for s in streaks:
            if s==1: gene.append("X")
            elif s==2: gene.append("S")
            elif s==3: gene.append("M")
            else:
                if s>10: s=10
                gene.append(f"L{s}")
        return gene

    def same_family(self,a,b):
        return a[0]==b[0]

    def calculate_E(self,streaks):
        s2=sum(1 for s in streaks if s==2)
        s4=sum(1 for s in streaks if s>=4)
        if s4==0: return None,0
        return s2/s4,len(streaks)

    def dynamic_threshold(self,history_E):
        if len(history_E)==0: return 2
        return sum(history_E)/len(history_E)

    def E_variation_series(self,seq,window=500):
        if len(seq)<window: return None
        sub=seq[-window:]
        streaks=self.get_streaks(sub)
        values=[]
        for i in range(20,len(streaks)):
            part=streaks[:i]
            e,_=self.calculate_E(part)
            if e is not None:
                values.append(e)
        return values

    # 🔥 NEW: E TREND (SHAPE)
    def E_to_direction(self,E):
        dirs=[]
        for i in range(1,len(E)):
            if E[i]>E[i-1]:
                dirs.append(1)
            else:
                dirs.append(-1)
        return dirs

    def direction_similarity(self,a,b):
        same=0
        for i in range(len(a)):
            if a[i]==b[i]:
                same+=1
        return same/len(a)

    def E_trend_analysis(self,seq):

        E_series=self.E_variation_series(seq,500)
        if not E_series or len(E_series)<150:
            return 0,0,0,0,0

        recent=E_series[-100:]
        recent_dir=self.E_to_direction(recent)

        matches=[]

        for i in range(len(E_series)-150):
            past=E_series[i:i+100]
            past_dir=self.E_to_direction(past)

            sim=self.direction_similarity(recent_dir,past_dir)

            if sim>0.6:
                future=E_series[i+100:i+150]

                if len(future)<30:
                    continue

                future_avg=sum(future)/len(future)

                matches.append((sim,future_avg))

        if not matches:
            return 0,0,0,0,0

        long_score=0
        short_score=0

        for sim,e in matches:
            if e<2:
                long_score+=sim
            else:
                short_score+=sim

        total=long_score+short_score
        long_rate=long_score/total if total>0 else 0.5
        short_rate=1-long_rate

        return long_rate*100, short_rate*100, len(matches), long_score, short_score

    def gene_entropy(self,gene):
        total=len(gene)
        types=set(gene)
        entropy=0
        for t in types:
            p=gene.count(t)/total
            if p>0:
                entropy-=p*math.log2(p)
        return entropy

    def entropy_trend(self,gene):
        windows=[30,40,50,60]
        values=[]
        for w in windows:
            if len(gene)>w:
                segment=gene[-w:]
                values.append(self.gene_entropy(segment))
        if len(values)<2:
            return 0
        return values[0]-values[-1]

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
        history_E=[]

        for sim,h in history:

            if sim < 0.55:
                continue

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

            history_E.append(E_future)

            total_similarity+=sim
            weighted_E+=sim*E_future

            threshold=self.dynamic_threshold(history_E)

            if E_future < threshold:
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

    def reliability(self,avg_sim,matches,entropy):
        sim_factor=min(avg_sim/0.8,1)
        match_factor=min(matches/120,1)
        entropy_factor=max(0,1-(entropy-1.3))
        score=(sim_factor*0.4+match_factor*0.4+entropy_factor*0.2)
        return round(score*100,1)

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

        decision = "LONG" if long_rate>0.5 else "SHORT"

        E_series=self.E_variation_series(seq,500)
        E_series_250=self.E_variation_series(seq,250)

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
            "E_series":E_series,
            "E_series_250":E_series_250
        }

# UI
st.title("🧠 V36 SYSTEM BEHAVIOR AI")

raw_input=st.text_area("Nhập dữ liệu 1 2 3 4")

if st.button("Phân tích"):

    data=[int(x) for x in raw_input if x in "1234"]

    st.write("Tổng dữ liệu:",len(data))

    if len(data)<300:
        st.warning("Cần ít nhất 300 dữ liệu")
        st.stop()

    bot=UltimateBotV36(data)

    r1=bot.forecast(bot.cl_seq)
    r2=bot.forecast(bot.tn_seq)

    st.subheader("CHẴN / LẺ")

    st.metric("E hiện tại",f'{r1["E_now"]}')
    st.metric("E dự đoán",r1["E_future"])

    if r1["E_series"]:
        df=pd.DataFrame({"E":r1["E_series"]})
        df["E=2"]=2
        st.subheader("E 500 ván")
        st.line_chart(df)

    if r1["E_series_250"]:
        df2=pd.DataFrame({"E":r1["E_series_250"]})
        df2["E=2"]=2
        st.subheader("E 250 ván")
        st.line_chart(df2)

    lr,sr,match,ls,ss=bot.E_trend_analysis(bot.cl_seq)

    st.subheader("E TREND (RIÊNG)")
    st.write("Long:",round(lr,1),"%")
    st.write("Short:",round(sr,1),"%")
    st.write("Matches:",match)

    st.success(r1["decision"])
