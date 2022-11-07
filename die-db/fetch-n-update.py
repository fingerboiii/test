
import time
import os
import boto3
from git import Repo

#logging.basicConfig(filename='AutomatedDIEdb.log', level=logging.NOTSET, format='%(asctime)s:%(levelname)s:%(message)s')
s3 = boto3.resource('s3', region_name='ap-southeast-1')
s3bucket = s3.Bucket("chum-bucket1")

def upload_folder_to_s3(s3bucket, inputDir, s3Path):
        print("Uploading results to s3 initiated...")
        print("Local Source:",inputDir)
        os.system("ls -ltR " + inputDir)

        print("Dest  S3path:",s3Path)

        try:
            for path, subdirs, files in os.walk(inputDir):
                for file in files:
                    dest_path = path.replace(inputDir,"")
                    __s3file = os.path.normpath(s3Path + '/' + dest_path + '/' + file)
                    __local_file = os.path.join(path, file)
                    print("upload : ", __local_file, " to Target: ", __s3file, end="")
                    s3bucket.upload_file(__local_file, __s3file)
                    print(" ...Success")
        except Exception as e:
            print(" ... Failed!! Quitting Upload!!")
            print(e)
            raise e



#repo_path = "/temp70"
#Repo.clone_from("https://github.com/fingerboiii/test.git", "/temp71")
#upload_folder_to_s3(s3bucket, "D:/temp71/db", "db")

try:
    Repo.clone_from("https://github.com/fingerboiii/test.git", "/temp71")
    print("repository cloned")
    upload_folder_to_s3(s3bucket, "D:/temp71/db", "db")
except:
    print("local repository already created")

def check_for_update(repo_path):
    Repo(repo_path).remotes.origin.fetch()
    diff = str(Repo(repo_path).git.diff('origin/master')).splitlines()
    if len(diff) != 0:
        Repo(repo_path).remote().pull("master")
        print("Commits detected. Pulling changes")
        upload_folder_to_s3(s3bucket, "D:/temp71/db", "db")
    else:
        print("No commits detected.")
        time.sleep(60)


while True:
    check_for_update("/temp71")