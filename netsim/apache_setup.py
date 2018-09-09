import sys

sys.path.append('../common')

import os
import shutil
import logging
import platform
from util import check_output, strip_comments

NETSIM_STRING = '# Modified by netsim'

APACHE = '/usr/local/apache2/bin/httpd'
APACHE_CONF = '/usr/local/apache2/conf/httpd.conf'
APACHE_CONF_BAK = '/usr/local/apache2/conf/httpd.conf.bak'
APACHE_DOC_ROOT = '/var/www'

APACHE_VIRTUAL_HOST_TEMPLATE = '''

Listen %s:8080
<VirtualHost %s:8080>
    ServerAdmin webmaster@localhost
    ServerName video.cs.cmu.edu:8080

    DocumentRoot %s
    <Directory />
        Options FollowSymLinks
        AllowOverride None
    </Directory>
    <Directory %s/>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride None
        Order allow,deny
        allow from all
    </Directory>

</VirtualHost>'''

LINUX = platform.linux_distribution()[0]


def is_apache_configured_split_conf(ports):
    found = False
    try:
        with open(ports, 'r') as portsf:
            for line in portsf:
                if NETSIM_STRING in line:
                    found = True
                    break
        portsf.closed
    except Exception as e:
        logging.getLogger(__name__).error(e)
    return found


def is_apache_configured_single_conf(conf):
    found = False
    try:
        with open(conf, 'r') as conff:
            for line in conff:
                if NETSIM_STRING in line:
                    found = True
                    break
        conff.closed
    except Exception as e:
        logging.getLogger(__name__).error(e)
    return found


def is_apache_configured():
    return is_apache_configured_single_conf(APACHE_CONF)


def configure_apache_single_conf(ip_list, conf, conf_bak, doc_root):
    try:
        # back up the existing httpd.conf
        shutil.copyfile(conf, conf_bak)

        found = False
        with open(conf, 'r') as conffile:
            for line in conffile:
                if 'ServerName' in line and line[0] != '#':
                    found = True
                    break
        conffile.closed
        with open(conf, 'a') as conffile:
            conffile.write('%s\n' % NETSIM_STRING)
            if not found:
                conffile.write('\nServerName www.example.com:80\n')
            for ip in ip_list:
                conffile.write(APACHE_VIRTUAL_HOST_TEMPLATE % (ip, ip, doc_root, doc_root))
        conffile.closed

    except Exception as e:
        logging.getLogger(__name__).error(e)


# Prepare apache VirtualHost for each server ip in ip_list
def configure_apache(ip_list):
    configure_apache_single_conf(ip_list, APACHE_CONF, \
                                 APACHE_CONF_BAK, APACHE_DOC_ROOT)


def reset_apache_single_conf(ip_list, conf, conf_bak):
    try:
        # restore ports.conf from backup
        if os.path.isfile(conf_bak):
            shutil.move(conf_bak, conf)
        else:
            logging.getLogger(__name__).warning('Could not find %s' % conf_bak)

        # TODO: clean this up
        found = False
        if os.path.isfile(conf):
            with open(conf, 'r') as conffile:
                for line in conffile:
                    if 'ServerName' in line and line[0] != '#':
                        found = True
                        break
            conffile.closed
        if not found:
            with open(conf, 'a') as conffile:
                conffile.write('\nServerName www.example.com:80\n')
            conffile.closed
    except Exception as e:
        logging.getLogger(__name__).error(e)


# Put apache back to normal
def reset_apache(ip_list):
    reset_apache_single_conf(ip_list, APACHE_CONF, APACHE_CONF_BAK)


def restart_apache_binary(bin):
    check_output('%s -k restart' % bin, shouldPrint=True)


def restart_apache_script(script):
    check_output('%s restart' % script, shouldPrint=False)


def restart_apache():
    restart_apache_binary(APACHE)
