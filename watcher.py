import sys
import os
import time
import logging
import requests
from requests.auth import HTTPDigestAuth
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#User configurable options

#This is the address of the management console server
MANAGEMENT_CONSOLE_URL="http://192.168.2.2/bitconsole/mgtconsolemsghandler.php"
#User name for web server authentication if required
USER="passmark"
#Password for web server authentication if required
PASSWD="passmark"
#Directory to watch for files uploaded from memtest (tftp server upload directory)
WATCHDIR="C:\Server\htdocs\memtest86-site\Clients"

#End user configurable options

class DirectoryWatchhandler(FileSystemEventHandler):
    def process(self, event):
        print("File change " + event.src_path)
        filename = event.src_path
        #Only process XML files
        if(filename.lower().endswith('.xml')==False): 
           return
        try:
          file=open(filename, 'rb')
          payload=file.read()
          file.close()
          print ("Posting " + filename + " to server")
          if(USER != ""):
              r = requests.post(MANAGEMENT_CONSOLE_URL, payload, auth=HTTPDigestAuth(USER,PASSWD), timeout=5)
          else:
               r = requests.post(MANAGEMENT_CONSOLE_URL, payload, timeout=5)
          print ("session response: '{}'".format(r.status_code)) 
      
          #try to delete file, if it doesn't delete not an issue as next time it is overwritten it will trigger the script
          print ("Deleting local copy of " + filename)
          os.remove(filename)
        except Exception as e:
          print (e)
    def on_modified(self, event):
        if(event.event_type != 'deleted'):
            self.process (event)
    # Modified seems to be called for creation and update, so just process it
    #def on_created(self, event):
    #    self.process (event.src_path)

print ("Watching directory: " + WATCHDIR + " for Memtest86 status files");
print ("Sending files to management console at " + MANAGEMENT_CONSOLE_URL);
print ("Waiting for files from Memtest86 (Use Ctrl-c to exit)")

observer = Observer()
observer.schedule(DirectoryWatchhandler(), WATCHDIR, recursive=False)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    print ("\nCtrl-c caught, shutting down")
    sys.exit()
except requests.exceptions.ConnectionError as e:
 print ("HTML post error '{}'".format(e) )
 sys.exit()
except Exception as e:
 print ("Error '{}'".format(e) )
 sys.exit()
except:
 e = sys.exec_info()[0]
 print ("Other Error '{}'".format(e) )
 sys.exit()

observer.join() 

#Should check we can access the expected web server with credentials, eg not getting a 401 error

