from tqdm import tqdm
import requests
from pathlib import Path

def download(url, file_path='', file_name=None, name='Download progress', block_size=1024): 
    if Path(file_name).is_file():
        print ("%s: File already exists. Skipping"%name)
    else:
        if len(name) > 60:
            name=name[:60]+"..."
            
        resp = requests.get(url, stream=True)
        total_size_in_bytes = int(resp.headers.get('content-length', 0))
    
        bar = tqdm(total=total_size_in_bytes, unit='iB', dynamic_ncols=False,unit_scale=True, desc=name,ncols=80)
    
        if not file_name:
            file_name = url.split('/')[-1]
    
        if file_path != '':
            if file_path[-1] == '/':
                file_path = file_path + file_name
            else:
                file_path = file_path + '/' + file_name
        else:
            file_path = file_name
    
        with open(file_path, 'wb') as file:
            for data in resp.iter_content(block_size):
                bar.update(len(data))
                file.write(data)
        bar.close()
    
        return file_path