from cryptography.fernet import Fernet
import base64
import os
from ..config.settings import settings


class CryptoUtil:
    """API Key 加密工具"""

    def __init__(self):
        # 从环境变量或配置读取密钥
        key = settings.SECRET_KEY or os.environ.get("RENWEI_SECRET_KEY")
        if not key:
            # 开发环境自动生成（生产环境必须配置）
            key = Fernet.generate_key().decode()
            print("⚠️  警告: 使用自动生成的加密密钥，生产环境请配置 RENWEI_SECRET_KEY")

        # 确保密钥是 32 字节 base64
        if len(key) < 32:
            key = base64.urlsafe_b64encode(key.ljust(32, '0').encode()).decode()

        self.fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str) -> str:
        """加密"""
        if not plaintext:
            return None
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """解密"""
        if not ciphertext:
            return None
        return self.fernet.decrypt(ciphertext.encode()).decode()


crypto = CryptoUtil()