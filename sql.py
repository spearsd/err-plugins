from errbot import BotPlugin, botcmd
import subprocess, tempfile, re, time

class SQLPlugin(BotPlugin):
    """SQL plugin for Errbot"""
    
    user = ""
    passwd = ""
    server = ""
    error = ""
    
    def set_variables(self, msg):
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
    
    def check_access(self, msg):
        self.error = ""
        try:
            self.set_variables(msg)
        except:
            self.error = "Unable to retrieve your credentials. "
        
        try:
            subprocess.check_output(["mysql", "-u", self.user, self.passwd, "-h", self.server, "-e", "SELECT * FROM test.table1"])
        except:
            self.error = self.error + "Error connecting with your user, do you have the correct permissions? "
    
    @botcmd(split_args_with=None)
    def sql_select(self, msg, args):
        """Return result of select statement. ex: !sql select * db.tablename"""
        
        self.check_access(msg)
        
        what_to_select = args[0]
        table = args[1]
        query = "SELECT "+ what_to_select + " FROM " + table

        if self.error == "":
            error_occurred = False
            try:
                output = subprocess.check_output(["mysql", "-u", self.user, self.passwd, "-h", self.server, "-e", query])
            except:
                error_occurred = True
                yield "Error occurred while trying to execute sql query."
                
            if not error_occurred:
                output_array_list = str(output).split("'")[1].split("\\n")
                first_line = True
                for o in output_array_list:
                    output_array = o.split("\\t")
                    whole_line = ""
                    for x in output_array:
                        whole_line = whole_line + x + "     "
                    if first_line:
                        yield whole_line
                        yield "------------------"
                        first_line = False
                    else:
                        yield whole_line
        else:
            yield self.error

    @botcmd(split_args_with=None)
    def sql_file_retrieve(self, msg, args):
        """Retrieve file from errbot"""
        file_to_get = args[0]
        string = '<a href="file:///media/sf_sql_files/' + file_to_get + '">' + file_to_get + '</a>'
        yield string
                
    @botcmd(split_args_with=None)
    def sql_file(self, msg, args):
        """Execute shared drive or remote sql file. ex: !sql file --url http://path.to.file/file.sql"""
        self.check_access(msg)
        
        if args[0] == "--url":
            file_url = args[1]
            try:
                wget_url = "wget -O /tmp/sql_file.sql " + file_url
                subprocess.Popen([wget_url], shell=True, stdout=subprocess.PIPE)
                time.sleep(1)
                if self.error == "":
                    error_occurred = False
                    contents = ""
                    with open('/tmp/sql_file.sql') as f:
                        for line in f.readlines():
                            contents += line
                    try:
                        output = subprocess.check_output(["mysql", "-u", self.user, self.passwd, "-h", self.server, "-e", contents])
                    except:
                        error_occurred = True
                        yield "Error occurred while trying to execute sql file."
            except:
                self.error = error + ""
        else:
            file = "/tmp/" + args[0]
            if self.error == "":
                error_occurred = False
                contents = ""
                try:
                    with open(file) as f:
                        for line in f.readlines():
                            contents += line
                except:
                    error_occurred = True
                    yield "Error occurred while trying to read sql file. Does it exist?"
                try:
                    output = subprocess.check_output(["mysql", "-u", self.user, self.passwd, "-h", self.server, "-e", contents])
                except:
                    error_occurred = True
                    yield "Error occurred while trying to execute sql file."

        if not error_occurred:
            output_array_list = str(output).split("'")[1].split("\\n")
            first_line = True
            for o in output_array_list:
                output_array = o.split("\\t")
                whole_line = ""
                for x in output_array:
                    whole_line = whole_line + x + "     "
                if first_line:
                    yield whole_line
                    yield "------------------"
                    first_line = False
                else:
                    yield whole_line
        else:
            yield self.error
