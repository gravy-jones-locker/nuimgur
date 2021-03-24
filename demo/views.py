from django.shortcuts import render, redirect
from demo.forms import UploadFile
from django.contrib import messages
from demo.models import ImageFile
import traceback as tb
from urllib.parse import urlparse

# Create your views here.

def index(request, context={}):

    """Render homepage from template"""

    for msg in messages.get_messages(request):
        if msg.level != 20:
            continue
        
        fname = msg.message
        context = {'file': ImageFile.objects.get(fname=fname)}

    return render(request, 'index.html', context)

def upload_image(request):

    """Upload image file from local machine to static files"""

    try:
        ImageFile.objects.update_storage()

        form = UploadFile(request.POST, request.FILES)
        form.save()

        form.instance.do_processing()    
        messages.info(request, form.instance.fname)
    
    # If any errors are raised the user will see a message
    except:
        print(tb.format_exc())
        messages.error(request, 'There was an error processing the image')

    return redirect('/')

    