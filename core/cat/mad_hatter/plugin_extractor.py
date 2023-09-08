import os
import uuid
import tarfile
import zipfile
import shutil
import mimetypes
import slugify

from cat.log import log


class PluginExtractor:
    
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

        # this will be plugin folder name (its id for the mad hatter)
        self.id = slugify(path)

    def extract(self, to):

        # create tmp directory
        tmp_folder_name = f"/tmp/{uuid.uuid1()}"
        os.mkdir(tmp_folder_name)

        # extract into tmp directory
        shutil.unpack_archive(self.path, tmp_folder_name, self.extension)
        # what was extracted?
        contents = os.listdir(tmp_folder_name)

        # if it is just one folder and nothing else, that is the plugin
        if len(contents) == 1 and os.path.isdir( os.path.join(tmp_folder_name, contents[0]) ):
            folder_to_copy = os.path.join(tmp_folder_name, contents[0])
            log(f"plugin is nested, copy: {folder_to_copy}", "ERROR")
        else: # flat zip
            folder_to_copy = tmp_folder_name
            log(f"plugin is flat, copy: {folder_to_copy}", "ERROR")
        
        # move plugin folder to cat plugins folder
        extracted_path = f"{to}/mock_plugin"
        shutil.move(folder_to_copy, extracted_path)

        # cleanup
        if os.path.exists(tmp_folder_name):
            shutil.rmtree(tmp_folder_name)

        # return extracted dir path
        return extracted_path
    

    def get_extension(self):
        return self.extension

    def get_name(self):
        return self.id
