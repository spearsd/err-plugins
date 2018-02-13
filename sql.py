from errbot import BotPlugin, botcmd
import subprocess, tempfile, re, time

class SQLPlugin(BotPlugin):
    """SQL plugin for Errbot"""
    
    user = ""
    passwd = ""
    server = ""
    
    def set_variables(self, msg, args):
        user_array = str(msg.frm).split("@")
        username = user_array[0]
        gpg_string = "/root/.password-store/" + username + ".gpg"
        proc = subprocess.Popen(["echo $ERRBOT_PASS"], shell=True, stdout=subprocess.PIPE)
        outs, errs = proc.communicate()
        errbot_pass = str(outs).split("'")[1].split("\\")[0]
        user_pass_temp = subprocess.check_output(["gpg2", "--batch", "--passphrase", errbot_pass, "-a", "-d", gpg_string])
        user_pass = str(user_pass_temp).split("'")[1].split("\\")[0]
        user_server = username + "@" + self.get_plugin('AutoSysServer').target_server
        self.user = username
        self.passwd = "-p"+user_pass
        self.server = self.get_plugin('AutoSysServer').target_server
        
    
    @botcmd
    def select(self, msg, args):
        """Return job status"""
        yield "Following args given: " + args
        what_to_select = args[0]
        table = args[1]
        query = "SELECT "+ what_to_select + " FROM " + table
        error = ""
        
        self.set_variables(self, msg, args)
        output = subprocess.check_output(["mysql", "-u", self.user, self.passwd, "-h", self.server, "-e", query])

        output_array = output.split("\\n")
        for o in output_array:
           yield o
