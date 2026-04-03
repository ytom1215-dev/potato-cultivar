import streamlit as st
import pandas as pd
from PIL import Image
import os

# --- 1. データの準備（図鑑用） ---
potato_data = {
    "No": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "品種名": ["ニシユタカ", "デジマ", "さんじゅう丸", "ながさき黄金", "アイマサリ", "しまあかり", "こいじゃ", "とうや", "ホッカイコガネ", "メークイン", "トヨシロ", "オホーツクチップ"],
    "交配親（母×父）": ["デジマ × 長系65号", "北海31号 × ウンゼン", "長系107号 × 春あかり", "西海35号 × 西海33号", "愛系158 × アイユタカ", "デジマ × アローワ", "ニシユタカ × サクラフブキ", "R392-50 × WB 77025-2", "トヨシロ × 北海51号", "不明（英国在来種）", "「北海19号」×「エニワ」", "「アトランチック」×「ND8」"],
    "用途": ["青果", "青果", "青果", "青果", "青果", "青果", "青果", "青果", "青果・加工", "青果", "チップ", "チップ"],
    "熟期": ["中晩生", "中晩生", "中晩生", "中晩生", "中晩生　実際はかなり早生", "中晩生", "中晩生", "早生", "中晩生", "中早生", "中早生", "早生"],
    "休眠期間": ["やや短", "短", "短", "短", "短", "やや短", "中", "やや長", "極長", "長", "長", "やや短"],
    "形": ["扁球～楕円", "扁短楕円", "球～楕円", "卵～楕円", "短卵～円", "球～扁球", "短卵", "球", "長楕円", "長楕円", "扁球（扁平度強い）", "球"],
    "肉色": ["淡黄", "白黄", "白", "濃黄", "明黄～淡黄", "淡黄～黄", "明黄", "黄", "黄～淡黄", "淡黄～白黄", "白", "白"],
    "病害抵抗性": ["PCN: 無 hhhh", "PCN: 無 hhhh", "PCN: 有 Hhhh そうか病: 強", "青枯病: 比較的強、PCN: 有 Hhhh、PVY: 有", "PCN: 有 Hhhh、PVY: 有", "PCN: 有 Hhhh", "PCN: 有 Hhhh", "PCN: 有（HHhh）、PVY: 有", "PCN: 有 Hhhh、そうか病: やや弱、疫病: 弱", "PCN: 無 hhhh", "PCN: 無 hhhh、軟腐に弱い", "PCN: 有 Hhhh"],
    "特徴": ["塊茎腐敗しにくい、休眠期間がやや長く二期作で限界の長さ", "地上部旺盛、食味は良、最近は面積が減少、以前は徳之島天城町で多かった", "でんぷん価が低い、塊茎腐敗しやすい、そうか病抵抗性の普及品種はこれだけ", "インカのめざめを親にもつ、内部異常、壱岐黄金など特殊利用、青枯病に強い", "ポテトサラダ向き、個人的には二期作向きで有望と思っているが、早生すぎ？", "鹿児島県育成の最初の品種、日長・温度反応が独特、完全にはわからないが、CDF1のアレルが２なのが影響している？", "チルド加工用品種、沖永良部で利用ができない検討中、感覚的には冬作はやや低収、春作のほうが多収", "チルド加工用に利用、褐色心腐・裂開が発生しやすい、中心に褐心がでやすい、形が球なので、中心が酸欠になりやすい？", "チルド加工用に利用、打撲、褐心がほとんどでない、細胞が小さい、褐色になる酵素そのものが少ないなど優点をもつ", "鹿児島県では低収、ちゃんと育った経験がない", "「じゃがりこ」はこの品種じゃないとだめらしい、腐れやすいのが最大の欠点、大玉で多収", "塊茎腐敗しにくく、面積が拡大中であるが、早生のため可能な限り地上部を持たせることが重要、農薬散布の徹底、生産物はコレ"]
}
df_potato = pd.DataFrame(potato_data)

# --- 2. 四倍体の配偶子形成確率（染色体分離モデル） ---
# キーは優性対立遺伝子(H)の数。バリューは生成される配偶子の{優性遺伝子の数: 確率}
gamete_probs = {
    4: {2: 1.0},                                      # HHHH -> HH(1.0)
    3: {2: 0.5, 1: 0.5},                              # HHHh -> HH(0.5), Hh(0.5)
    2: {2: 1/6, 1: 4/6, 0: 1/6},                      # HHhh -> HH(1/6), Hh(4/6), hh(1/6)
    1: {1: 0.5, 0: 0.5},                              # Hhhh -> Hh(0.5), hh(0.5)
    0: {0: 1.0}                                       # hhhh -> hh(1.0)
}

genotype_labels = {
    4: "HHHH (四重式: Quadruplex)",
    3: "HHHh (三重式: Triplex)",
    2: "HHhh (二重式: Duplex)",
    1: "Hhhh (単重式: Simplex)",
    0: "hhhh (零重式: Nulliplex)"
}

# --- 3. アプリ全体の構成 ---
st.set_page_config(page_title="Potato Lab Pro", layout="wide")

st.sidebar.title("🧬 Potato Lab Pro")
app_mode = st.sidebar.radio("機能を選択してください", ["品種図鑑", "遺伝分離シミュレーター"])

# --- 4. 【機能1】品種図鑑 ---
if app_mode == "品種図鑑":
    st.title("🥔 鹿児島県 バレイショ品種図鑑")
    
    selected_name = st.sidebar.selectbox("品種名を選択", df_potato["品種名"].tolist())
    selected_data = df_potato[df_potato["品種名"] == selected_name].iloc[0]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"📷 No.{selected_data['No']} {selected_data['品種名']}")
        img_path = f"No{selected_data['No']}.jpg"
        if os.path.exists(img_path):
            st.image(Image.open(img_path), use_container_width=True)
        else:
            st.warning(f"画像ファイル「{img_path}」が見つかりません。")

    with col2:
        st.subheader("📋 品種詳細情報")
        specs = {
            "項目": ["交配親", "用途", "熟期", "休眠期間", "形", "肉色", "病害抵抗性"],
            "内容": [selected_data['交配親（母×父）'], selected_data['用途'], selected_data['熟期'], selected_data['休眠期間'], selected_data['形'], selected_data['肉色'], selected_data['病害抵抗性']]
        }
        st.table(pd.DataFrame(specs))
        st.success(f"**【特徴】**\n\n{selected_data['特徴']}")

# --- 5. 【機能2】遺伝分離シミュレーター ---
elif app_mode == "遺伝分離シミュレーター":
    st.title("🧬 四倍体 遺伝分離シミュレーター")
    st.markdown("ジャガイモ（同質四倍体）の特定の単一遺伝子（例: $H1$ 病害抵抗性遺伝子）における交配結果をシミュレーションします。")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("母本 (Female)")
        p1_genotype = st.selectbox("母本の遺伝子型", options=[4, 3, 2, 1, 0], format_func=lambda x: genotype_labels[x], index=2, key="p1")

    with col2:
        st.subheader("父本 (Male)")
        p2_genotype = st.selectbox("父本の遺伝子型", options=[4, 3, 2, 1, 0], format_func=lambda x: genotype_labels[x], index=0, key="p2")

    if st.button("次代の表現型・遺伝子型を計算"):
        st.divider()
        st.subheader("📊 期待される次世代 (F1) の分離比")

        # 配偶子の確率を取得
        g1_probs = gamete_probs[p1_genotype]
        g2_probs = gamete_probs[p2_genotype]

        # F1の遺伝子型を計算
        f1_genotypes = {4: 0.0, 3: 0.0, 2: 0.0, 1: 0.0, 0: 0.0}
        
        for g1_alleles, g1_prob in g1_probs.items():
            for g2_alleles, g2_prob in g2_probs.items():
                f1_alleles = g1_alleles + g2_alleles
                f1_genotypes[f1_alleles] += g1_prob * g2_prob

        # 表現型の計算 (優性Hが1つでもあれば発現)
        dominant_pheno = sum(prob for alleles, prob in f1_genotypes.items() if alleles > 0)
        recessive_pheno = f1_genotypes[0]

        # 結果表示用カラム
        res_col1, res_col2 = st.columns(2)

        with res_col1:
            st.markdown("### 🧬 遺伝子型の割合")
            f1_df = pd.DataFrame([
                {"遺伝子型": genotype_labels[k].split(" ")[0], "出現確率 (%)": f"{v*100:.1f}"} 
                for k, v in f1_genotypes.items() if v > 0
            ])
            st.table(f1_df)

        with res_col2:
            st.markdown("### 🥔 表現型の割合")
            pheno_df = pd.DataFrame({
                "表現型": ["優性 (抵抗性など)", "劣性 (感受性など)"],
                "出現確率 (%)": [f"{dominant_pheno*100:.1f}", f"{recessive_pheno*100:.1f}"]
            })
            st.table(pheno_df)
            
            # 5:1 などの整数比でのヒント表示
            if p1_genotype == 2 and p2_genotype == 0:
                st.info("💡 **ワンポイント解説**: 二重式(Duplex)と零重式(Nulliplex)の交配では、表現型はおおよそ **5 : 1** に分離します。二倍体のメンデル遺伝（1:1）とは異なる四倍体特有の現象です。")

        st.caption("※この計算は染色体分離（Chromosome segregation）を前提とした理論値です。実際の育種現場では、動原体からの距離による二重還元（Double reduction）の影響でわずかに数値が変動する場合があります。")

# --- 6. 共通フッター ---
st.sidebar.divider()
st.sidebar.caption("© 2026 Potato Breeding Support Tool")
