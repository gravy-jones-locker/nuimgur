from django.db import models
from demo import config
import dirconfig
import subprocess
import os
import time
import traceback as tb
import psutil

class CustomManager(models.Manager):

    def update_storage(self):

        """Clean the input/output files and db table to avoid breaching limit"""

        # Delete row/files for as long as count is over the limit set
        while self.count() >= config.FILE_LIMIT:
            self.first().full_delete()

    def check_status(self, test_id):

        """Check status of script associated with test_id"""

        proc = ManagedScript.objects.filter(test_id=test_id).first()
        if not proc:  # True if no process has even been started yet
            return 'waiting'

        try:  # Raises error if pid not found
            live_proc = psutil.Process(proc.pid)
        except:
            live_proc = None

        if live_proc and live_proc.status() != 'zombie':
            return 'live'  # True if script currently running

        proc.running = False
        proc.save()
        
        if not os.path.isfile(f'demo/static/zip/{test_id}.zip'):
            return 'error'  # True if not running but no output .zip
        else:
            return 'done'

    def get_pks(self, **filters):

        """Return the primary keys as a list with filters applied"""

        return self.filter(**filters).values_list('pk', flat=True)

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

        try:
            cmd = self.build_cmd()
            
            output = subprocess.check_output(cmd)
                    
            # Error marked if exact string found in stdout...
            if config.ERROR_STR in str(output):
                self.error = True   
        
        except:  # ...or if the process failed to start for some reason
            self.error = True
            print(tb.format_exc())

        self.processed = True         
        self.save()

    def full_delete(self):

        """Remove row entry and associated files"""

        if os.path.isfile(self.in_path):  # True if input file exists
            os.remove(self.in_file.path)
        
        if os.path.isfile(self.out_path):  # True if output file exists
            os.remove(self.out_path)

        # True if .zip associated to test_id (current batch) exists
        if os.path.isfile(f'demo/static/zip/{self.test_id}.zip'):
            os.remove(f'demo/static/zip/{self.test_id}.zip')

        self.delete()

    def store_info(self, test_id):

        """Stores image file info which doesn't fit in request"""

        self.in_path = self.in_file.path
        self.fname = os.path.split(self.in_path)[1]

        # This assumes files stored in /demo/static/[input;output]
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