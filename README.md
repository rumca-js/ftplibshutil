# Overview
This is a FTP library that provides simple means for downloading and uploading files.
It can be installed using python3 setup tools works. Requires root priviliges.
```
python3 setup.py install
```
You can use directly ftpshutil/ftpshutil.py file in your project instead of installing with setup tools.

# API
Can be observed using examples/down.py. Provides FTPShutil class with the following methods:
 - download_dir
     ```
     def download_dir(self, directory):
     ```
 - upload_dir
     ```
     def upload_dir(self, directory):
     ```
 - quit
     ```
     def quit(self):
     ```

The walk_ftp_dir method might be used to traverse a directory tree. As the first argument accepts python ftplib FTP object. The FTPShutil has ftp field, which represents this object. 
```
def walk_ftp_dir(ftp, root_dir):
```
This can be used therefore like
```
ftp = FTPShutil(server,user,password)
for root, dirs, files in walk_ftp_dir(ftp.ftp, "MyDirectory"):
    print(dirs)
    print(files)
```

# Other

You can try installing this using pip. I have not checked if that works.
```
pip install git+https://github.com/rumca-js/ftplibshutil.git#egg=ftpshutil-renegat0x0
```
