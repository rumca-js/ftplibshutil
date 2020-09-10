# Overview
This is a FTP library that provides simple means for downloading and uploading files.
It can be installed using python3 setup tools works.
```
python setup.py install
```
You can use directly ftpshutil/ftpshutil.py file in your project instead of installing with setup tools.

# API

## General

The walk_ftp_dir method might be used to traverse a directory tree. As the first argument accepts the FTPShutil object.

```
def walk_ftp_dir(ftp, root_dir):
```

This can be used therefore like:

```
ftp = FTPShutil(server,user,password)
for root, dirs, files in walk_ftp_dir(ftp, "MyDirectory"):
    print(dirs)
    print(files)
```

## FTPShutil class

Can be observed using examples/ftpmgr.py. Provides FTPShutil class with the following methods:

 - downloadtree
     ```
     def downloadtree(self, directory, destination):

     ```
 - uploadtree
     ```
     def uploadtree(self, directory, destination):
     ```
 - uploadfile
    ```
    def uploadfile(self, local_file, remote_file):
    ```
 - downloadfile
    ```
    def downloadfile(self, remote_file, local_file):
    ```
 - listdir. Returns list of files / directories withing the location.
     ```
    def listdir(self, root_dir):
     ```
 - listdir_ex. Returns list of directories and files in the root_dir (as a tuple of two lists)
     ```
    def listdir_ex(self, root_dir):
     ```
 - write. Allows to create a file with the specified data.
     ```
    def write(self, file_path, data):
     ```
 - read. Allows to read contents of a file.
     ```
    def read(self, file_path):
     ```
 - mkdir
    ```
    def mkdir(self, path):
    ```
 - makedirs
    ```
    def makedirs(self, path):
    ```
 - rename
    ```
    def rename(self, fromname, toname):
    ```
 - exists
    ```
    def exists(self, path):
    ```
 - isdir
    ```
    def isdir(self, dir_path):
    ```
 - isfile
    ```
    def isfile(self, dir_path):
    ```
 - remove_file
    ```
    def remove_file(self, path):
    ```
 - remove_dir
    ```
    def remove_dir(self, path):
    ```
 - rmtree
    ```
    def rmtree(self, directory):
    ```
 - get_ftplib_handle
    ```
    def get_ftplib_handle(self):
    ```
 - quit
    ```
    def quit(self):
    ```

# API with CRC synchronization

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

The CRC file is a simple INI file format, with one section. It contains a list of files with checksum values, and directory listing.

# Other

You can try installing this using pip. I have not checked if that works.
```
pip install git+https://github.com/rumca-js/ftplibshutil.git#egg=ftpshutil-renegat0x0
```
