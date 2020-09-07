# Overview
This is a FTP library that provides simple means for downloading and uploading files.
It can be installed using python3 setup tools works. Requires root priviliges.
```
python3 setup.py install
```
You can use directly ftpshutil/ftpshutil.py file in your project instead of installing with setup tools.

# API
Can be observed using examples/ftpmgr.py. Provides FTPShutil class with the following methods:
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

# Experimental API with CRC

Sometimes you do not want to transfer entire page into the Internet. You have a webpage, you modified one page and you need to transfer only that page, not entire image assets of your page.
For every directory on your local file system a CRC checksum file is generated. If the checksum of that directory is exactly the same as the remote checksum, then this directory is skpped

Download with CRC checking:
 - downloadfile_sync
     ```
     def downloadfile_sync(self, remote_file, local_file):
     ```

Upload with CRC checking:
 - downloadfile_sync
     ```
     def downloadfile_sync(self, remote_file, local_file):
     ```

It is important to know that right now the entire directory is transferred, is something is changed.

The CRC file is a simple INI file, with one section. It contains a list of files with checksum values, and directory listing.

# Other

You can try installing this using pip. I have not checked if that works.
```
pip install git+https://github.com/rumca-js/ftplibshutil.git#egg=ftpshutil-renegat0x0
```
