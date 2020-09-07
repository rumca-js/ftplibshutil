
import unittest

import ftpshutil

myuser = 'user'
mypass = 'pass'
myserver= 'myserver.com'


class TestStringMethods(unittest.TestCase):

    ftp = None

    def setUp(self):
        if not ftp:
            ftp = ftpshutil.FTPShutil(myserver, user=myuser, passwd=mypass )     # connect to host, default port
            logging.info("Connected") 

        if ftp.exists("/Test"):
            ftp.rmtree("/Test")

    def tearDown(self):
        ftp.quit()

    def test_mkdir(self):
        ftp.mkdir("/Test")

        self.assertTrue( ftp.exists("/Test") )

    def test_rmtree(self):

        if ftp.exists("/Test"):
            ftp.rmtree("/Test")

        self.assertFalse( ftp.exists("/Test") )


if __name__ == '__main__':
    unittest.main()
