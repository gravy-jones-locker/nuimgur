from django.db import models
from demo import config
import dirconfig
import subprocess
import os
import time
import psutil

class CustomManager(models.Manager):

    def update_storage(self):

        """Overwrite existing file and set to limit"""

        while self.count() >= config.FILE_LIMIT:
            self.first().full_delete()  # The first row is the oldest

    def full_delete(self):

        """Remove all existing records/files"""

        for row in self.all():
            row.full_delete()

    def get_pks(self, **filters):

        """Return the primary keys as a list with filters applied"""

        return self.filter(**filters).values_list('pk', flat=True)

    def check_status(self, test_id):

        """Check that the script is still running and a zip has been made"""

        proc = ManagedScript.objects.filter(test_id=test_id).first()
        if not proc:
            return 'dead'

        if proc.pid in [p.pid for p in psutil.process_iter()]:
            return 'live'

        proc.running = False
        proc.save()
        
        if not os.path.isfile(f'demo/static/zip/{test_id}.zip'):
            return 'error'
        else:
            return 'done'

class ImageFile(models.Model):

    objects = CustomManager()

    in_file = models.FileField(upload_to='demo/static/input/')
    
    fname = models.CharField(max_length=255, default='')

    in_path = models.CharField(max_length=255, default='')
    out_path = models.CharField(max_length=255, default='')

    binned = models.BooleanField(default=False)
    gain = models.FloatField()

    test_id = models.IntegerField(null=True, blank=True, default=None)
    processed = models.BooleanField(default=False)
    error = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def do_processing(self):

        """Run processing commands on input image"""

        cmd = self.build_cmd()
        output = subprocess.check_output(cmd)

        self.processed = True
            
        # Error only marked if exact string found in stdout
        if config.ERROR_STR in str(output):
            self.error = True            
    
        self.save()

    def full_delete(self):

        """Remove row entry and associated files"""

        if os.path.isfile(self.in_path):
            os.remove(self.in_file.path)
        
        if os.path.isfile(self.out_path): 
            os.remove(self.out_path)

        if os.path.isfile(f'demo/static/zip/{self.test_id}.zip'):
            os.remove(f'demo/static/zip/{self.test_id}.zip')

        self.delete()

    def store_info(self, test_id):

        """Stores image file info which doesn't fit in request"""

        self.in_path = self.in_file.path
        self.fname = f'{test_id}_{os.path.split(self.in_path)[1]}'

        self.out_path = self.in_path.replace('input', 'output')
        
        self.test_id = test_id

        self.save()

    def build_cmd(self):

        """Replace path elements in processing command with file specifics"""

        cmd = ','.join(config.CMD)

        for var in ['in_path', 'out_path', 'binned', 'gain']:
            cmd = cmd.replace(f'[{var}]', str(getattr(self, var)))
        
        return cmd.split(',')

class ManagedScript(models.Model):

    objects = CustomManager()

    pid = models.IntegerField()
    test_id = models.IntegerField()

    running = models.BooleanField(default=False)