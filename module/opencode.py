'''
    opencode相关处理文件
'''


from config import self_user_id_dict, rule_files_list_dict, skills_dict, model_dict
from universe import root_dir, logger, hint_message_dict
import os
import subprocess
import json
import re


def get_opencode_args(user_id, message, bot_type):
    '''
        构造opencode命令参数
    '''
    prompt_files = rule_files_list_dict["shared"] + rule_files_list_dict[bot_type]
    network = 'bridge' 

    # 环境变量参数
    env_args = [
        '-e', 'OPENCODE_DISABLE_AUTOUPDATE=true',
        '-e', 'OPENCODE_AUTO_SHARE=false'
    ]
    
    if bot_type == "self":
        if user_id not in self_user_id_dict.keys():
            return hint_message_dict["bot_no_permission"]

        user_file = f'USER_{self_user_id_dict[user_id]}.md'
        prompt_files += [user_file]
        env_args += ['-e', 'OPENCODE_DISABLE_MODELS_FETCH=true']
        network = 'no-internet'

    # 规则文件卷映射参数
    prompt_args = []
    for file in prompt_files:
        prompt_args.append('-v')
        prompt_args.append(f'{os.path.join(root_dir, "prompt", bot_type, file)}:/root/workspace/{file.split("_")[0].split(".")[0] + ".md"}:ro')
        
    # 技能卷映射参数
    skills_args = []
    for skill in skills_dict["shared"] + skills_dict[bot_type]:
        skills_args.append('-v')
        skills_args.append(f'{root_dir}/skills/{skill}:/root/workspace/.opencode/skills/{skill}:ro')

    # 会话存储卷映射参数
    storage_args = ['-v', f'{root_dir}/storage/{bot_type}/{user_id}:/root/.local']

    # 附件和运行时文件卷映射参数
    assets_args = [
        '-v', f'{root_dir}/inputs/{bot_type}/{user_id}:/root/workspace/inputs:ro',
        '-v', f'{root_dir}/current_inputs/{bot_type}/{user_id}:/root/workspace/current_inputs:ro',
        '-v', f'{root_dir}/outputs/{bot_type}/{user_id}:/root/workspace/outputs',
        '-v', f'{root_dir}/current_outputs/{bot_type}/{user_id}:/root/workspace/current_outputs'
    ]

    # 配置文件卷映射参数
    config_args = ['-v', f'{root_dir}/opencode.json:/root/workspace/.opencode/opencode.json:ro']

    return network, prompt_args, skills_args, storage_args, assets_args, config_args, env_args, model_dict[bot_type], message


def run_opencode(network, prompt_args, skills_args, storage_args, assets_args, config_args, env_args, model, message):
    '''
        运行opencode，返回结果
    '''
    command = [
        'docker', 'run', '--rm', '--network', network
    ] + prompt_args + skills_args + storage_args + assets_args + config_args + env_args + [
        'tdragon6/opencode:latest', 'run', message,
        '-c', '-m', model,
        '--dir', '/root/workspace',
        '--format', 'json'
    ]
    logger.info(f"Opencode Command: {' '.join(command)}")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        bufsize=1,
        text=True
    )

    return process


def get_opencode_result(process):
    '''
        获取opencode的结果
    '''
    result = {}
    for line in process.stdout:
        logger.info(f"Opencode Stream Output: {line.strip()}")
        try:
            line = json.loads(line.strip())
        except:
            continue
        message_type = line.get('type', '')
        if message_type == 'text':
            result = line
        if message_type == 'step_finish':
            if line.get('part', {}).get('reason', '') == 'stop':
                result = result.get('part', {}).get('text', '')
                pattern = re.compile(r"<think>.*?</think>", re.DOTALL)
                result = pattern.sub("", result)
                if 'think>' in result:
                    pattern = re.compile(r"^.*?/think>", re.DOTALL)
                    result = pattern.sub("", result)
                return result.strip()
            else:
                result = {}
    
    return ''
