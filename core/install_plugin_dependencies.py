import os

for root, dirs, files in os.walk("./cat/plugins"):
    for file in files:
        if file == "requirements.txt":
            req_file = os.path.join(root, file)
            os.system(f'pip install --no-cache-dir -r "{req_file}"')
