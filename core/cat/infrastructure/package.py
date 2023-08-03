import os
import tarfile
import zipfile
import mimetypes


class Package:
    
    admitted_mime_types = ['application/zip', 'application/x-tar']

    def __init__(self, path):
        content_type = mimetypes.guess_type(path)[0]
        if content_type == 'application/x-tar':
            self.extension = 'tar'
        elif content_type == 'application/zip':
            self.extension = 'zip'
        else:
            raise Exception(f"Invalid package extension. Valid extensions are: {self.admitted_mime_types}")

        self.path = path

    def unpackage(self, to):

        # list of folder contents before extracting
        ls_before = os.listdir(to)

        # extract
        if self.extension == 'zip':
            with zipfile.ZipFile(self.path, 'r') as zip_ref:
                zip_ref.extractall(to)
        elif self.extension == 'tar':
            with tarfile.open(self.path, 'r') as tar_ref:
                tar_ref.extractall(to)

        # list of folder contents after extracting
        ls_after = os.listdir(to)

        # return extracted contents paths
        # TODO: does not handle overwrites, should extract in a /temp new folder and then copy to destination
        ls = set(ls_after) - set(ls_before)
        return list(ls)

    def get_extension(self):
        return self.extension

    def get_name(self):
        return self.path.split("/")[-1]
