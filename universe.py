'''
    运行时全局配置和变量
'''


import os
import logging
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor


# 根目录
root_dir = os.path.dirname(os.path.abspath(__file__))


# 日志配置
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

log_file_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_file_dir, exist_ok=True)

file_handler = RotatingFileHandler(
    filename=os.path.join(log_file_dir, 'server.log'),
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding='utf-8'
)

file_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
)

logger.addHandler(file_handler)


# 线程池
executor = ThreadPoolExecutor(max_workers=10)


# 运行时token
token_info = {
    'self': {
        'access_token': "",
        'token_expire_time': 0
    },
    'bot': {
        'access_token': "",
        'token_expire_time': 0
    },
}


# 提示信息
hint_message_dict = {
    # 下载媒体文件失败
    "download_no_media": "您发送的{content_type_name}好像有问题，请重试",
    # 上传媒体文件失败
    "upload_no_media": "很抱歉，帮您生成的{file_name}{media_type_name}发送失败",
    # 机器人无权限
    "bot_no_permission": "抱歉，您无权限访问此功能",
    # 位置信息用户提示词
    "location_prompt": "我现在所处的位置信息如下：纬度：{location_x}, 经度：{location_y}，地图缩放大小：{scale}，位置信息:{label}",
    # 媒体文件用户提示词
    "media_prompt": "这是一个附件类型请求，我这有一个{content_type_name}文件，它保存在：{media_path}，请你结合上下文分析这个{content_type_name}文件并回答，如果没有相关上下文，那么我就只是再给你分享这个{content_type_name}文件；注意：这是一个本地文件，{media_path}是一个本地路径，不是远程URL",
    # 微信临时素材大小限制
    "file_size_limit": "很抱歉，帮您生成的{file_name}{file_type}{limit}，微信不支持发送，请重新生成",
    # 不支持的消息类型
    "not_support_msg_type": "暂不支持处理{msg_type}类消息",
    # 冷却提示
    "cool_down": "上一个请求正在处理中，请一个一个来~"
}


# 消息类型描述
msg_type_dict = {
    "image": "图片",
    "video": "视频",
    "voice": "语音",
    "file": "文件"
}


# 文件类型映射消息类型
file_type_to_media_type_dict = {
    "jpg": "image",
    "png": "image",
    "mp4": "video",
    "amr": "voice",
    "bin": "file"
}


# 文件限制
file_size_limit = {
    "image": 10 * 1024 * 1024,
    "video": 10 * 1024 * 1024,
    "file": 20 * 1024 * 1024
}


# 支持接收的消息类型列表
supported_msg_types = ["text", "voice", "image", "video", "file", "location"]


# 用户请求状态
# user_id + bot_type 为key，value为字典，包含message、in_progress、update_time字段
# message为用户请求消息，in_progress为是否正在处理中，update_time为最近一次消息时间戳
# 单次消息请求时初始化或更新key和value，单次会话结束时删除key和value，确保同一用户同一bot同一时间只能进行一个会话
# 单次消息请求后的10秒内若收到后续消息，则认为是一次会话请求，拼接message字段，以此类推处理；若某次消息请求10秒内无后续消息请求，设置in_progress为True，开始处理这次会话所有message
# 若存在key，且单次会话在处理中，且最近一次消息时间戳小于当前时间15min内则拦截请求，否则允许请求
user_request_status = {}


# 被认为归属一次用户会话请求的时间间隔
user_one_request_interval = 10
