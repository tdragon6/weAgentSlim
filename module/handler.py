'''
    入口文件
'''


from config import tencent_cloud
from universe import root_dir, logger, hint_message_dict, msg_type_dict, user_request_limit
from module.task import get_agent_result, judge_media_file_size, voice_to_text
from module.wechat import send_reply_message, download_wechat_media, upload_wechat_media
import os
import shutil
import time
import traceback


def agent_task_handler(user_id, msg, bot_type):
    '''
        agent任务入口函数
    '''
    try:
        # 设置用户请求状态
        user_request_limit[user_id + '_' + bot_type] = time.time()

        message = ""
        
        # 处理text类型消息
        if msg.type == "text":
            message = msg.content
        
        # 处理location类型消息
        if msg.type == "location":
            message = hint_message_dict["location_prompt"].format(location_x=msg.location_x, location_y=msg.location_y, scale=msg.scale, label=msg.label)

        # 处理media类型消息
        if msg.type in ["voice", "image", "video", "file"]:
            media_id = msg.media_id if hasattr(msg, "media_id") else None
            # 检查media_id是否存在
            if not media_id:
                send_reply_message(user_id, hint_message_dict["download_no_media"].format(content_type_name=msg_type_dict[msg.type]), "text", bot_type)
                logger.info(f"No Media ID Received: user_id={user_id}, bot_type={bot_type}, msg_type={msg.type}")
                return
            
            # 处理voice类型消息
            if msg.type == "voice":
                voice_file = download_wechat_media(media_id, '/tmp', bot_type)
                if voice_file == "":
                    send_reply_message(user_id, hint_message_dict["download_no_media"].format(content_type_name=msg_type_dict[msg.type]), "text", bot_type)
                    logger.info(f"Voice Download Failed: user_id={user_id}, bot_type={bot_type}, msg_type={msg.type}, media_id={media_id}")
                    return
                
                message = voice_to_text(tencent_cloud["SECRET_ID"], tencent_cloud["SECRET_KEY"], voice_file)
                if message == "":
                    send_reply_message(user_id, hint_message_dict["download_no_media"].format(content_type_name=msg_type_dict[msg.type]), "text", bot_type)
                    logger.info(f"Voice To Text Failed: user_id={user_id}, bot_type={bot_type}, msg_type={msg.type}, media_id={media_id}")
                    return

            # 处理其他image、video、file类型消息，下载media文件
            else:
                save_dir = os.path.join(root_dir, "current_inputs", bot_type, user_id)
                os.makedirs(save_dir, exist_ok=True)
                save_path = download_wechat_media(media_id, save_dir, bot_type)

                # 判断下载是否成功
                if save_path != "":
                    message = hint_message_dict["media_prompt"].format(content_type_name=msg_type_dict[msg.type], media_path='/root/workspace/current_inputs/' + save_path.split('/')[-1])
                else:
                    send_reply_message(user_id, hint_message_dict["download_no_media"].format(content_type_name=msg_type_dict[msg.type]), "text", bot_type)
                    logger.info(f"Media Download Failed: user_id={user_id}, bot_type={bot_type}, msg_type={msg.type}, media_id={media_id}")
                    return
        
        # 执行agent并获取结果
        agent_result = get_agent_result(user_id, message, bot_type)

        # 发送text结果
        text = agent_result["text"]
        if text != "":
            send_reply_message(user_id, text, "text", bot_type)
            logger.info(f"Sent Text Message: user_id={user_id}, bot_type={bot_type}, content={text}")
        
        # 处理media结果
        media_path_list = agent_result["media_path_list"]
        if media_path_list != []:
            # 获取文件大小限制判断结果
            media_judge_result = judge_media_file_size(media_path_list)
            for ele in media_judge_result:
                # 满足文件大小限制
                if ele["is_legal"]:
                    media_id = upload_wechat_media(bot_type, ele["media_type"], ele["file_path"])
                    if media_id != '':
                        # 发送media结果
                        send_reply_message(user_id, media_id, ele["media_type"], bot_type)
                        logger.info(f"Sent Media Message: user_id={user_id}, bot_type={bot_type}, file_path={ele['file_path']}, media_id={ele['media_id']}, media_type={ele['media_type']}")
                    else:
                        send_reply_message(user_id, hint_message_dict["upload_no_media"].format(file_name=ele['file_path'].split("/")[-1], media_type_name=msg_type_dict[ele['media_type']]), 'text', bot_type)
                        logger.info(f"Upload Media Failed: user_id={user_id}, bot_type={bot_type}, file_path={ele['file_path']}, media_type={ele['media_type']}")
                # 不满足文件大小限制
                if not ele["is_legal"]:
                    send_reply_message(user_id, ele["message"], "text", bot_type)
                    logger.info(f"Send File Size Error: user_id={user_id}, bot_type={bot_type}, file_size={ele['file_size']}, file_path={ele['file_path']}, media_type={ele['media_type']}")
            
        
        # 本次会话处理结束后，将输入的media文件复制到inputs目录下
        if 'save_path' in locals() and save_path != "":
            shutil.copy2(save_path, f'{root_dir}/inputs/{bot_type}/{user_id}/{save_path.split("/")[-1]}')
    except:
        logger.error(traceback.format_exc())
    finally:
        # 本次会话处理结束，删除用户请求状态
        del user_request_limit[user_id + '_' + bot_type]
