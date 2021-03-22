import sys
import os
import shutil
import time

in_path = sys.argv[1]
out_path = sys.argv[2]

shutil.copy(in_path, out_path)