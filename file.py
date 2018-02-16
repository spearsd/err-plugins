from errbot import BotPlugin, botcmd
import subprocess, tempfile, re, time

class File(BotPlugin):
"""File retrieval plugin for Errbot"""

    @botcmd(split_args_with=None)
    def file_retrieve(self, msg, args):
        """Retrieve file from errbot"""
        file_to_get = args[0]
        path = ""
        for s in self.get_plugin('Setup').share_drive_paths:
            if str(msg.frm) in s:
                path = s.split(':')[1].rstrip('/')
        if path == "":
            yield "Share drive must be setup first. use !setup path /path/to/sharedrive"
        else:
            string = '<a href="file://' + path + file_to_get + '">' + file_to_get + '</a>'
            yield string
            yield "Note: If this link does not work, your shared drive is not properly configured."
