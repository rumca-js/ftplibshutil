
import unittest
import logging
import os

import ftpshutil
import ftpshutil.ftpconfig as ftpconfig

import ftpshutil.dircrc as dircrc

from ftplib import *


class FtpMock(FTP):
    """
    This mock class replaces ftp lib connection.
    We want to write unit test here!
    """

    def __init__(self):
        self._files = {'/Test/file.txt' : 'contents'}
        self._dirs = ['/', '/Test']
        self._cwd = ''
    	
    def nlst(self, apath):
        result = []
        
        for afile in self._files:
            if afile.startswith(apath):
                result.append(afile)
                
        for adir in self._dirs:
            if afile.startswith(apath):
                result.append(adir)
                
        return result
        
    def quit(self):
        pass
        
    def cwd(self, path):
        if not path.startswith("/"):
             path = os.path.join(self._cwd, path)
             
        if path in self._dirs:
            self._cwd = path
        else:
            raise error_perm("No such path: "+path)
        
    def mkd(self, adir):
        dst_dir = os.path.join(self._cwd, adir)
        if dst_dir not in self._dirs:
            self._dirs.append(dst_dir)
        
    def rmd(self, adir):
        self._dirs.remove(adir)
        
    def retrlines(self, cmd, callback = None):
        dirstring = 'drwxr-sr-x    5 1176     1176         4096 Dec 19  2000 {}'
        filestring = '-rw-rw-r--    1 1176     1176         1063 Jun 15 10:18 {}'
        result = ''
    
        for afile in self._files:
            filestring = filestring.format(afile)
            result += filestring + "\n"
            
        for adir in self._dirs:
            dirstring = dirstring.format(adir)
            result += dirstring + "\n"
    
        return result
        
    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        sp = cmd.split(" ")
        if sp[0] == "STOR":
            afile = sp[1]
            contents = fp.read()
            self._files[afile] = contents
        
    def retrbinary(self, cmd, callback=None, blocksize=8192, rest=None):
        sp = cmd.split(" ")
        if sp[0] == "RETR":
            afile = sp[1]
            if afile in self._files:
                callback(self._files[afile])


class TestStringMethods(unittest.TestCase):

    ftp = None

    def setUp(self):
        if not TestStringMethods.ftp:

            config = ftpconfig.FtpConfig()
            config.read()

            TestStringMethods.ftp = ftpshutil.FTPShutil()
            TestStringMethods.ftp._ftp = FtpMock()

            logging.info("Connected") 

        if TestStringMethods.ftp.exists("/Test"):
            TestStringMethods.ftp.rmtree("/Test")

    def tearDown(self):
        TestStringMethods.ftp.quit()
        TestStringMethods.ftp = None

    def test_mkdir(self):
        TestStringMethods.ftp.mkdir("/Test")
                
        self.assertTrue( TestStringMethods.ftp._ftp._dirs == ['/','/Test'])

        self.assertTrue( TestStringMethods.ftp.exists("/Test") )

    def test_rmtree(self):
        TestStringMethods.ftp.mkdir("/Test")
        TestStringMethods.ftp.rmtree("/Test")

        self.assertFalse( TestStringMethods.ftp.exists("/Test") )

    def test_makedirs(self):
        if TestStringMethods.ftp.exists("/Test"):
            TestStringMethods.ftp.rmtree("/Test")

        TestStringMethods.ftp.makedirs("/Test/uno")
        
        self.assertTrue( '/Test' in TestStringMethods.ftp._ftp._dirs)
        self.assertTrue( '/Test/uno' in TestStringMethods.ftp._ftp._dirs)

        self.assertTrue( TestStringMethods.ftp.exists("/Test") )
        self.assertTrue( TestStringMethods.ftp.exists("/Test/uno") )

    def test_listdir_empty_dir(self):
        TestStringMethods.ftp.makedirs("/Test/uno")

        self.assertTrue( TestStringMethods.ftp.listdir("/Test/uno") == [])

    def test_write_read(self):
        TestStringMethods.ftp.makedirs("/Test/uno")
        TestStringMethods.ftp.write("/Test/uno/my_file", b"test")

        self.assertTrue( TestStringMethods.ftp.read("/Test/uno/my_file") == b"test")

    def test_crc(self):
        dircrc.create_dircrcs("test")

        crc_file = os.path.join("test", "crc_list.txt")
        self.assertTrue( os.path.isfile( crc_file))

        with open(crc_file, 'r') as fh:
            data = fh.read()

        example = """[CRC List]
./crc_list.txt = -2
./one_test_file.txt = 4227995677

"""

        self.assertTrue( example == data)


if __name__ == '__main__':
    unittest.main()
