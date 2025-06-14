# -*- coding: utf-8 -*-

# ################################################################### #
#                                                                     #
#  BigBrotherBot(B3) (www.bigbrotherbot.net)                         #
#  Copyright (C) 2005 Michael "ThorN" Thornton                        #
#                                                                     #
#  This program is free software; you can redistribute it and/or      #
#  modify it under the terms of the GNU General Public License        #
#  as published by the Free Software Foundation; either version 2     #
#  of the License, or (at your option) any later version.             #
#                                                                     #
#  This program is distributed in the hope that it will be useful,    #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of     #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the       #
#  GNU General Public License for more details.                       #
#                                                                     #
#  You should have received a copy of the GNU General Public License  #
#  along with this program; if not, write to the Free Software        #
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA      #
#  02110-1301, USA.                                                   #
#                                                                     #
# ################################################################### #

import b3
import b3.config
import json
import os
import re
import string
import sys
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from packaging import version
from time import sleep

# Import the required path functions
from b3 import HOMEDIR, B3_CONFIG_GENERATOR

## url from where we can get the latest B3 version number
URL_B3_LATEST_VERSION = 'http://master.bigbrotherbot.net/version.json'

## supported update channels
UPDATE_CHANNEL_STABLE = 'stable'
UPDATE_CHANNEL_BETA = 'beta'
UPDATE_CHANNEL_DEV = 'dev'


class B3version(version.Version):
    """
    Version numbering for BigBrotherBot.
    Uses packaging.version.Version for version comparison.
    """
    def __init__(self, version_string):
        # Clean up version string to be compatible with PEP 440
        cleaned = str(version_string).replace('dev', 'dev0')
        super().__init__(cleaned)


def getDefaultChannel(currentVersion):
    """
    Return an update channel according to the current B3 version.
    :param currentVersion: The B3 version to use to compute the update channel
    :return: str
    """
    try:
        v = B3version(currentVersion)
        if 'dev0' in str(v):
            return 'dev'
        elif 'a' in str(v):
            return 'beta'
        elif 'b' in str(v):
            return 'beta'
        else:
            return 'stable'
    except Exception:
        return 'stable'


def checkUpdate(currentVersion, channel=None, singleLine=True, showErrormsg=False, timeout=4):
    """
    Check if an update is available for the current version of B3 on the given channel.
    :param currentVersion: The current version of B3
    :param channel: The channel from where to get the up-to-date version number
    :param singleLine: Whether to format the message on a single line or not
    :param showErrormsg: Whether to display the error message on failures
    :param timeout: The timeout to be used for the HTTP connection
    :return: str
    """
    if channel is None:
        channel = getDefaultChannel(currentVersion)

    def _get_version_info(_data, _channel):
        """
        Return version information from the given data dict.
        :param _data: A dictionary holding versions information
        :param _channel: The channel to use for the lookup
        :return: tuple (version_number, download_url)
        """
        _channels = _data.get('channels', {})
        return _channels.get(_channel, {}).get('version', None), _channels.get(_channel, {}).get('url', None)

    def _get_response(_url):
        """
        Get version information from the remote host.
        :param _url: The URL to fetch the information from
        :return: dict
        """
        req = urllib2.Request(_url)
        req.add_header('User-Agent', 'B3 (www.bigbrotherbot.net)')
        res = urllib2.urlopen(req, timeout=timeout)
        return json.loads(res.read().decode('utf-8'))

    # try to fetch version information from the remote host
    try:
        data = _get_response(URL_B3_LATEST_VERSION)
        latestVersion, latestUrl = _get_version_info(data, channel)
    except Exception as e:
        message = 'could not check for update: %s' % e
        if showErrormsg:
            return message
        else:
            return None

    # skip if we get an empty response for the specific channel
    if not latestVersion:
        message = 'could not check for update: no such channel (%s)' % channel
        if showErrormsg:
            return message
        else:
            return None

    else:
        _lver = B3version(latestVersion)
        _cver = B3version(currentVersion)
        if _cver < _lver:
            if singleLine:
                message = 'update available (v%s : %s)' % (latestVersion, latestUrl)
            else:
                message = r"""
                 _\|/_
                 (o o)    {version:^21}
         +----oOO---OOo-----------------------+
         |                                    |
         |                                    |
         | A newer version of B3 is available |
         |                                    |
         | {url:^34} |
         |                                    |
         |                                    |
         +------------------------------------+
                """.format(version='v%s' % latestVersion, url=latestUrl)

            return message

        else:
            return None


def console_exit(message):
    """
    Exit with a message.
    :param message: The message to be printed on sys.stderr
    """
    if not message.endswith('\n'):
        message += '\n'
    sys.stderr.write(message)
    if sys.platform.startswith('win'):  
        input("press any key to continue...")
    sys.exit(1)


def clearscreen():
    """
    Clear the console screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class DBUpdate(object):
    """
    Console application responsible for updating the B3 database schema.
    """
    config = None
    console = None

    def __init__(self, config=None):
        """
        Object constructor.
        :param config: The B3 configuration file instance
        """
        if config:
            if not os.path.isfile(config):
                console_exit('ERROR: configuration file not found (%s)' % config)

        # load the configuration file
        try:
            if config:
                self.config = b3.config.load(config)
            else:
                for p in (os.path.join(HOMEDIR, 'conf', 'b3.xml'),
                          os.path.join(HOMEDIR, 'conf', 'b3.ini'),
                          os.path.join(HOMEDIR, 'b3.xml'),
                          os.path.join(HOMEDIR, 'b3.ini'),
                          os.path.join(HOMEDIR, 'conf', 'b3.distribution.xml')):
                    if os.path.isfile(p):
                        config = p
                        break

                if not config:
                    console_exit('ERROR: could not find any valid configuration file')

                self.config = b3.config.load(config)

            if self.config.analyze():
                raise b3.config.ConfigFileNotValid
        except b3.config.ConfigFileNotValid:
            console_exit('ERROR: configuration file not valid (%s).\n'
                         'Please visit %s to generate a new one.' % (config, B3_CONFIG_GENERATOR))

    def run(self):
        """
        Run the DB update
        """
        clearscreen()
        print(r"""
                        _\|/_
                        (o o)    {:>32}
                +----oOO---OOo----------------------------------+
                |                                               |
                |             UPDATING B3 DATABASE              |
                |                                               |
                +-----------------------------------------------+

        """.format('B3 : %s' % b3.__version__))

        input("press any key to start the update...")

        def _update_database(storage, update_version):
            """
            Update a B3 database.
            :param storage: the B3 storage module
            :param update_version: the B3 version we are updating to
            """
            if b3.getB3versionString() != update_version:
                console_exit('B3 version mismatch: expected \'%s\' but got \'%s\': '
                             'check your B3 installation' % (update_version, b3.getB3versionString()))

            try:
                clearscreen()
                if storage.update():
                    print('B3 database update completed!')
                else:
                    print('B3 database already up-to-date!')
            except Exception as err:
                console_exit('B3 database update failed: %s' % err)

        # importing here so the B3 config file gets parsed
        # before the storage module is loaded
        import b3.storage
        _update_database(b3.storage.getStorage(), b3.getB3versionString())


if __name__ == '__main__':

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-c', '--config',
                      dest='config',
                      default=None,
                      metavar='CONFIG_FILE',
                      help='B3 config file. Example: -c b3.xml')

    options, args = parser.parse_args()
    update = DBUpdate(config=options.config)
    update.run()
