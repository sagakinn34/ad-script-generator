import streamlit as st
import whisper
import openai
import csv
import subprocess
import os

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("📽️ 動画広告の台本自動生成ツール（Streamlit Cloud対応）")
video_url = st.text_input("🎥 動画のURLを入力してください（例: YouTubeのURL）")
category = st.selectbox("📦 商材カテゴリを選んでください", ["美容サプリ", "健康食品", "育毛剤"])

if st.button("▶️ 台本を生成する"):
    st.info("動画を処理中です。しばらくお待ちください…")

    # ① 動画から音声抽出（yt-dlp使用）
    output_filename = "audio.mp3"
    command = ["yt-dlp", "-x", "--audio-format", "mp3", "-o", output_filename, video_url]
    try:
        subprocess.run(command, check=True)
    except Exception as e:
        st.error(f"音声抽出でエラーが発生しました: {e}")
        st.stop()

    # ② Whisperで文字起こし
    try:
        model = whisper.load_model("base")
        result = model.transcribe(output_filename)
        transcript = result["text"]
    except Exception as e:
        st.error(f"文字起こしでエラーが発生しました: {e}")
        st.stop()

    # ③ キーワードCSVの読み込み
    keywords = []
    try:
        with open("keyword_db.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["category"] == category:
                    keywords = row["keywords"].split(",")
                    break
    except Exception as e:
        st.error(f"キーワードCSVの読み込みエラー: {e}")
        st.stop()

    # ④ GPTで台本生成
    prompt = f"""
以下の文字起こしを元に、広告の構成を抽出し、{category}の台本を30秒動画用で作成してください。
以下のキーワードを自然に入れてください：{', '.join(keywords)}

【文字起こし】
{transcript}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        script = response["choices"][0]["message"]["content"]
        st.success("✅ 台本が生成されました！")
        st.text_area("✏️ 出力された台本はこちら", script, height=400)
    except Exception as e:
        st.error(f"GPTでの生成エラー: {e}")

    # 後処理：音声ファイルを削除
    if os.path.exists(output_filename):
        os.remove(output_filename)
