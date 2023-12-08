import os
import smtplib


class Mail(object):

    def __init__(self, cfg):
        super(Mail, self).__init__()
        self.cfg = cfg
        self.server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self.is_init = ( hasattr(self.cfg, "GMAIL_USER") and hasattr(self.cfg, "GMAIL_PASSWORD") ) and True or False

    """
    Send mail to <to> with <subject> and <body>
    """
    def send(self, to, subject, error, ctx=None):
        body = str(error)
        type(error).__name__
        commande_details = ""
        if ctx:
            full_command_name = ctx.command.qualified_name
            split = full_command_name.split(" ")
            executed_command = str(split[0])
            kwargs = f" `{ctx.kwargs}`" if ctx.kwargs.__len__() > 0 else ""
            args = f" `{[str(arg) for arg in ctx.args if ctx.args.index(arg) > 1]}`" if ctx.args.__len__() > 2 else kwargs
            commande_details = f"Commande : `{ctx.clean_prefix}{executed_command}`{args} command in {f'{ctx.channel.guild.name} - {ctx.channel.name}' if ctx.channel.guild != None else 'DM' } (ID: {ctx.channel.id}) by {ctx.message.author} (ID: {ctx.message.author.id})\n"
        to = to if type(to) == str else ", ".join(to)
        email_text = f"""\
From: {self.cfg.botName} {self.cfg.GMAIL_USER}
To: {to}
Subject: [{self.cfg.botName}] {subject}

{commande_details}
{body}
"""
        try:
            self.server.connect('smtp.gmail.com', 465)
            self.server.ehlo()
            self.server.login(self.cfg.GMAIL_USER, self.cfg.GMAIL_PASSWORD)
            self.server.sendmail(self.cfg.GMAIL_USER, to, email_text)
            self.server.close()
        except Exception as e:
            return False, e
