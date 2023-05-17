# -*- coding: utf-8 -*-
import time
import signal
from subprocess import Popen

#在单独的进程中运行命令，并同时输出标准输出和标准错误
class SubProcessSrc(object):
    """Running the process in a separate thread
       and outputting the stdout and stderr simultaneously.
       result dict with status and proc. status = 1 means process not completed.
       status = 0 means process completed successfully.
       在单独的线程中运行进程，并同时输出stdout和stderr。结果字典包含状态和进程信息。状态=1表示进程未完成，状态=0表示进程已成功完成。
       cmd: 要执行的命令，可以是字符串或由多个字符串组成的列表。
       cwd: 执行命令的工作目录。
       shell: 是否使用 shell 来解释执行命令。
       timeout: 命令的最长执行时间，超时后将终止命令。
    """
    def __init__(self, cmd, cwd, shell=False, timeout=604800):
        self.cmd = cmd          #要执行的命令
        self.timeout = timeout  #命令超时时间，默认为 604800 秒（即 7 天
        self.proc = None        #子进程对象。默认值为 None，这意味着该对象尚未创建
        self.shell = shell  #是否在 shell 中运行命令。默认为 False，表示不在 shell 中运行
        self.revoked = False   #是否已撤销。默认为 False，表示未被撤销
        self.cwd = cwd      #执行命令时的工作目录

    #在新的子进程中运行命令，并在必要时检查和停止该进程
    def run(self):
        #SIGTERM 是由操作系统发送给进程以请求其正常终止的信号
        signal.signal(signal.SIGTERM, self.sigterm_hander)
        #调用 Popen 函数来创建一个新的子进程，并且将其保存在对象的 proc 属性中
        self.proc = Popen(self.cmd, shell=self.shell, cwd=self.cwd)

        is_timeout = True
        #使用一个循环来等待进程的完成或超时,循环迭代次数为 self.timeout，默认为 604800 秒（即 7 天）
        for i in range(self.timeout):
            #self.proc.poll() 用于检查子进程是否完成
            if self.proc.poll() is not None:
                is_timeout = False
                break
            # 每秒检查子进程是否已经完成。如果子进程完成或者超时，则退出循环
            time.sleep(1)
        #根据进程的状态码和是否被撤销，设置一个字典对象作为返回结果。
        # 如果被撤销，则状态码为-1；如果超时，则状态码为 1；如果完成，状态码为 0。
        result = {'proc': self.proc}

        if self.revoked:
            result['status'] = -1
        elif is_timeout: # Process not completed
            result['status'] = 1
        else:  # Process completed successfully.
            result['status'] = 0

        #会返回一个字典对象，其中包括进程对象和状态码
        return result

    #定义了一个 sigterm_hander() 方法，用于捕获 SIGTERM 信号并终止进程。
    def sigterm_hander(self, signum, frame):
        #self.proc是一个子进程对象
        self.proc.terminate()   #向子进程发送SIGTERM信号，以请求其优雅地关闭
        self.proc.wait()     #等待子进程终止并返回退出状态码
        self.revoked = True  #表示子进程已经被终止并且不能再被重新启动