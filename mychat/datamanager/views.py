import os
import json
import uuid
import csv
import shutil
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from datamanager.models import FileInfo
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from app.chat.spl import text_to_xml, extract_text_from_pdf, extract_text_from_word

def upload_file(request):
    media_path = os.path.join(settings.MEDIA_ROOT)
    selected_directory = request.POST.get('directory', '')
    selected_directory_path = os.path.join(media_path, selected_directory)

    if request.method == 'POST':
        if 'folder' in request.FILES:
            folder_name = request.POST.get('folder_name')
            destination_directory = os.path.join(selected_directory_path, folder_name)
            if os.path.exists(destination_directory):
                messages.info(request, f'Thư mục \'{folder_name}\' đã tồn tại')
            else:
                os.makedirs(destination_directory, exist_ok=True)

            for subfile in request.FILES.getlist('folder'):
                subfile_path = os.path.join(destination_directory, subfile.name)
                if subfile.name.endswith('.pdf'):
                    with open(subfile_path, 'wb') as destination:
                        for chunk in subfile.chunks():
                            destination.write(chunk)
                    text = extract_text_from_pdf(subfile_path)
                elif subfile.name.endswith('.doc') or subfile.name.endswith('.docx'):
                    with open(subfile_path, 'wb') as destination:
                        for chunk in subfile.chunks():
                            destination.write(chunk)
                    text = extract_text_from_word(subfile_path)
                else:
                    text = ''
                    for chunk in subfile.chunks():
                        text += chunk.decode('utf-8')

                xml_path = subfile_path.split('.')[0] + ".xml"
                text_to_xml(text, xml_path)
        else:
            files = request.FILES.getlist('files[]')
            for uploaded_file in files:
                file_path = os.path.join(selected_directory_path, uploaded_file.name)
                with open(file_path, 'wb') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                if uploaded_file.name.endswith('.pdf'):
                    text = extract_text_from_pdf(file_path)
                elif uploaded_file.name.endswith('.doc') or uploaded_file.name.endswith('.docx'):
                    text = extract_text_from_word(file_path)
                else:
                    text = ''
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()

                xml_path = file_path.split('.')[0] + ".xml"
                text_to_xml(text, xml_path)

    return redirect(request.META.get('HTTP_REFERER'))

def create_folder(request):
    if request.method == 'POST':
        new_folder_name = request.POST.get('new_folder_name')
        selected_directory = request.POST.get('directory', '')
        selected_directory_path = os.path.join(settings.MEDIA_ROOT, selected_directory)
        new_folder_path = os.path.join(selected_directory_path, new_folder_name)

        if os.path.exists(new_folder_path):
            messages.info(request, f'Thư mục \'{new_folder_name}\' đã tồn tại')
        else:
            os.makedirs(new_folder_path)

    return redirect(request.META.get('HTTP_REFERER'))

def rename_folder(request):
    if request.method == 'POST':
        old_name = request.POST.get('old_name')
        new_name = request.POST.get('new_name')
        old_path = os.path.join(settings.MEDIA_ROOT, old_name)
        new_path = os.path.join(settings.MEDIA_ROOT, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
    return redirect(request.META.get('HTTP_REFERER'))

def delete_folder(request, folder_path):
    path = folder_path.replace('%slash%', '/')
    absolute_folder_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(absolute_folder_path):
        shutil.rmtree(absolute_folder_path)
    return redirect(request.META.get('HTTP_REFERER'))

def index(request):
    context = {}
    return render(request, 'pages/dashboard.html', context=context)

def convert_csv_to_text(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
    text = ''
    for row in rows:
        text += ','.join(row) + '\n'
    return text

def get_files_from_directory(directory_path):
    files = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            try:
                _, extension = os.path.splitext(filename)
                if extension.lower() == '.csv':
                    csv_text = convert_csv_to_text(file_path)
                else:
                    csv_text = ''
                files.append({
                    'file': file_path.split(os.sep + 'database' + os.sep)[1],
                    'filename': filename,
                    'file_path': file_path,
                    'csv_text': csv_text
                })
            except Exception as e:
                print(str(e))
    return files

def save_info(request, file_path):
    path = file_path.replace('%slash%', '/')
    if request.method == 'POST':
        FileInfo.objects.update_or_create(
            path=path,
            defaults={'info': request.POST.get('info')}
        )
    return redirect(request.META.get('HTTP_REFERER'))

def get_breadcrumbs(request):
    path_components = [component for component in request.path.split("/") if component]
    breadcrumbs = []
    url = ''
    for component in path_components:
        url += f'/{component}'
        if component == "file-manager":
            component = "database"
        breadcrumbs.append({'name': component, 'url': url})
    return breadcrumbs

def file_manager(request, directory=''):
    if not request.user.is_superuser:
        return redirect('/admin/')
    media_path = os.path.join(settings.MEDIA_ROOT)
    directories = generate_nested_directory(media_path, media_path)
    selected_directory = directory

    files = []
    selected_directory_path = os.path.join(media_path, selected_directory)
    if os.path.isdir(selected_directory_path):
        files = get_files_from_directory(selected_directory_path)

    breadcrumbs = get_breadcrumbs(request)

    # Pagination logic
    paginator = Paginator(files, 25)  # Show 25 files per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'directories': directories,
        'files': page_obj.object_list,
        'selected_directory': selected_directory,
        'segment': 'file_manager',
        'breadcrumbs': breadcrumbs,
        'page_obj': page_obj,  # Added for pagination
        'total_files': len(files)  # Total file count
    }
    return render(request, 'pages/file-manager.html', context)

def generate_nested_directory(root_path, current_path):
    directories = []
    for name in os.listdir(current_path):
        if os.path.isdir(os.path.join(current_path, name)):
            unique_id = str(uuid.uuid4())
            nested_path = os.path.join(current_path, name)
            nested_directories = generate_nested_directory(root_path, nested_path)
            directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path), 'directories': nested_directories})
    return directories

def delete_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    os.remove(absolute_file_path)
    return redirect(request.META.get('HTTP_REFERER'))

def download_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(absolute_file_path):
        with open(absolute_file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(absolute_file_path)
            return response
    raise Http404

def fetch_data(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        start_page = int(request.POST.get('start_page', 1))
        progress_var = start_processing(url, start_page)
        return JsonResponse({'status': 'seccess', 'message': progress_var})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
