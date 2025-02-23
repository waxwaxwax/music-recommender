import os
import logging
import msal
from flask import Blueprint, redirect, request, session as flask_session, url_for
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

# ログの設定
logger = logging.getLogger(__name__)

# 環境変数の読み込み
AZURE_AD_TENANT_ID = os.getenv("AZURE_AD_TENANT_ID")
AZURE_AD_CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID")
AZURE_AD_CLIENT_SECRET = os.getenv("AZURE_AD_CLIENT_SECRET")
AZURE_AD_AUTHORITY = os.getenv("AZURE_AD_AUTHORITY")
AZURE_AD_REDIRECT_URI = os.getenv("AZURE_AD_REDIRECT_URI", "http://localhost:8000/getToken")
AZURE_AD_SCOPE = [os.getenv("AZURE_AD_SCOPE", "User.Read")]

# Flask Blueprint（Flaskのサブアプリ）
auth_bp = Blueprint("auth", __name__)

def get_msal_app():
    """MSALインスタンスを作成"""
    return msal.ConfidentialClientApplication(
        AZURE_AD_CLIENT_ID, authority=AZURE_AD_AUTHORITY,
        client_credential=AZURE_AD_CLIENT_SECRET
    )

@auth_bp.route("/login")
def login():
    """Azure AD でのサインイン処理"""
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        AZURE_AD_SCOPE, redirect_uri=AZURE_AD_REDIRECT_URI
    )
    return redirect(auth_url)

@auth_bp.route("/getToken")
def get_token():
    """Azure AD からのリダイレクト後の処理"""
    code = request.args.get("code")
    if not code:
        return redirect(url_for("index"))

    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=AZURE_AD_SCOPE,
        redirect_uri=AZURE_AD_REDIRECT_URI
    )

    if "access_token" in result:
        flask_session["user"] = result.get("id_token_claims")  # ユーザー情報をセッションに保存
        logger.info(f"ログイン成功: {flask_session['user']}")
        return redirect(url_for("index"))
    else:
        logger.error(f"ログインエラー: {result.get('error_description')}")
        return {"error": "ログイン失敗", "details": result.get("error_description")}, 400

@auth_bp.route("/logout")
def logout():
    """Azure AD からログアウトし、セッションを完全にクリア"""
    logger.info(f"ログアウト開始: {flask_session.get('user')}")

    # Flask セッションをクリア
    flask_session.clear()

    logout_url = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/oauth2/v2.0/logout?post_logout_redirect_uri={url_for('index', _external=True)}"
    
    logger.info(f"Azure AD ログアウト URL: {logout_url}")
    
    return redirect(logout_url)
