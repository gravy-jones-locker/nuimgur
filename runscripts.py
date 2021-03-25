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

def make_zip(outfile, test_id):

    """Compile all successfully processed files into a zip archive"""

    lookup = {'test_id': test_id, 'processed': True, 'error': False}
    
    img_pks = ImageFile.objects.get_pks(**lookup)
    assert len(img_pks) > 0

    for img_pk in img_pks:
        path = ImageFile.objects.get(pk=img_pk).out_path

        # Write any successfully processed files into the zip
        outfile.write(path, arcname=os.path.split(path)[1])

if __name__ == '__main__':
    
    from demo.models import ImageFile

    test_id = sys.argv[1]

    time.sleep(5)  # Wait to allow for user pageload
    
    for img_pk in ImageFile.objects.get_pks(test_id=test_id):
        
        # Fetch from pk to avoid db conflicts
        ImageFile.objects.get(pk=img_pk).do_processing()
    
    try:
        outfile = zipfile.ZipFile(f'demo/static/zip/{test_id}.zip', 'w')
        make_zip(outfile, test_id)
    except:
        try:
            outfile.close()
        except:
            pass

        os.remove(f'demo/static/zip/{test_id}.zip')