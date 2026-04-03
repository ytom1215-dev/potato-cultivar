import streamlit as st
import pandas as pd
from PIL import Image
import os

# 保存先のファイル名
DATA_FILE = "potato_data.csv"

# --- 1. データの初期化と読み込み ---
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # 初回実行時：既存のデータをDataFrameにしてCSV保存
        initial_data = {
            "No": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "品種名": ["ニシユタカ", "デジマ", "さんじゅう丸", "ながさき黄金", "アイマサリ", "しまあかり", "こいじゃ", "とうや", "ホッカイコガネ", "メークイン", "トヨシロ", "オホーツクチップ"],
            "交配親（母×父）": ["デジマ × 長系65号", "北海31号 × ウンゼン", "長系107号 × 春あかり", "西海35号 × 西海33号", "愛系158 × アイユタカ", "デジマ × アローワ", "ニシユタカ × サクラフブキ", "R392-50 × WB 77025-2", "トヨシロ × 北海51号", "不明（英国在来種）", "「北海19号」×「エニワ」", "「アトランチック」×「ND8」"],
            "用途": ["青果", "青果", "青果", "青果", "青果", "青果", "青果", "青果", "青果・加工", "青果", "チップ", "チップ"],
            "熟期": ["中晩生", "中晩生", "中晩生", "中晩生", "中晩生　実際はかなり早生", "中晩生", "中晩生", "早生", "中晩生", "中早生", "中早生", "早生"],
            "休眠期間": ["やや短", "短", "短", "短", "短", "やや短", "中", "やや長", "極長", "長", "長", "やや短"],
            "形": ["扁球～楕円", "扁短楕円", "球～楕円", "卵～楕円", "短卵～円", "球～扁球", "短卵", "球", "長楕円", "長楕円", "扁球（扁平度強い）", "球"],
            "肉色": ["淡黄", "白黄", "白", "濃黄", "明黄～淡黄", "淡黄～黄", "明黄", "黄", "黄～淡黄", "淡黄～白黄", "白", "白"],
            "病害抵抗性": ["PCN: 無", "PCN: 無", "PCN: 有 そうか病: 強", "青枯病: 比較的強、PCN: 有、PVY: 有", "PCN: 有、PVY: 有", "PCN: 有", "PCN: 有", "PCN: 有（H1二重）、PVY: 有", "PCN: 有、そうか病: やや弱、疫病: 弱", "PCN: 無", "PCN: 無、軟腐に弱い", "PCN: 有"],
            "特徴": ["塊茎腐敗しにくい、休眠期間がやや長く二期作で限界の長さ", "地上部旺盛、食味は良、最近は面積が減少、以前は徳之島天城町で多かった", "でんぷん価が低い、塊茎腐敗しやすい、そうか病抵抗性の普及品種はこれだけ", "インカのめざめを親にもつ、内部異常、壱岐黄金など特殊利用、青枯病に強い", "ポテトサラダ向き、個人的には二期作向きで有望と思っているが、早生すぎ？", "鹿児島県育成の最初の品種、日長・温度反応が独特、完全にはわからないが、CDF1のアレルが２なのが影響している？", "チルド加工用品種、沖永良部で利用ができない検討中、感覚的には冬作はやや低収、春作のほうが多収", "チルド加工用に利用、褐色心腐・裂開が発生しやすい、中心に褐心がでやすい、形が球なので、中心が酸欠になりやすい？", "チルド加工用に利用、打撲、褐心がほとんどでない、細胞が小さい、褐色になる酵素そのものが少ないなど優点をもつ", "鹿児島県では低収、ちゃんと育った経験がない", "「じゃがりこ」はこの品種じゃないとだめらしい、腐れやすいのが最大の欠点、大玉で多収", "塊茎腐敗しにくく、面積が拡大中であるが、早生のため可能な限り地上部を持たせることが重要、農薬散布の徹底、生産物はコレ"],
            "ベテランの意見": [""] * 12  # 初期は空欄
        }
        new_df = pd.DataFrame(initial_data)
        new_df.to_csv(DATA_FILE, index=False)
        return new_df

# データの読み込み
df = load_data()

# --- 2. StreamlitアプリのUI構築 ---
st.set_page_config(page_title="バレイショ品種図鑑", layout="wide")
st.title("🥔 鹿児島県 バレイショ品種図鑑")

# サイドバーで品種を選択
st.sidebar.header("品種を選択してください")
selected_name = st.sidebar.selectbox("品種名", df["品種名"].tolist())

# 選択された品種の行インデックスを取得
idx = df[df["品種名"] == selected_name].index[0]
selected_data = df.iloc[idx]

# --- 3. メイン画面の表示レイアウト ---
col1, col2 = st.columns([1, 1])

# 左側：写真
with col1:
    st.subheader(f"No.{selected_data['No']} {selected_data['品種名']} の写真")
    image_filename = f"No{selected_data['No']}.jpg"
    if os.path.exists(image_filename):
        image = Image.open(image_filename)
        st.image(image, caption=f"No.{selected_data['No']} {selected_data['品種名']}", use_container_width=True)
    else:
        st.warning(f"画像ファイル「{image_filename}」が見つかりません。")

# 右側：品種データと意見入力
with col2:
    st.subheader("品種詳細情報")
    st.write(f"**交配親:** {selected_data['交配親（母×父）']}")
    st.write(f"**用途:** {selected_data['用途']}")
    st.write(f"**熟期:** {selected_data['熟期']}")
    st.write(f"**休眠期間:** {selected_data['休眠期間']}")
    st.write(f"**形:** {selected_data['形']}")
    st.write(f"**肉色:** {selected_data['肉色']}")
    st.write(f"**病害抵抗性:** {selected_data['病害抵抗性']}")
    
    st.info(f"**特徴:**\n\n{selected_data['特徴']}")

    # --- ベテラン技術員の意見入力エリア ---
    st.divider()
    st.subheader("👨‍🌾 ベテラン技術員の意見")
    
    # テキストエリアの初期値に現在の保存内容を表示
    current_opinion = selected_data["ベテランの意見"] if pd.notna(selected_data["ベテランの意見"]) else ""
    new_opinion = st.text_area("追加の知見や現場の声を記入してください", value=current_opinion, height=150)

    if st.button("意見を保存する"):
        # DataFrameを更新してCSVに書き込み
        df.at[idx, "ベテランの意見"] = new_opinion
        df.to_csv(DATA_FILE, index=False)
        st.success(f"{selected_name} の意見を保存しました！")
        # 再読み込み（表示を最新にするため）
        st.rerun()

    # 保存されている意見がある場合は表示（テキストエリア以外でも確認用）
    if current_opinion:
        st.markdown("---")
        st.write("**現在の登録内容:**")
        st.write(current_opinion)
