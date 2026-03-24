'''
    企业微信相关处理文件
'''


from config import wechat_config, wechat_proxies
from universe import logger
from module.utils import get_file_type, generate_secure_random_letters
from universe import token_info
import requests
import time
import os
import traceback


def get_access_token(bot_type):
    '''
        获取企业微信access_token
    '''
    global token_info

    if token_info[bot_type]['access_token'] and time.time() < token_info[bot_type]['token_expire_time']:
        return token_info[bot_type]['access_token']
    
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={wechat_config['CORP_ID']}&corpsecret={wechat_config['SECRET'][bot_type]}"
    try:
        resp = requests.get(url, timeout=10)
        resp_data = resp.json()
        if resp_data.get("errcode") == 0:
            token_info[bot_type]['access_token'] = resp_data["access_token"]
            token_info[bot_type]['token_expire_time'] = time.time() + resp_data["expires_in"] - 60
            return token_info[bot_type]['access_token']
        else:
            return None
    except:
        return None


def send_reply_message(to_user, content, content_type, bot_type):
    '''
        发送企业微信回复消息
    '''
    token = get_access_token(bot_type)
    if not token:
        return False

    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    data = {
        "touser": to_user,
        "msgtype": content_type,
        "agentid": wechat_config["AGENT_ID"][bot_type],
        content_type: {
            "content" if content_type == "text" else "media_id": content
        }
    }

    try:
        resp = requests.post(url, json=data, timeout=10, proxies=wechat_proxies)
        resp_data = resp.json()
        logger.info(f"Raw Send Message: {resp_data}")
        if resp_data.get("errcode") == 0:
            return True
        else:
            return False
    except:
        logger.error(traceback.format_exc())
        return False


def download_wechat_media(media_id, save_dir, bot_type):
    '''
        下载企业微信媒体文件
    '''
    token = get_access_token(bot_type)
    if not token:
        return ""
    
    download_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token={token}&media_id={media_id}"
    
    try:
        resp = requests.get(download_url, stream=True, timeout=600, proxies=wechat_proxies)
        if resp.status_code != 200:
            return ""
        
        filename = generate_secure_random_letters(16)

        save_path = os.path.join(save_dir, filename)
        
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        
        file_type = get_file_type(save_path)
        
        new_save_path = save_path + '.' + file_type

        os.rename(save_path, new_save_path)

        return new_save_path
    
    except:
        logger.error(traceback.format_exc())
        return ""


def upload_wechat_media(bot_type, media_type, media_path):
    '''
        上传企业微信媒体文件
    '''
    if not os.path.exists(media_path):
        return ""

    token = get_access_token(bot_type)
    if not token:
        return ""

    upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type={media_type}"

    try:
        with open(media_path, 'rb') as f:
            files = {'media': f}
            resp = requests.post(upload_url, files=files, timeout=600, proxies=wechat_proxies)

        if resp.status_code != 200:
            return ""
        
        resp = resp.json()

        if resp.get("errcode") != 0:
            return ""

        media_id = resp.get("media_id")
        if len(media_id) > 128:
            return ""
        return media_id
    
    except:
        logger.error(traceback.format_exc())
        return ""