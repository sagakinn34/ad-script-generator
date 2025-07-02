import streamlit as st
import whisper
import openai
import csv
import tempfile

# OpenAI APIキー
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ユーザー画面
st.title("📽️ 動画広告の台本自動生成ツール（Streamlit Cloud対応）")

# 音声ファイルアップロード
uploaded_file = st.file_uploader("🎧 音声ファイル（mp3）をアップロードしてください", type=["mp3"])

# カテゴリ選択
category = st.selectbox("📦 商材カテゴリを選んでください", ["美容サプリ", "健康食品", "育毛剤"])

if st.button("▶️ 台本を生成する"):
    if uploaded_file is None:
        st.warning("音声ファイルをアップロードしてください。")
        st.stop()

    st.info("処理中です。しばらくお待ちください…")

    # 一時ファイルとして保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Whisperで文字起こし
    model = whisper.load_model("base")
    result = model.transcribe(tmp_path)
    transcript = result["text"]

    # キーワード辞書（CSV）を読み込み
    keywords = []
    with open("keyword_db.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["category"] == category:
                keywords = row["keywords"].split(",")
                break

    # GPTにプロンプト送信
    prompt = f"""
以下の文字起こしを元に、広告の構成を抽出し、{category}の台本を30秒動画用で作成してください。
以下のキーワードを自然に入れてください：{', '.join(keywords)}

【文字起こし】
{transcript}
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    script = response["choices"][0]["message"]["content"]
    st.success("✅ 台本が生成されました！")
    st.text_area("✏️ 出力された台本はこちら", script, height=400)
