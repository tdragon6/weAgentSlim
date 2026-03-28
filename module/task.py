'''
    agent业务逻辑文件
'''


from universe import root_dir, logger, hint_message_dict, msg_type_dict, file_type_to_media_type_dict, file_size_limit
from module.opencode import get_opencode_args, run_opencode, get_opencode_result
from module.utils import get_file_type
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.asr.v20190614 import asr_client, models
import os
import json
import base64
import traceback


def get_agent_result(user_id, message, bot_type):
    '''
        获取agent的执行结果
    '''
    # 获取opencode执行结果
    network, prompt_args, skills_args, storage_args, assets_args, time_args, config_args, env_args, model, message = get_opencode_args(user_id, message, bot_type)
    process = run_opencode(network, prompt_args, skills_args, storage_args, assets_args, time_args, config_args, env_args, model, message)
    opencode_result = get_opencode_result(process)

    result = {
        "text": "",
        "media_path_list": []
    }

    # 构建模型输出消息
    result["text"] = opencode_result
    
    # 构建media路径列表
    current_outputs_dir = f'{root_dir}/current_outputs/{bot_type}/{user_id}'
    for dir_path, _, file_names in os.walk(current_outputs_dir):
        for file_name in file_names:
            full_file_path = os.path.join(dir_path, file_name)
            result["media_path_list"].append(full_file_path)
    
    return result


def judge_media_file_size(media_path_list):
    '''
        判断media文件是否满足大小限制
    '''
    result = []
    for file_path in media_path_list:
        metainfo = {
            "is_legal": True,
            "file_path": file_path,
            "file_size": 0,
            "media_type": "",
            "message": ""
        }

        file_size = os.path.getsize(file_path)
        metainfo["file_size"] = file_size

        # 微信要求所有文件必须大于5B
        if file_size <= 5:
            metainfo["message"] = hint_message_dict["file_size_limit"].format(file_name=file_path.split("/")[-1], file_type="文件", limit='<=5字节')
            metainfo["is_legal"] = False
            result.append(metainfo)
            continue

        # 获取文件类型和media类型
        file_type = get_file_type(file_path)
        media_type = file_type_to_media_type_dict[file_type]
        metainfo["media_type"] = media_type

        # 确保各类型文件大小限制满足微信要求
        if file_size >= file_size_limit[media_type]:
            metainfo["message"] = hint_message_dict["file_size_limit"].format(file_name=file_path.split("/")[-1], file_type=msg_type_dict[media_type], limit=f'>={file_size_limit[media_type] / 1024 / 1024}MB')
            metainfo["is_legal"] = False
            result.append(metainfo)
            continue
        
        result.append(metainfo)

    return result


def voice_to_text(secret_id, secret_key, voice_file):
    '''
        语音识别
    '''
    try:
        with open(voice_file, "rb") as f:
            audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile(endpoint="asr.tencentcloudapi.com")
        client = asr_client.AsrClient(cred, "ap-shanghai", ClientProfile(httpProfile=http_profile))

        req = models.SentenceRecognitionRequest()
        req.from_json_string(
            json.dumps(
                {
                    "EngSerViceType": "8k_zh",
                    "VoiceFormat": "amr",
                    "SourceType": 1,
                    "Data": audio_base64
                }
            )
        )

        return client.SentenceRecognition(req).Result.strip()
    except:
        logger.error(traceback.format_exc())
        return ""
    finally:
        try:
            os.remove(voice_file)
        except:
            pass
