from django.shortcuts import render, redirect
from demo.forms import UploadFile
from django.contrib import messages
from demo.models import ImageFile

# Create your views here.

def index(request, context={}):

    """Render homepage from template"""

    for msg in messages.get_messages(request):
        if msg.level != 20:
            continue
        
        fname = msg.message
        context = {'file': ImageFile.objects.get(pk=fname)}

    return render(request, 'index.html', context)

def upload_image(request):

    """Upload image file from local machine to static files"""

    try:
        fname = str(request.FILES['in_file']).replace(' ', '_')
        ImageFile.objects.update_storage(fname)

        form = UploadFile({**{'fname': fname}, **request.POST}, request.FILES)
        form.save()

        form.instance.do_processing()    
        messages.info(request, fname)
    
    # If any errors are raised the user will see a message
    except:
        messages.error(request, 'There was an error processing the image')

    return redirect('/')

    