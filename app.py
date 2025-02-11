import os
import logging
import re
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# .envファイルから環境変数を読み込み
load_dotenv()

app = Flask(__name__)

# ログの設定（INFOレベル以上を出力）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")

def get_session_with_retries(retries=3, backoff_factor=1.0, status_forcelist=(500, 502, 503, 504)):
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
session = get_session_with_retries()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    mood = data.get('mood', '')
    genre = data.get('genre', '')
    era = data.get('era', '')
    
    # 改良したプロンプト（各項目は十分な改行と余白を入れるように指示）
    prompt = f"""以下の条件に従って、{era}の{genre}音楽について情報を生成してください。

【出力フォーマット】

曲名 
<曲名>
<一行空ける>
アーティスト 
<アーティスト名>
<一行空ける>
<年代>
<一行空ける>
作詞 ...作曲 ...の順番で記述
🎵 説明 🎵: 
<一行空ける>
<楽曲の特徴、背景、雰囲気などを、1行15文字程度で簡潔に記述してください。>
<一行空ける>
👇 おすすめ曲のYouTube 👇: 
<一行空ける>
<リンク>
<一行空ける>
【注意事項】

・回答の冒頭に「もちろん！」などの挨拶文は付けないでください。

・回答内にMarkdown記法（例：**）は使用しないでください。

・おすすめ曲は最大3曲までとし、最終出力ではリンクは1つだけにすること。

・各項目は改行を2行以上入れて見やすくしてください。

・YouTube のリンクが見つかる曲だけを出力するようにして。リンクをクリックしても再生されないことがあります。https://www.youtube.com/watch?v=exampleは再生されません。

以上のフォーマットに従って、回答してください。"""

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1200,
        "temperature": 0.7,
        "top_p": 1
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY
    }
    
    openai_url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
    
    try:
        response = session.post(openai_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Azure OpenAI APIエラー: %s", str(e))
        return jsonify({"error": "API request failed", "details": str(e)}), 500
    
    try:
        result = response.json()
        text_response = result["choices"][0]["message"]["content"].strip()
    except (KeyError, ValueError) as e:
        logger.error("APIレスポンス解析エラー: %s", str(e))
        return jsonify({"error": "Invalid API response", "details": str(e)}), 500

    logger.info("フォーマットに沿ったレコメンド生成に成功")
    return jsonify({"recommendation": text_response})

if __name__ == '__main__':
    app.run(debug=True)
