import os
 
def load_dotenv(file_path):
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
 
            key, value = line.split('=', 1)
            value = value.strip().strip('\'"')
            os.environ[key] = value
 
 
load_dotenv('.env')