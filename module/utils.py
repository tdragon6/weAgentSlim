'''
    通用工具文件
'''


from universe import root_dir
import os
import shutil
import secrets
import string


def generate_secure_random_letters(length):
    '''
        生成随机字符串
    '''
    letters = string.ascii_letters
    return ''.join(secrets.choice(letters) for _ in range(length))


def recursive_delete_except(root_dir, except_list):
    '''
        递归删除目录下的所有文件和子目录，除了except_list中的文件和目录
    '''
    root_dir = os.path.abspath(root_dir)
    if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
        return
    
    for root, dirs, files in os.walk(root_dir, topdown=False):
        for file_name in files:
            if file_name not in except_list:
                file_path = os.path.join(root, file_name)
                try:
                    os.remove(file_path)
                except:
                    pass
        
        for dir_name in dirs:
            if dir_name not in except_list:
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)
                except:
                    pass


def user_data_clean(user_id, bot_type):
    '''
        清理用户临时数据
    '''
    try:
        shutil.rmtree(os.path.join(root_dir, f"current_inputs/{bot_type}/{user_id}"))
    except:
        pass
    
    try:
        shutil.rmtree(os.path.join(root_dir, f"current_outputs/{bot_type}/{user_id}"))
    except:
        pass
    
    recursive_delete_except(os.path.join(root_dir, f"storage/{bot_type}/{user_id}"), ["opencode.db", "opencode.db-shm", "opencode.db-wal", "share", "opencode"])


def get_file_type(file_path):
    '''
        获取文件类型
    '''
    if not os.path.exists(file_path):
        return ""
    
    if not os.path.isfile(file_path):
        return ""
    
    with open(file_path, 'rb') as f:
        header = f.read(16)
    
    if header.startswith(b'\xFF\xD8\xFF'):
        return 'jpg'
    elif header.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'):
        return 'png'
    elif b'ftypmp4' in header[:12] or b'ftypiso' in header[:12] or b'ftypM4V' in header[:12]:
        return 'mp4'
    elif header.startswith(b'#!AMR\n') or header.startswith(b'#!AMR-WB\n'):
        return 'amr'
    else:
        return 'bin'
