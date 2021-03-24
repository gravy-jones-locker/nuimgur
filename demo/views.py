from django.shortcuts import render, redirect
from demo.forms import UploadFile
from django.contrib import messages
from demo.models import ImageFile
import os
import runscripts
import traceback as tb
import time
from urllib.parse import urlparse

# Create your views here.

def index(request, context={}):

    """Render homepage from template"""

    test_id = request.GET.get('test_id') 

    if test_id:
        context = {'file': ImageFile.objects.filter(test_id=test_id).last(),
                   'status': ImageFile.objects.check_status(test_id)}

    return render(request, 'index.html', context)

def upload_image(request):

    """Upload image file from local machine to static files"""

    test_id = int(time.time())
    
    try:
        ImageFile.objects.update_storage()
        for upload_im in request.FILES.getlist('in_file'):
            
            form = UploadFile(request.POST, {'in_file': upload_im})
            form.save()

            form.instance.store_info(test_id)

        runscripts.start_script(test_id)
    
    # If any errors are raised the user will see a message
    except:
        print(tb.format_exc())
        messages.error(request, 'There was an error processing the image')
        return redirect(f'/')

    return redirect(f'/?test_id={test_id}')

    