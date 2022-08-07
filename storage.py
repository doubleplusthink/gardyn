import os, uuid, sys
import time
from azure.storage.blob import BlockBlobService, PublicAccess
from config import STORAGE_SERVER, STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY, IMG_CONTAINER_NAME, LOG_CONTAINER_NAME
from util import get_serial

class BaseStorage:
    
    def __init__(self, container=IMG_CONTAINER_NAME):
        self.service = BlockBlobService(account_name=STORAGE_ACCOUNT_NAME, account_key=STORAGE_ACCOUNT_KEY)
        self.container = container

    def upload(self, file_path):
        try:
            self.service.create_blob_from_path(self.container, os.path.basename(file_path), file_path)
        except Exception as e:
            print(repr(e))

    def get_list(self):
        try:
            blobs = self.service.list_blobs(self.container)
            return [blob for blob in blobs] 
        except Exception as e:
            print(repr(e))
    
    def download(self, name, file_path):
        try:
            self.service.get_blob_to_path(self.container, os.path.basename(file_path), file_path)
        except Exception as e:
            print(repr(e))

    def copy(self, src, target):
        try:
            full_uri = '{}/{}/{}'.format(STORAGE_SERVER, IMG_CONTAINER_NAME, os.path.basename(src))
            self.service.copy_blob(self.container, os.path.basename(target), full_uri)
        except Exception as e:
            print(repr(e))

class ImageStorage(BaseStorage):
    def __init__(self, container=IMG_CONTAINER_NAME):
        super().__init__(container=container)
        
class LogStorage(BaseStorage):
    def __init__(self, container=LOG_CONTAINER_NAME):
        super().__init__(container=container)

    def upload(self, file_path):
        try:
            serial = get_serial()
            self.service.create_blob_from_path(self.container, '{}_{}'.format(serial, os.path.basename(file_path)), file_path)
        except Exception as e:
            print(repr(e))

# Main method.
if __name__ == '__main__':
    pass