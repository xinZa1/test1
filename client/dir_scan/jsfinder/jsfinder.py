#!/usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery
import os
from time import time
import json

from process import SubProcessSrc
from urllib.parse import urlparse   #urllib.parse: 用于解析URL
#在指定网站中查找JavaScript文件，并获取JavaScript文件对应的URL、状态码、标题等信息


FILEPATH = os.path.split(os.path.realpath(__file__))[0]     #获取当前运行脚本文件的绝对路径

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'False':
    broker = os.environ['BROKER']
    backend = os.environ['BACKEND']
    DEBUG = "False"
else:
    DEBUG = "True"
    broker = 'amqp://guest:guest@127.0.0.1:5672/H_broker'
    backend = 'amqp://guest:guest@127.0.0.1:5672/H_backend'

app = Celery('H.jsfinder', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(target):

    work_dir = FILEPATH + '/tools'
    out_file_name = 'jsfinder_{}.txt'.format(time())
    out_file_name2 = 'httpx_{}.txt'.format(time())


    # 执行命令
    if DEBUG == 'True':
        command = ['python3', 'JSFinder.py', '-u', target, '-ou', out_file_name]
        command2 = ['./httpx_mac', '-l', out_file_name, '-follow-host-redirects' , '-json', '-o', out_file_name2]
    else:
        command = ['python3', 'JSFinder.py', '-u', target, '-ou', out_file_name]
        #获取相关信息
        command2 = ['./httpx', '-l', out_file_name, '-follow-host-redirects' , '-json', '-o', out_file_name2]
    result = []
    #读取命令输出文件，提取JavaScript文件对应的URL、状态码、标题等信息
    result = tool(command, command2, work_dir, out_file_name2, target)
    try:
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name2))
    except:
        pass
    return {'tool': 'jsfinder', 'result': result}

def tool(command, command2, work_dir, out_file_name, target):
    result = []
    sb = SubProcessSrc(command, cwd=work_dir).run()
    if sb['status'] == 0:      
        # 运行成功，读取数据
        sb = SubProcessSrc(command2, cwd=work_dir).run()
        if sb['status'] == 0:
            try:
                with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        flag = False
                        for qc in result:
                            if (json.loads(line)['path'] == qc['path']):
                                flag = True
                                break
                        if(target.split("://")[1] in json.loads(line)['url'] and flag == False and json.loads(line)['status-code'] in [200,500,403,503] and 'javascript' not in json.loads(line)['content-type'] and 'image' not in json.loads(line)['content-type']): 
                            dic={"host":"", "path":"", "content-length":"", "title":"", "status-code":""}
                            try:
                                url = json.loads(line)['url']
                                urlres = urlparse(url)
                                dic["host"] = urlres.scheme + "://" + urlres.netloc
                                dic["path"] = urlres.path
                                dic["content-length"] = json.loads(line)['content-length']
                                dic["title"] = json.loads(line)['title']
                                dic["status-code"] = json.loads(line)['status-code']
                                result.append(dic)
                            except:
                                url = json.loads(line)['url']
                                urlres = urlparse(url)
                                dic["host"] = urlres.scheme + "://" + urlres.netloc
                                dic["path"] = urlres.path
                                dic["content-length"] = ""
                                dic["title"] = ""
                                dic["status-code"] = json.loads(line)['status-code']
                                result.append(dic)
            except:
                pass
    return result

if __name__ == '__main__':
    target = 'https://wlmkids.com:443'
    print(run(target))
