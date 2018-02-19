from errbot import BotPlugin, botcmd
import subprocess, tempfile, re, time

class AutoSysJob(BotPlugin):
    """AutoSys job plugin for Errbot"""
    
    error = ""
    
    def ssh(self, msg, command):
        user_array = str(msg.frm).split("@")
        username = user_array[0]
        gpg_string = "/root/.password-store/" + username + ".gpg"
        proc = subprocess.Popen(["echo $ERRBOT_PASS"], shell=True, stdout=subprocess.PIPE)
        outs, errs = proc.communicate()
        errbot_pass = str(outs).split("'")[1].split("\\")[0]
        user_pass_temp = subprocess.check_output(["gpg2", "--batch", "--passphrase", errbot_pass, "-a", "-d", gpg_string])
        user_pass = str(user_pass_temp).split("'")[1].split("\\")[0]
        user_server = username + "@" + self.get_plugin('AutoSysServer').target_server
        try:
            output = subprocess.check_output(["sshpass", "-p", user_pass, "ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", user_server, command])
        except:
            self.error = self.error + "Error connecting... "
        return output
    
    @botcmd
    def job_status(self, msg, args):
        """Return job status"""
        job_name = args
        
        target_server = self.get_plugin('AutoSysServer').target_server
        if target_server == "":
            self.error = self.error + "Target server not set. Set the target server using !server target (servername). "

        if self.error == "":
            command = "AutoSysJob " + job_name
            result = str(self.ssh(msg, command))  
            if result.find("Job Name:") == -1:
                self.error = self.error + "Cannot connect to targeted server with your user. "
        
        if self.error != "":
            return self.error
        else:
            result_array = result.split("'")[1].split("\\n")
            for r in result_array:
                yield r
        
    @botcmd
    def job_start(self, msg, args):
        """Start requested job"""
        job_name = args
        
        target_server = self.get_plugin('AutoSysServer').target_server
        if target_server == "":
            self.error = self.error + "Target server not set. Set the target server using !server target (servername). "
            
        if self.error == "":
            command = "AutoSysJob " + job_name + " --rerun"
            yield "Starting " + job_name + " on " + target_server + "..."
            time.sleep(3)
            result = str(self.ssh(msg, command))
            if result.find("Job Name:") == -1:
                self.error = self.error + "Cannot connect to targeted server with your user. "
        
        if self.error != "":
            return self.error
        else:
            result_array = result.split("'")[1].split("\\n")
            for r in result_array:
                yield r
