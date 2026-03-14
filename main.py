class UltimateBotV29:
    def __init__(self, data):
        self.raw_data = data
        self.cl_seq = [x % 2 == 0 for x in data]
        self.tn_seq = [x > 2 for x in data]

    # --- TÌM STREAK ---
    def get_streaks(self, sequence):
        if not sequence:
            return []

        streaks = []
        count = 1

        for i in range(1, len(sequence)):
            if sequence[i] == sequence[i-1]:
                count += 1
            else:
                streaks.append(count)
                count = 1

        streaks.append(count)
        return streaks

    # --- MÃ HOÁ GENE ---
    def encode_gene(self, streaks):

        encoded = []

        for s in streaks:

            if s == 1:
                encoded.append("X")

            elif s < 4:
                encoded.append("S")

            else:
                encoded.append("L")

        return encoded

    # --- TÌM CẤU TRÚC QUÁ KHỨ ---
    def find_structures(self, encoded):

        window = 90
        structures = []

        for i in range(len(encoded) - window):

            sub = encoded[i:i+window]

            if sub.count("L") >= 10:
                structures.append(sub)

        return structures

    # --- SO KHỚP GENE ---
    def similarity(self, current, past):

        match = 0
        min_len = min(len(current), len(past))

        for i in range(min_len):

            if current[-i-1] == past[-i-1]:
                match += 1

        return (match / min_len) * 100

    # --- PHÂN TÍCH ---
    def analyze(self, sequence, name):

        streaks = self.get_streaks(sequence)

        encoded = self.encode_gene(streaks)

        vision = 90

        current = encoded[-vision:]

        past_structures = self.find_structures(encoded)

        max_sim = 0

        for p in past_structures:

            sim = self.similarity(current, p)

            if sim > max_sim:
                max_sim = sim

        # --- ÁP SUẤT S ---
        s_list = [s for s in streaks if s < 4]
        recent_s = s_list[-30:]

        avg_s = sum(recent_s) / len(recent_s) if recent_s else 0

        # --- TRẠNG THÁI ---
        pressure_msg = "Ổn định"

        if avg_s > 2.7:
            pressure_msg = "🔥 RẤT CĂNG"

        elif avg_s > 2.45:
            pressure_msg = "⚠️ Đang nén"

        # --- QUYẾT ĐỊNH ---
        if max_sim > 70 and avg_s > 2.6:

            horizon = "🔭 Vision 90: Khớp cấu trúc Tiền Bão"
            decision = "🎯 ĐU MẠNH"

        elif len(streaks) > 0 and streaks[-1] >= 4:

            horizon = "🌊 ĐANG TRONG BÃO"
            decision = "🎯 ĐU"

        else:

            horizon = "🧊 Cấu trúc phân mảnh"
            decision = "🛡️ CHỜ"

        return {
            "name": name,
            "avg_s": avg_s,
            "pressure": pressure_msg,
            "pattern": " -> ".join(encoded[-12:]),
            "sim": max_sim,
            "horizon": horizon,
            "decision": decision,
            "color": "#00cec9"
        }
