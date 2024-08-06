import os
import uuid
import shutil
import mimetypes
from slugify import slugify



class PluginExtractor:
    admitted_mime_types = ["application/zip", "application/x-tar"]

    def __init__(self, path):
        content_type = mimetypes.guess_type(path)[0]
        if content_type == "application/x-tar":
            self.extension = "tar"
        elif content_type == "application/zip":
            self.extension = "zip"
        else:
            raise Exception(
                f"Invalid package extension. Valid extensions are: {self.admitted_mime_types}"
            )

        self.path = path

        # this will be plugin folder name (its id for the mad hatter)
        self.id = self.create_plugin_id()

    def create_plugin_id(self):
        file_name = os.path.basename(self.path)
        file_name_no_extension = os.path.splitext(file_name)[0]
        return slugify(file_name_no_extension, separator="_")

    def extract(self, to):
        # create tmp directory
        tmp_folder_name = f"/tmp/{uuid.uuid1()}"
        os.mkdir(tmp_folder_name)

        # extract into tmp directory
        shutil.unpack_archive(self.path, tmp_folder_name, self.extension)
        # what was extracted?
        contents = os.listdir(tmp_folder_name)

        # if it is just one folder and nothing else, that is the plugin
        if len(contents) == 1 and os.path.isdir(
            os.path.join(tmp_folder_name, contents[0])
        ):
            folder_to_copy = os.path.join(tmp_folder_name, contents[0])
        else:  # flat zip
            folder_to_copy = tmp_folder_name

        # move plugin folder to cat plugins folder
        extracted_path = os.path.join(to, self.id)
        # if folder exists, delete it as it will be replaced
        if os.path.exists(extracted_path):
            settings_file_path = os.path.join(extracted_path, "settings.json")
            # check if settings.json exists in the folder
            if os.path.isfile(settings_file_path):
                # copy settings.json to the temporary directory
                shutil.copy(settings_file_path, folder_to_copy)
            shutil.rmtree(extracted_path)
        # extracted plugin in plugins folder!
        shutil.move(folder_to_copy, extracted_path)

        # cleanup
        if os.path.exists(tmp_folder_name):
            shutil.rmtree(tmp_folder_name)

        # return extracted dir path
        return extracted_path

    def get_extension(self):
        return self.extension

    def get_plugin_id(self):
        return self.id
