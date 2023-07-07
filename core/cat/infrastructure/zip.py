import zipfile


class Zip:
    def __init__(self, path):
        self.path = path

    def unzip(self, to):
        with zipfile.ZipFile(self.path, 'r') as zip_ref:
            zip_ref.extractall(to)

    def get_name(self):
        return self.path.split("/")[-1]
