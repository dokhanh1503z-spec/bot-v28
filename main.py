import numpy as np
from collections import Counter

########################################
# CONFIG
########################################

GENE_WINDOWS = [40,80,120]

SIM_THRESHOLD = 0.45

FORECAST_ROUNDS = 100

########################################
# ENCODE GENE
########################################

def encode_gene(results):

    gene=[]
    streak=1

    for i in range(1,len(results)):

        if results[i]==results[i-1]:
            streak+=1

        else:

            if streak>=4:
                gene.append("L")

            elif streak==2:
                gene.append("S")

            else:
                gene.append("X")

            streak=1

    return "".join(gene)

########################################
# STREAK ANALYSIS (NEW ENGINE)
########################################

def streak_distribution(results):

    streaks=[]
    streak=1

    for i in range(1,len(results)):

        if results[i]==results[i-1]:
            streak+=1

        else:

            streaks.append(streak)
            streak=1

    streaks.append(streak)

    s2=0
    s3=0
    s4=0

    for s in streaks:

        if s==2:
            s2+=1

        elif s==3:
            s3+=1

        elif s>=4:
            s4+=1

    total=len(streaks)

    if total==0:
        return 0,0,0

    return s2/total,s3/total,s4/total

########################################
# SIMILARITY
########################################

def similarity(a,b):

    length=min(len(a),len(b))

    score=0

    for i in range(length):

        if a[i]==b[i]:
            score+=1

    return score/length

########################################
# GENE MATCH
########################################

def find_matches(current_gene,history_genes):

    matches=[]

    for g in history_genes:

        sim=similarity(current_gene,g)

        if sim>SIM_THRESHOLD:

            matches.append((g,sim))

    return matches

########################################
# WEIGHTED VOTING
########################################

def weighted_vote(matches):

    long_score=0
    short_score=0

    for g,sim in matches:

        if g.count("L")>g.count("S"):

            long_score+=sim

        else:

            short_score+=sim

    return long_score,short_score

########################################
# ENTROPY
########################################

def entropy(seq):

    count=Counter(seq)

    total=len(seq)

    e=0

    for c in count.values():

        p=c/total

        e-=p*np.log2(p)

    return e

########################################
# CYCLE LENGTH PREDICTOR (NEW)
########################################

def cycle_length_predictor(results):

    streaks=[]
    streak=1

    for i in range(1,len(results)):

        if results[i]==results[i-1]:

            streak+=1

        else:

            streaks.append(streak)

            streak=1

    streaks.append(streak)

    avg=np.mean(streaks)

    if avg>=3.5:

        return "LONG_CYCLE"

    if avg<=2:

        return "SHORT_CYCLE"

    return "MIXED"

########################################
# MULTI WINDOW ANALYSIS
########################################

def multi_gene_analysis(results,history):

    predictions=[]

    all_matches=[]

    for window in GENE_WINDOWS:

        gene_now=encode_gene(results[-window:])

        matches=find_matches(gene_now,history)

        long_score,short_score=weighted_vote(matches)

        predictions.append((long_score,short_score,len(matches)))

        all_matches+=matches

    return predictions,all_matches

########################################
# FINAL PREDICTION
########################################

def final_prediction(predictions):

    long_total=0
    short_total=0

    for l,s,m in predictions:

        weight=m+1

        long_total+=l*weight

        short_total+=s*weight

    if long_total>short_total:

        return "LONG"

    return "SHORT"

########################################
# FORECAST ENGINE
########################################

def forecast(matches):

    long_cases=0
    short_cases=0

    for g,sim in matches:

        if g.count("L")>g.count("S"):

            long_cases+=1

        else:

            short_cases+=1

    total=long_cases+short_cases

    if total==0:

        return 0,0

    return long_cases/total,short_cases/total

########################################
# MAIN ANALYSIS
########################################

def analyze(results,history):

    predictions,all_matches=multi_gene_analysis(results,history)

    prediction=final_prediction(predictions)

    long_pct,short_pct=forecast(all_matches)

    e=entropy(results)

    s2,s3,s4=streak_distribution(results)

    cycle_type=cycle_length_predictor(results)

    return{

        "prediction":prediction,

        "entropy":e,

        "forecast_long":long_pct,

        "forecast_short":short_pct,

        "streak2_prob":s2,

        "streak3_prob":s3,

        "streak4plus_prob":s4,

        "cycle_type":cycle_type,

        "matches":len(all_matches)
    }
