import django
import sys
import os
import subprocess
import dirconfig
import time
import zipfile
from demo import config

sys.path.append('~/apps/lbc')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lbc_django.settings')

django.setup()

from demo.models import ManagedScript

def start_script(test_id):

    """Run (this!) script with appropriate arguments"""

    cmd = [dirconfig.PYTHON_PATH, 'runscripts.py', str(test_id)]

    proc = subprocess.Popen(cmd)
    ManagedScript.objects.create(pid=proc.pid, running=True, test_id=test_id)

if __name__ == '__main__':
    
    from demo.models import ImageFile

    test_id = sys.argv[1]
    
    for img_pk in ImageFile.objects.get_pks(test_id=test_id):
        
        # Fetch from pk to avoid db conflicts
        ImageFile.objects.get(pk=img_pk).do_processing()
    
    try:
        outfile = zipfile.ZipFile(f'demo/static/zip/{test_id}.zip', 'w')
        lookup = {'test_id': test_id, 'processed': True, 'error': False}

        for img_pk in ImageFile.objects.get_pks(**lookup):
            path = ImageFile.objects.get(pk=img_pk).out_path

            # Write any successfully processed files into the zip
            outfile.write(path, arcname=os.path.split(path)[1])
    except:
        try:
            outfile.close()
        except:
            pass

        os.remove(f'demo/static/zip/{test_id}.zip')