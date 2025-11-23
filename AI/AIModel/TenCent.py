import base64
import json
import os
import re
import uuid

from dotenv import load_dotenv
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tts.v20190823 import tts_client, models

load_dotenv(r"D:\GridFriend\AI\apiKey.env")
SECRET_ID = os.getenv("Tencent_SecretId")
SECRET_KEY = os.getenv("Tencent_SecretKey")

class TenCent:
    def __init__(self, text, path, voice_type: int = 603004, speed: int = 0):
        self.text = text
        self.path = path
        self.voice_type = voice_type
        self.speed = speed

    def clean_text(self):
        """清洗文本：去掉小括号及内容、表情包"""
        # 1. 去掉小括号（包括中英文括号）及括号内所有内容
        text = re.sub(r'[（(][^）)]*[）)]', '', self.text)
        # 2. 去掉表情包（匹配Unicode表情符号区间）
        text = re.sub(r'[\U00010000-\U0010ffff\u200d\u2640-\u2642\u2600-\u2b55\u23cf\u23e9\u231a\u3030\u2702-\u27b0]', '', text)
        # 3. 去掉多余空格（可选，根据需求保留）
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def split_text(self, max_length=149):
        """先清洗再分段"""
        cleaned_text = self.clean_text()
        return [cleaned_text[i:i + max_length] for i in range(0, len(cleaned_text), max_length)]

    def tts_connect(self):
        cred = credential.Credential(SECRET_ID, SECRET_KEY)
        httpProfile = HttpProfile(endpoint="tts.tencentcloudapi.com")
        clientProfile = ClientProfile(httpProfile=httpProfile)
        client = tts_client.TtsClient(cred, "ap-beijing", clientProfile)

        full_audio_base64 = b""
        for t in self.split_text():
            if not t:  # 跳过空分段
                continue
            req = models.TextToVoiceRequest()
            req.from_json_string(json.dumps({
                "Text": t,
                "ModelType": 1,
                "VoiceType": self.voice_type,
                "Codec": "mp3",
                "Speed": self.speed,
                "Volume": 5,
                "SessionId": str(uuid.uuid1())
            }))

            resp = client.TextToVoice(req)
            full_audio_base64 += resp.Audio.encode("utf-8")

        audio_data = base64.b64decode(full_audio_base64)
        return audio_data

    def simple_tts(self):
        try:
            audio_data = self.tts_connect()
            with open(self.path, "wb") as f:
                f.write(audio_data)
            # 可选：返回文件大小，保持之前的用法
            return os.path.getsize(self.path)
        except Exception as e:
            print(f"TTS生成失败：{e}")
            return 0