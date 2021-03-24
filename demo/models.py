from django.db import models
from demo import config
import dirconfig
import subprocess
import os
import time

class CustomManager(models.Manager):

    def update_storage(self):

        """Overwrite existing file and set to limit"""

        if self.count() >= config.FILE_LIMIT:
            self.first().full_delete()  # The first row is the oldest

class ImageFile(models.Model):

    objects = CustomManager()

    in_file = models.ImageField(upload_to='demo/static/input/')
    fname = models.CharField(max_length=255, default='')

    binned = models.BooleanField(default=False)
    gain = models.FloatField(default=config.GAIN_DEFAULT)

    def do_processing(self):

        """Run processing commands on input image"""

        self.fname = os.path.split(self.in_file.path)[1]
        self.save() 

        cmd = [x.replace('[file_name]', self.fname) for x in dirconfig.CMD] 

        r = subprocess.run(cmd, timeout=config.TIMEOUT)

    def full_delete(self):

        """Remove row entry and associated files"""

        if os.path.isfile(self.in_file.path):
            
            os.remove(self.in_file.path)
            os.remove(self.in_file.path.replace('input', 'output'))

        self.delete()