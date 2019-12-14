#!/usr/bin/python3

import time
import os
import tempfile
import shlex
import subprocess
import re
import requests


FETCHMAIL = """
fetchmail -N \
    -f {}
"""


RC_LINE = """
poll "{host}" proto {protocol}  port {port}
    user "{username}" password "{password}"
    is "{user_email}"
    smtphost "{smtphost}"
    {options}
"""


def extract_host_port(host_and_port, default_port):
    host, _, port = re.match('^(.*)(:([0-9]*))?$', host_and_port).groups()
    return host, int(port) if port else default_port


def escape_rc_string(arg):
    return arg.replace("\\", "\\\\").replace('"', '\\"')


def fetchmail(fetchmailrc):
    with tempfile.NamedTemporaryFile() as handler:
        handler.write(fetchmailrc.encode("utf8"))
        handler.flush()
        command = FETCHMAIL.format(shlex.quote(handler.name))
        output = subprocess.check_output(command, shell=True)
        return output


def run(debug):
    source_user  = os.getenv('SOURCE_USER', '')
    source_pass  = os.getenv('SOURCE_PASS', '')
    source_host  = os.getenv('SOURCE_HOST', '')
    source_port  = os.getenv('SOURCE_PORT', '')
    source_proto = os.getenv('SOURCE_PROTOCOL', '')
    dest_user    = os.getenv('DEST_USER', '')
    dest_pass    = os.getenv('DEST_PASS', '')
    dest_host    = os.getenv('DEST_HOST', '')
    dest_port    = os.getenv('DEST_PORT', '')
    options      = os.getenv('OPTIONS', '')
    
    smtphost, smtpport = extract_host_port(os.environ.get("HOST_SMTP", "smtp"), None)
    if smtpport is None:
        smtphostport = smtphost
    else:
        smtphostport = "%s/%d" % (smtphost, smtpport)
    fetchmailrc += RC_LINE.format(
        user_email=escape_rc_string(fetch["user_email"]),
        protocol=fetch["protocol"],
        host=escape_rc_string(fetch["host"]),
        port=fetch["port"],
        smtphost=smtphostport,
        username=escape_rc_string(fetch["username"]),
        password=escape_rc_string(fetch["password"]),
        options=options
    )
    if debug:
        print(fetchmailrc)
    try:
        print(fetchmail(fetchmailrc))
        error_message = ""
    except subprocess.CalledProcessError as error:
        error_message = error.output.decode("utf8")
        # No mail is not an error
        if not error_message.startswith("fetchmail: No mail"):
            print(error_message)
        user_info = "for %s at %s" % (fetch["user_email"], fetch["host"])
        # Number of messages seen is not a error as well
        if ("messages" in error_message and
                "(seen " in error_message and
                user_info in error_message):
            print(error_message)
        
if __name__ == "__main__":
    while True:
        time.sleep(int(os.environ.get("FETCHMAIL_DELAY", 60)))
        run(os.environ.get("DEBUG", None) == "True")
