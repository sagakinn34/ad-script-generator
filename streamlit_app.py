import streamlit as st
import whisper
import openai
import csv
import subprocess

# OpenAI APIキーをここに貼ってください（例: sk-abc123...）
import streamlit as st
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ユーザー画面
st.title("📽️ 動画広告の台本自動生成ツール")
video_url = st.text_input("🎥 動画のURLを入力してください")
category = st.selectbox("📦 商材カテゴリを選んでください", ["美容サプリ", "健康食品", "育毛剤"])

if st.button("▶️ 台本を生成する"):
    st.info("動画を処理中です。しばらくお待ちください…")

    # ① 動画から音声抽出（yt-dlpを使ってmp3に）
    subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", video_url, "-o", "audio.%(ext)s"])

    # ② Whisperで文字起こし
    model = whisper.load_model("base")
    result = model.transcribe("audio.mp3")
    transcript = result["text"]

    # ③ キーワード辞書（CSV）を読み込み
    keywords = []
    with open("keyword_db.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["category"] == category:
                keywords = row["keywords"].split(",")
                break

    # ④ GPTにプロンプトを送信
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

    # 出力された台本を表示
    script = response["choices"][0]["message"]["content"]
    st.success("✅ 台本が生成されました！")
    st.text_area("✏️ 出力された台本はこちら", script, height=400)

