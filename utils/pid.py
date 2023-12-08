import os, sys,psutil


class PID(object):
    system = os.name
    if system == 'nt':
        pid_file = os.getenv('temp') + os.path.sep + "lsd_bot.pid"
    elif system == "posix":
        pid_file = '/tmp/lsd_bot.pid'
    else:
        pid_file = './lsd_bot.pid'
    
    def __init__(self) -> None:
        super(PID, self).__init__() 

    def check_launch(self, pid):
        if os.path.isfile(self.pid_file):
            with open(self.pid_file, 'r') as f:
                pidf = int(f.read())
                # print(pid, pidf, psutil.pid_exists(pidf))
                if pid != pidf and psutil.pid_exists(pidf):
                    print("Already running, exiting")
                    sys.exit()

        with open(self.pid_file, 'w') as f:
            f.write(str(pid))

    def unlink(self):
        os.unlink(self.pid_file)