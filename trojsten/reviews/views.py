import os.path
import zipfile
import io
import re
from time import time

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from sendfile import sendfile

from trojsten.regal.tasks.models  import Task, Submit
from trojsten.regal.people.models import User
from trojsten.submit.helpers import save_file, get_path

from trojsten.reviews.helpers import submit_review, submit_readable_name, get_latest_submits_by_task
from trojsten.reviews.forms import ReviewForm, get_zip_form_set

file_re = re.compile (r"(?P<lastname>[^_]*)_(?P<submit_pk>[0-9]+)_(?P<filename>.+\.[^.]+)")

def review_task_view (request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    max_points = task.description_points
    users = get_latest_submits_by_task(task)
    choices = [(None, "Auto / all")] + [(user.pk, user.username) for user in users]

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, choices=choices, max_value=max_points)

        if form.is_valid():
            user = form.cleaned_data["user"]
            filecontent = request.FILES["file"]
            filename = form.cleaned_data["file"].name
            points = form.cleaned_data["points"]

            if user == "None" and filename.endswith(".zip"):
                path = os.path.join(settings.SUBMIT_PATH, "reviews", "%s_%s.zip" % (int(time()), request.user.pk))
                save_file(filecontent, path)

                request.session["review_archive"] = path
                return redirect ("admin:review_submit_zip", task.pk)


            filematch = file_re.match (filename)
            
            if filematch:
                filename = filematch.groupdict()["filename"]

            if user == "None":
                if not filematch: 
                    messages.add_message(request, messages.ERROR, "Unknown target")
                    return redirect("admin:review_task", task.pk)

                try:
                    user = Submit.objects.get(pk=int(filematch["submit_pk"])).user
                
                except Submit.DoesNotExist:
                    messages.add_message(request, messages.ERROR, "Unknown target")
                    return redirect("admin:review_task", task.pk)
            else:
                try:
                    user = User.objects.get(pk=int(user))
                
                except User.DoesNotExist:
                    messages.add_message(request, messages.ERROR, "User does not exists")
                    return redirect("admin:review_task", task.pk)

            submit_review(filecontent, filename, task, user, points)
            messages.add_message(request, messages.SUCCESS, "Uploaded file %s to %s" % (filename, user.last_name))

            return redirect("admin:review_task", task.pk)

    template_data = {
        "task": task,
        "users": users,
        "form" : ReviewForm(choices=choices, max_value=max_points),
    }

    return render (
        request, "admin/review_form.html", template_data
    )


def submit_download_view (request, submit_pk):
    submit = get_object_or_404(Submit, pk=submit_pk)
    name = submit_readable_name(submit)

    return sendfile(request, submit.filepath, attachment=True, attachment_filename=name)


def download_latest_submits_view (request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    data = [data["description"] for data in get_latest_submits_by_task(task).values()]

    path = os.path.join(settings.SUBMIT_PATH, "reviews")
    if not os.path.isdir (path):
        os.makedirs(path)
        fd = os.open(path, os.O_RDONLY)
        os.fchmod(fd, 0777)
        os.close(fd)

    path = os.path.join(path, "Uloha %s-%s-%s.zip" %(task.name, int(time()), request.user))

    zipper = zipfile.ZipFile(path, "w")
    for submit in data:
        zipper.write(submit.filepath, submit_readable_name(submit))

    zipper.close()
    
    return sendfile(request, path, attachment=True)


def zip_upload (request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    name = request.session.get("review_archive", None)
    try:
        data = zipfile.ZipFile(name)

    except (zipfile.BadZipfile, IOError):
        messages.add_message(request, messages.ERROR, "Problems with uploaded zip")
        return redirect ("admin:review_task", task.pk)

    users = [(None, "")] +  [(user.pk, user.username) for user in get_latest_submits_by_task(task)]
    initial =   [{
                    "filename": file, 
                } 
                for file in data.namelist()] 

    for form_data in initial:
        match = file_re.match(form_data["filename"])
        if not match: continue

        pk = match.groupdict()["submit_pk"]
        try:
            form_data["user"] = Submit.objects.get(pk=pk).user.pk
        
        except Submit.DoesNotExist:
            pass 

    ZipFormSet = get_zip_form_set (users, task.description_points, extra=0)
    formset = ZipFormSet (initial=initial)

    if request.method == "POST":
        formset = ZipFormSet (request.POST)
        
        if formset.is_valid():
            names = data.namelist()
            valid = True

            for form in formset:
                user = form.cleaned_data["user"]
                filename = form.cleaned_data["filename"]
                points = form.cleaned_data["points"]

                if user == "None": continue
                
                if not filename in names:
                    err = "Invalid filename %s" % filename
                    form._errors["__all__"] = form.error_class([err])
                    
                    valid = False
                    continue

                user = User.objects.get(pk=int(user))
                submit_review (data.read(filename), os.path.split(filename)[1], task, user, points)

            
            if valid: return redirect("admin:review_task", task.pk)
        
        for form in formset:
            form.name = form.cleaned_data["filename"]

    template_data = {
        "formset": formset,
        "task": task
    } 
    return render (
        request, "admin/zip_upload.html", template_data
    )
