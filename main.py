'''
    主程序入口
'''


from config import wechat_config, uri_bot_type_dict
from universe import executor, logger, hint_message_dict, supported_msg_types, user_request_limit
from module.utils import start_clean
from module.handler import agent_task_handler
from module.wechat import send_reply_message
from flask import Flask, request
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.enterprise import parse_message
import time
import traceback


app = Flask(__name__)


@app.route(list(uri_bot_type_dict.keys())[0], methods=["GET", "POST"])
@app.route(list(uri_bot_type_dict.keys())[1], methods=["GET", "POST"])
def wechat_callback():
    '''
        微信回调接口
    '''
    bot_type = uri_bot_type_dict[request.path]

    msg_signature = request.args.get("msg_signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")

    crypto = WeChatCrypto(
        wechat_config["TOKEN"][bot_type],
        wechat_config["ENCODING_AES_KEY"][bot_type],
        wechat_config["CORP_ID"]
    )

    if request.method == "GET":
        try:
            echostr = request.args.get("echostr")
            echo_str = crypto.check_signature(msg_signature, timestamp, nonce, echostr)
            return echo_str
        except:
            return "签名验证失败", 403

    else:
        try:
            decrypted_msg = crypto.decrypt_message(
                request.data, msg_signature, timestamp, nonce
            )
            msg = parse_message(decrypted_msg)
            logger.info(f"Received Message: {msg}, bot_type={bot_type}")

            user_id = msg.source

            # 检查用户请求是否在冷却中
            if user_id + '_' + bot_type in user_request_limit.keys() and time.time() - user_request_limit[user_id + '_' + bot_type] < 15 * 60:
                executor.submit(send_reply_message, user_id, hint_message_dict['cool_down'], "text", bot_type)
                logger.info(f"Message Handle Cool Down: user_id={user_id}, bot_type={bot_type}")
                return "success"

            # 清理本次会话输入输出目录，删除历史冗余信息
            start_clean(user_id, bot_type)
            
            # 支持的类型消息处理
            if msg.type in supported_msg_types:
                executor.submit(agent_task_handler, user_id, msg, bot_type)
            # 不支持的类型消息处理
            else:
                executor.submit(send_reply_message, user_id, f"{hint_message_dict['not_support_msg_type'].format(msg_type=msg.type)}", "text", bot_type)
                logger.info(f"Message Type Not Support: user_id={user_id}, bot_type={bot_type}, msg_type={msg.type}")
            return "success"
        except:
            logger.error(traceback.format_exc())
            return "success"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)