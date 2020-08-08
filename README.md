# Overview
This is a FTP library that provides simple means for downloading and uploading files.
It can be installed using python3 setup tools works. Requires root priviliges.
```
python3 setup.py install
```
You can use directly ftpshutil/ftpshutil.py file in your project instead of installing with setup tools.

# API
Can be observed using examples/down.py. Provides FTPShutil class with the following methods:
 - downloadtree
     ```
     def downloadtree(self, directory, destination):

     ```
 - upload_dir
     ```
     def uploadtree(self, directory, destination):
     ```
 - mkdirs
     ```
     def mkdirs(self, path):
     ```
 - exists
     ```
     def exists(self, path):
     ```
 - uploadfile
     ```
     def uploadfile(self, local_file, remote_file):
     ```
 - downloadfile
     ```
     def downloadfile(self, remote_file, local_file):
     ```
 - get_ftplib_handle
     ```
     def get_ftplib_handle(self):
     ```
 - quit
     ```
     def quit(self):
     ```

The walk_ftp_dir method might be used to traverse a directory tree. As the first argument accepts the FTPShutil object.
```
def walk_ftp_dir(ftp, root_dir):
```
This can be used therefore like
```
ftp = FTPShutil(server,user,password)
for root, dirs, files in walk_ftp_dir(ftp, "MyDirectory"):
    print(dirs)
    print(files)
```

# Other

You can try installing this using pip. I have not checked if that works.
```
pip install git+https://github.com/rumca-js/ftplibshutil.git#egg=ftpshutil-renegat0x0
```
