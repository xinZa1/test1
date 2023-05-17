import time
import signal
from subprocess import Popen

#用于在Python中启动一个新进程，并等待它完成。同时，它还支持处理超时和程序被终止的情况。有以下功能
# 在单独的线程中运行进程；
# 同时输出标准输出和标准错误；
# 支持设置超时时间；
# 支持终止进程。
class SubProcessSrc(object):
    """Running the process in a separate thread
       and outputting the stdout and stderr simultaneously.
       result dict with status and proc. status = 1 means process not completed.
       status = 0 means process completed successfully.
       在单独的线程中运行进程，并同时输出stdout和stderr。结果字典包含状态和进程信息。状态为1表示进程未完成，状态为0表示进程成功完成。
    """

    #cmd表示要执行的命令，cwd表示要执行命令时所在的工作目录，shell表示是否使用Shell执行命令，timeout表示进程执行超时时间，默认为一周
    def __init__(self, cmd, cwd, shell=False, timeout=604800):
        self.cmd = cmd
        self.timeout = timeout
        self.proc = None
        self.shell = shell
        self.revoked = False
        self.cwd = cwd

    #启动进程并等待其完成，返回一个字典，其中包含两个键值对，proc表示subprocess.Popen对象，status表示进程的状态，
    # 0表示成功完成，1表示未完成，-1表示被终止。如果进程已经被终止，则返回相应的状态码，否则会等待进程完成，或者直到超时
    def run(self):
        #Python中用于注册信号处理函数的语句。它的作用是将self.sigterm_hander函数注册为进程接收到SIGTERM信号时的处理函数。
        #下面一条代码的作用是将self.sigterm_hander函数注册为进程接收到SIGTERM信号时的处理函数。
        #当进程接收到SIGTERM信号时，会自动调用self.sigterm_hander函数，并在其中执行相应的退出操作。
        signal.signal(signal.SIGTERM, self.sigterm_hander)
        #过 Popen 函数启动一个新的进程，将结果保存到proc属性中。
        self.proc = Popen(self.cmd, shell=self.shell, cwd=self.cwd)

        is_timeout = True
        #在一个循环中检查进程是否已经结束
        for i in range(self.timeout):
            if self.proc.poll() is not None:
                is_timeout = False
                break
            time.sleep(1)

        result = {'proc': self.proc}

        if self.revoked:
            #self.revoked = True 表示进程被终止
            result['status'] = -1
        #status设置为1表示进程未完成。
        elif is_timeout: # Process not completed
            result['status'] = 1
        else:  # Process completed successfully.
            result['status'] = 0
        #在返回的字典中，将proc和status保存起来并返回。
        return result

    #信号处理函数，用于接收SIGTERM信号并终止进程
    #当调用sigterm_hander方法时，会将self.revoked属性设为True，并使用terminate()函数终止进程。
    # 在终止进程后，调用wait()函数等待进程结束，并将self.revoked属性设置为True，以便在run()方法中得到相应的状态码。
    def sigterm_hander(self, signum, frame):
        self.proc.terminate()
        self.proc.wait()
        self.revoked = True   #表示进程是否被终止的标志位

