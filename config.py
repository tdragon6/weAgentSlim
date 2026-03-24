'''
    配置文件
'''


# 企业微信自建应用配置（此处图方便，建议环境变量）
wechat_config = {
    # 企业微信应用ID
    "CORP_ID": "xxx",
    # 自建应用ID
    "AGENT_ID": {
        "self": "xxx",
        "bot": "xxx"
    },
    # 自建应用Secret
    "SECRET": {
        "self": "xxx",
        "bot": "xxx"
    },
    # 自建应用回调Token
    "TOKEN": {
        "self": "xxx",
        "bot": "xxx"
    },
    # 自建应用回调EncodingAESKey
    "ENCODING_AES_KEY": {
        "self": "xxx",
        "bot": "xxx"
    },
}


# 腾讯云语音转文字API配置（此处图方便，建议环境变量），也可本地部署asr模型；腾讯云一句话语音识别每月有5000次免费额度
tencent_cloud = {
    "SECRET_ID": "xxx",
    "SECRET_KEY": "xxx",
}


# uri到bot_type的映射，需与企业微信自建应用配置中的回调地址一致
uri_bot_type_dict = {
    "/wechat/callback/self": "self",
    "/wechat/callback/bot": "bot"
}


# 自定义用户ID到标识的映射
self_user_id_dict = {
    'user_id_1': 'username_1',
    'user_id_2': 'username_2',
    'user_id_3': 'username_3'
}


# 规则文件列表映射，shared为共有
rule_files_list_dict = {
    "shared": ['AGENTS.md'],
    "self": ['IDENTITY.md', 'SOUL.md'],
    "bot": []
}


# 模型映射
model_dict = {
    "self": 'local/qwen/qwen3.5-9b',
    "bot": 'opencode/mimo-v2-omni-free'
}


# 技能映射，shared为共有
skills_dict = {
    "shared": ['reply-check', 'pua', 'high-agency', 'video-frames'],
    "self": [],
    "bot": []
}


# 微信请求代理，可连接固定IP代理，防止本地变化IP，为None时不开启代理
wechat_proxies = None
'''
wechat_proxies = {
    "http": "socks5h://127.0.0.1:1080",
    "https": "socks5h://127.0.0.1:1080"
}
'''
