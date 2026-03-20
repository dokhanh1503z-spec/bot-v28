import streamlit as st
import math
import pandas as pd
import requests
import re
import plotly.graph_objects as go

st.set_page_config(page_title="V36 SYSTEM BEHAVIOR AI", layout="centered")

def fetch_sheets_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5-pPONvbU7PR7FteVtEBvN6EuudQ2rgbV3sHX-Ngy1PALF4nvyTBidXOXXE325_TLKKDJwZB7xFgH/pub?output=csv"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return "".join(re.findall(r'[1-4]', response.text))
    except:
        return ""
    return ""

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

    def same_family(self,a,b):
        return a[0]==b[0]

    def calculate_E(self,streaks):
        s2=sum(1 for s in streaks if s==2)
        s4=sum(1 for s in streaks if s>=4)
        if s4==0:
            return None,0
        return s2/s4,len(streaks)

    def dynamic_threshold(self,history_E):
        if len(history_E)==0:
            return 2
        return sum(history_E)/len(history_E)

    def global_E_avg(self,seq):
        streaks=self.get_streaks(seq)
        values=[]
        for i in range(30,len(streaks)):
            part=streaks[:i]
            e,_=self.calculate_E(part)
            if e is not None:
                values.append(e)
        if len(values)==0:
            return 2
        return sum(values)/len(values)

    def E_variation_series(self,seq):
        if len(seq) < 30:
            return None
        streaks=self.get_streaks(seq)
        values=[]
        for i in range(20,len(streaks)):
            part=streaks[:i]
            e,_=self.calculate_E(part)
            if e is not None:
                values.append(e)
        return values

    # ✅ NEW: gene → E
    def gene_to_E_series(self, gene_seq):
        streaks=[]
        for g in gene_seq:
            if g=="X":
                streaks.append(1)
            elif g=="S":
                streaks.append(2)
            elif g=="M":
                streaks.append(3)
            elif g.startswith("L"):
                try:
                    streaks.append(int(g[1:]))
                except:
                    continue

        values=[]
        for i in range(20,len(streaks)):
            part=streaks[:i]
            e,_=self.calculate_E(part)
            if e is not None:
                values.append(e)
        return values

    # ✅ NEW: gene → số lượng data
    def gene_to_number_count(self, gene_seq):
        total=0
        for g in gene_seq:
            if g=="X":
                total+=1
            elif g=="S":
                total+=2
            elif g=="M":
                total+=3
            elif g.startswith("L"):
                try:
                    total+=int(g[1:])
                except:
                    continue
        return total

    def E_to_direction(self,E):
        dirs=[]
        for i in range(1,len(E)):
            if E[i] > E[i-1]:
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
        E_series=self.E_variation_series(seq)
        if not E_series or len(E_series)<150:
            return 0,0,0,0

        recent=E_series[-100:]
        recent_dir=self.E_to_direction(recent)

        long_cases=0
        short_cases=0
        matches=0

        streaks = self.get_streaks(seq)

        for i in range(len(E_series)-150):

            past=E_series[i:i+100]
            past_dir=self.E_to_direction(past)

            sim=self.direction_similarity(recent_dir,past_dir)

            if sim > 0.6:

                pos = sum(streaks[:i+100])
                future_seq = seq[pos:pos+50]

                if len(future_seq) < 30:
                    continue

                future_streaks = self.get_streaks(future_seq)
                E_future,_ = self.calculate_E(future_streaks)

                if E_future is None:
                    continue

                matches+=1

                if E_future < 2:
                    long_cases+=1
                else:
                    short_cases+=1

        if matches==0:
            return 0,0,0,0

        long_rate = long_cases/matches*100
        short_rate = short_cases/matches*100

        return round(long_rate,1),round(short_rate,1),long_cases,short_cases

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

        history = history[:20]

        global_avg = self.global_E_avg(seq)

        long_score=0
        short_score=0
        total_similarity=0
        weighted_E=0
        long_cases=0
        short_cases=0
        history_E=[]

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

            history_E.append(E_future)

            local_th=self.dynamic_threshold(history_E)

            total_similarity+=sim
            weighted_E+=sim*E_future

            if E_future < local_th and E_future < global_avg:
                long_score+=sim*1.2
                long_cases+=1
            elif E_future > local_th and E_future > global_avg:
                short_score+=sim*1.2
                short_cases+=1
            else:
                if E_future < 2:
                    long_score+=sim*0.5
                    long_cases+=1
                else:
                    short_score+=sim*0.5
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

        decision_flag = 1 if long_rate > 0.5 else 0
        self.pred_history.append(decision_flag)

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

st.title("🧠 V36 SYSTEM BEHAVIOR AI")

if st.button("☁️ Tải dữ liệu từ Google Sheets"):
    data_from_sheets = fetch_sheets_data()
    if data_from_sheets:
        st.session_state['data_input'] = data_from_sheets
        st.success("Đã tải xong!")

input_val = st.session_state.get('data_input', "")
raw_input=st.text_area("Nhập dữ liệu 1 2 3 4", value=input_val)

if st.button("Phân tích"):
    st.session_state.data = [int(x) for x in raw_input if x in "1234"]

if "data" in st.session_state:
    data = st.session_state.data

    st.write(f"📥 Tổng data: {len(data)}")

    if len(data)<300:
        st.warning("Cần ít nhất 300 dữ liệu")
        st.stop()

    bot=UltimateBotV36(data)

    r1=bot.forecast(bot.cl_seq)
    r2=bot.forecast(bot.tn_seq)

    st.subheader("CHẴN / LẺ")

    view_gene = st.text_input("Nhập số gene (CL)", value="50")
    view_gene_2 = st.text_input("Nhập gene khung 2 (CL)", value="100")

    try:
        view_gene = int(view_gene)
        view_gene_2 = int(view_gene_2)
    except:
        view_gene = 50
        view_gene_2 = 100

    streaks = bot.get_streaks(bot.cl_seq)
    gene = bot.encode_gene(streaks)

    sub_gene = gene[-view_gene:]
    sub_gene2 = gene[-view_gene_2:]

    E_series_new = bot.gene_to_E_series(sub_gene)
    E_series_2 = bot.gene_to_E_series(sub_gene2)

    st.write(f"🧬 {len(sub_gene)} gene ≈ {bot.gene_to_number_count(sub_gene)} data")

    if E_series_new:
        df=pd.DataFrame({"E":E_series_new})
        df["E=2"]=2
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df["E"], name="E"))
        fig.add_trace(go.Scatter(y=df["E=2"], name="E=2"))
        st.plotly_chart(fig, use_container_width=True)

    if E_series_2:
        df2=pd.DataFrame({"E":E_series_2})
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(y=df2["E"], name="E"))
        st.plotly_chart(fig2, use_container_width=True)

    st.metric("E hiện tại",f'{r1["E_now"]} ({r1["E_sample"]} streak)')
    st.metric("E dự đoán",r1["E_future"])
    st.metric("Entropy",r1["entropy"])
    st.metric("Entropy Trend",r1["entropy_trend"])
    st.metric("Reliability",f'{r1["reliability"]}%')

    st.success(r1["decision"])
