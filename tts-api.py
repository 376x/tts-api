# -*- coding: utf-8 -*-
import requests
import os
import pandas as pd
import time
import subprocess
import signal
import atexit
import configparser
import re

config_name = []
process = []


@atexit.register
def exit_handler():
    process.terminate()


def send_api_request(api_url, inference_data, output_path):
    response = requests.post(api_url, json=inference_data)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"音频已保存为 {output_path}")
    else:
        print(f"Error: {response.status_code}")
        print(f"Message: {response.text}")


def keep_chinese(text):
    pattern = r'[^\u4e00-\u9fa5]'
    chinese_text = re.sub(pattern, '', text)
    return chinese_text


def clean_filename(filename):
    # 替换掉Windows文件名中不允许的字符
    return re.sub(r'[\<\>:"/\\|?*]', '', filename)


# 读取Excel文件
df = pd.read_excel('./tts_api/视频-小屋代理精品视频文案洗稿_2024.xlsx')

# 在启动完成后更新配置文件
config = configparser.ConfigParser()
config.read('./tts_api/config.ini')

section = 'section_name'  # 配置文件中的节名
option = 'option_name'  # 要修改的选项名
value = '0'  # 要写入的数值

config.set(section, option, value)

with open('./tts_api/config.ini', 'w') as configfile:
    config.write(configfile)
print(config.sections())
# 遍历每一行数据
for index, row in df.iterrows():
    # title = row['二级标题']
    name = row['视频标题（洗稿）']
    text = row['视频内容文案（洗稿）']
    top = row['序号']
    people_name = row['代理商形象（凤仙填）']
    if config_name != people_name:
        print(people_name)
        print(config_name)
        if process:
            os.kill(process.pid, signal.SIGTERM)
        config = configparser.ConfigParser()

        # wav_file = "./tts_api/GPT参考音频/周婧参考.wav"
        # text_content = "结婚、事业成功，成为人生赢家。这些对他们来说"
        # sovits_path = "./tts_api/SoVITS_weights/周婧_e8_s80.pth"
        # gpt_path = "./tts_api/GPT_weights/周婧-e15.ckpt"

        tts_section = keep_chinese(people_name)  # 配置文件中的节名
        wav_option = 'wav_file'
        text_option = 'text_content'
        sovits_option = 'sovits_path'
        gpt_option = 'gpt_path'

        config.read('./tts_api/config.ini')

        # 检查section是否存在
        if config.has_section(tts_section):
            # 如果存在，读取相关option
            sovits_path = config.get(tts_section, sovits_option).strip('"')
            gpt_path = config.get(tts_section, gpt_option).strip('"')
            text_content = config.get(tts_section, text_option).strip('"')
            wav_file = config.get(tts_section, wav_option).strip('"')

            process = subprocess.Popen(['python', 'api.py', '-s', sovits_path, '-g', gpt_path, '-dr', wav_file, '-dt', text_content, '-dl', "中文"])

            # 创建一个ConfigParser对象并读取配置文件
            section = 'section_name'  # 配置文件中的节名
            option = 'option_name'  # 要读取的选项名

            for _ in range(60):
                config.read('./tts_api/config.ini')
                value = config.get(section, option)
                print(f"The value of {option} in section {section} is: {value}")
                time.sleep(2)
                if value == '1':
                    section = 'section_name'  # 配置文件中的节名
                    option = 'option_name'  # 要修改的选项名
                    value = '0'  # 要写入的数值

                    config.set(section, option, value)

                    with open('./tts_api/config.ini', 'w') as configfile:
                        config.write(configfile)
                    break
        else:
            # 如果不存在，输出提示信息
            print(f"没有此模型: {tts_section}")
            continue

    config_name = people_name
    inference_data = {
        "text": text,
        "text_language": "中文"
    }
    API_URL = "http://192.168.70.152:9880"
    # 假设your_path为您的路径
    your_path = "./tts_api/output"
    # 拼接name和路径生成OUTPUT_PATH
    f_name = str(top) + '_' + name + '_' + people_name
    g_name = clean_filename(f_name)
    OUTPUT_PATH = os.path.join(your_path, g_name) + ".wav"

    send_api_request(API_URL, inference_data, OUTPUT_PATH)
