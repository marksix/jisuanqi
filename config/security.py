from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
import os

def configure_security(app):
    # 从环境变量获取密钥
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
    
    # 初始化CSRF保护
    CSRFProtect(app)
    
    # 安全头设置
    Talisman(
        app,
        force_https=bool(os.environ.get('FLASK_ENV') == 'production'),
        strict_transport_security=True,
        session_cookie_secure=True,
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'"],
            'style-src': ["'self'", "'unsafe-inline'"]
        }
    )