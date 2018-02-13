from errbot import BotPlugin, botcmd
import subprocess, tempfile, re, time

class AutoSysJob(BotPlugin):
    """AutoSys job plugin for Errbot"""

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
            output = "Error connecting..."
        return output
    
    @botcmd
    def job_status(self, msg, args):
        """Return job status"""
        job_name = args
        error = ""
        
        target_server = self.get_plugin('AutoSysServer').target_server
        if target_server == "":
            error = "Target server not set. Set the target server using !server target (servername)."

        if error == "":
            command = "AutoSysJob " + job_name
            result = str(self.ssh(msg, command))  
            if result.find("Job Name:") == -1:
                error = "Cannot connect to targeted server with your user."
        
        if error:
            return error
        else:
            result_array = result.split("'")[1].split("\\n")
            for r in result_array:
                yield r
        
        ###################################################################
        #with open('/var/errbot/target_server', 'r') as file:
        #    target_server = str(file.read())
        #string = "Server:  \t\t" + target_server 
        #string += "\nJob Name:  \t" + job_name
        #string += "\nLast Start: \t" + "01/08/2018 22:35:03"
        #string += "\nLast End: \t\t" + "01/08/2018 22:35:52"
        #string += "\nStatus: \t\t" + "Success"
        #return string
    
    # This method would attempt to loggin to the server listed in /var/errbot/target_server
    # then after logging in, source into P11 instance by executing . /export/apps/sched/autouser/autosys.bash.P11
    # finally continue trying to start start the job
    # optionally, the method could be configured to continually poll the job for X time looking for a SU status.
    @botcmd
    def job_start(self, msg, args):
        """Start requested job"""
        error = ""
        job_name = args
        
        target_server = self.get_plugin('AutoSysServer').target_server
        if target_server == "":
            error = "Target server not set. Set the target server using !server target (servername)."
            
        if error == "":
            command = "AutoSysJob " + job_name + " --rerun"
            yield "Starting " + job_name + " on " + target_server + "..."
            time.sleep(3)
            result = str(self.ssh(msg, command))
            if result.find("Job Name:") == -1:
                error = "Cannot connect to targeted server with your user."
        
        if error:
            return error
        else:
            result_array = result.split("'")[1].split("\\n")
            for r in result_array:
                yield r
                
        #job_name = args
        #target_server = self.get_plugin('AutoSysServer').target_server
        #with open('/var/errbot/target_server', 'r') as file:
        #    target_server = str(file.read())
        #login
        #source file
        #poll for RU status
        #yield job_name + " has started."
        #string = "Server:  \t\t" + target_server 
        #string += "\nJob Name:  \t" + job_name
        #string += "\nLast Start: \t" + "01/08/2018 21:35:03"
        #string += "\nLast End: \t\t" + "01/08/2018 21:35:52"
        #string += "\nStatus: \t\t" + "Running"
        #yield string
        #optionally poll for SU status
