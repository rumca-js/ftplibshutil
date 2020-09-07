import os
import configparser

class FtpConfig(object):

    file_name = "ftp_config.ini"
    section_name = "Config"
    config = None

    def read(self):
        if os.path.isfile(FtpConfig.file_name):
            FtpConfig.config = configparser.ConfigParser()
            FtpConfig.config.read(FtpConfig.file_name)
        else:
            raise IOError("The file does not exist {0}".format(FtpConfig.file_name))

    def write(self):
       with open(FtpConfig.file_name , 'w') as configfile:
            FtpConfig.config.write(configfile)

    def get(self, key):
        return FtpConfig.config[FtpConfig.section_name][key]

    def set(self, key, value):
        FtpConfig.config[section_name][key] = value
