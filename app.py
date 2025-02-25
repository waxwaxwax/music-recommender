import os
import logging
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# .envファイルから環境変数を読み込み
load_dotenv()

app = Flask(__name__)

# ログの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")

# 必須環境変数のチェック
required_env_vars = [AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, DEPLOYMENT_NAME, API_VERSION]
if not all(required_env_vars):
    raise ValueError("環境変数が不足しています。API設定を確認してください。")

# Azure API用のリトライ付きセッション
def get_session_with_retries(retries=3, backoff_factor=1.0, status_forcelist=(500, 502, 503, 504)):
    """Azure OpenAI API 用のリトライ機能付きセッションを作成"""
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# リトライ機能付きセッション（タイムアウトは30秒）
azure_session = get_session_with_retries()

@app.route("/")
def index():
    """メインページ"""
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    """Azure OpenAI を使用した音楽推薦 API"""
    data = request.get_json()
    situation = data.get("situation", "").strip()
    genre = data.get("genre", "").strip()
    era = data.get("era", "").strip()

    if not situation or not genre or not era:
        return jsonify({"error": "無効な入力", "details": "すべてのフィールドを入力してください"}), 400

    prompt = f"""以下の条件に従って、{situation}、{era}の{genre}音楽について情報を生成してください。

🎵 【条件】 🎵
- シチュエーション: {situation}
- 音楽ジャンル: {genre}
- 年代: {era}

【出力フォーマット】

曲名:
<曲名>

アーティスト:
<アーティスト名>

年代:
<年代>

作詞・作曲:
<作詞作曲者>

🎵説明🎵:
楽曲の特徴、背景、雰囲気などを簡潔に記述してください。15文字程度で改行し、視認性を高めてください。

🔥おすすめ理由🔥:
なぜこの曲が {situation} に適しているのかを説明してください。

👇おすすめ曲のYouTube👇
<a href='<リンク>' target='_blank'>YouTubeで聴く</a>
"""

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1200,
        "temperature": 1,
        "top_p": 1,
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY,
    }

    openai_url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"

    try:
        response = azure_session.post(openai_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Azure OpenAI APIエラー: %s", str(e))
        return jsonify({"error": "APIリクエスト失敗", "details": str(e)}), 500

    try:
        result = response.json()
        text_response = result["choices"][0]["message"]["content"].strip()
    except (KeyError, ValueError) as e:
        logger.error("APIレスポンス解析エラー: %s", str(e))
        return jsonify({"error": "無効なAPIレスポンス", "details": str(e)}), 500

    logger.info("音楽レコメンド成功")
    return jsonify({"recommendation": text_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
