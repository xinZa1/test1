#!/usr/bin/env python
# -*- coding: utf-8 -*-
#基于分布式消息传递的异步任务队列系统
from celery import Celery
import os
from time import time
import json
#from process import SubProcessSrc
#该类封装了执行外部进程的相关方法
from process import SubProcessSrc

#基于Celery的异步任务，用于在后台运行子域名枚举工具Subfinder，并将结果以JSON格式返回

#获取当前脚本文件的绝对路径，并将其拆分为路径名和文件名两个部分，最后将路径名赋值给变量FILEPATH
FILEPATH = os.path.split(os.path.realpath(__file__))[0]

#如果环境变量DEBUG为False，则从系统环境变量中获取broker和backend的值
if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'False':
    broker = os.environ['BROKER']
    backend = os.environ['BACKEND']
    DEBUG = "False"
else:
    DEBUG = "True"
    broker = 'amqp://guest:guest@127.0.0.1:5672/H_broker'
    backend = 'amqp://guest:guest@127.0.0.1:5672/H_backend'

app = Celery('H.subfinder', broker=broker, backend=backend, )
#从配置模块config中读取配置信息，并将其应用到app对象。
app.config_from_object('config')

@app.task
#接收一个domain参数表示要进行子域名枚举的域名
def run(domain):
    work_dir = FILEPATH + '/tools'
    out_file_name = '{}_{}.json'.format(domain, time())
    # 执行命令 ./subfinder_mac -d example.com -json -o
    if DEBUG == 'True':
        command = ['./subfinder_mac', '-d', domain, '-json', '-config', 'config.yaml', '-o', out_file_name]
    else:
        command = ['./subfinder', '-d', domain, '-json', '-config', 'config.yaml', '-all', '-o', out_file_name]
    sb = SubProcessSrc(command, cwd=work_dir).run()
    result = []
    if sb['status'] == 0:
        # 运行成功，读取json数据返回
        with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
            subdomains = f.readlines()
            for line in subdomains:
                if('\\n' in json.loads(line)['host']):
                    continue
                else:
                    result.append(json.loads(line)['host'])
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
        return {'tool': 'subfinder', 'result': result}

if __name__ == '__main__':
    print(run('vivo.com'))

#如果想要执行该任务，则需要启动一个Celery worker进程来接收并处理任务。
# celery -A 文件名 worker --loglevel=info
# 在终端中执行以上命令即可启动Celery worker，其中-A参数指定要加载的Celery应用程序，worker表示要启动的进程类型，--loglevel=info表示设置日志输出级别为INFO。