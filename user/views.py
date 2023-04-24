import hashlib
import json
import subprocess
from virus_total_apis import PublicApi as VirusTotalPublicApi
from http.client import HTTPResponse
from django.shortcuts import render, redirect
from .forms import *
from email.parser import HeaderParser
import time
import dateutil.parser
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from datetime import datetime
import re
from xhtml2pdf import pisa
import Exif
from exif import Image
import exifread
from io import BytesIO
from .models import Case
import hashlib
from virus_total_apis import PublicApi as VirusTotalPublicApi



def dashboard(request):
    return render(request, "user/welcome.html")

# def search(request):

#     if request.method == "POST":
#         print("Entered search in view")
#         searchForm = CaseSearchForm(request.POST)
#         print("Seaarch Form", searchForm.is_valid())

#         if searchForm.is_valid():    
#             case_number = searchForm.cleaned_data["case_number"]
#             print("success in Search:",case_number)
#             return redirect("spoor", case_number)
#     else:
#         return render(request, "user/search.html",{"searchForm":CaseSearchForm()})
        
# def scan(request):
#     if request.method == "POST":
#         creationForm = CaseCreationForm(request.POST)
#         print("Creation Form", creationForm.is_valid())
#         searchForm= CaseSearchForm(request.POST)
#         print("Seaarch Form", searchForm.is_valid())
        
    
#         if creationForm.is_valid():
#             creationForm.save()
#             case_number = creationForm.cleaned_data["case_number"]
#             print("success in creation:",case_number)
#             return redirect("spoor", case_number)
#         elif not searchForm.is_valid() and not creationForm.is_valid():
#             if not creationForm.is_valid():
#                  return render(request, "user/scan.html", {
#                 "creationForm":creationForm, "searchForm":CaseSearchForm()})
#             elif not searchForm.is_valid():
#                  return render(request, "user/scan.html", {
#                 "creationForm":CaseCreationForm(), "searchForm":searchForm})
    
#     if request.method =='GET':
#         searchForm = CaseSearchForm()
#         creationForm = CaseCreationForm()
#         return render(request, "user/scan.html", {
#                 "creationForm":creationForm, "searchForm":searchForm})

def scan(request):
    if request.method=='POST':
        if 'form1_submit' in request.POST:
            creation_case_number = request.POST.get('creation_case_number')
            creation_domain = request.POST.get('creation_domain')
            creation_link = request.POST.get('creation_link')
            if Case.objects.filter(case_number=creation_case_number).exists():
                return render(request,'user/scan.html',{"error_message":"Case Number Already Exist"})
            else:
                creation_data = {
                'case_number': creation_case_number,
                'domain': creation_domain,
                'link':creation_link,
                }
                Case.objects.create(**creation_data)
                return redirect("spoor",creation_case_number)

        elif 'form2_submit' in request.POST:
            search_case_number = request.POST.get('search_case_number')
            if not Case.objects.filter(case_number=search_case_number).exists():
                return render(request,'user/scan.html',{"error_message":"Case Number Does Not Exist"})
            
            else:
                return redirect("spoor",search_case_number)
            
    return render(request, 'user/scan.html')


def spoor(request, case_number):
    case_obj = Case.objects.get(case_number=case_number)
    return render(request, "user/spoor.html", {
        "domain": str(case_obj.domain),
        "url": str(case_obj.link),
        "case_number": case_obj.case_number
    })


def dateParser(line):
    try:
        r = dateutil.parser.parse(line, fuzzy=True)
    except ValueError:
        r = re.findall('^(.*?)\s*(?:\(|utc)', line, re.I)
        if r:
            r = dateutil.parser.parse(r[0])
    return r


def utility_processor():
    def getCountryForIP(line):
        ipv4_address = re.compile(r"""
            \b((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.
            (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.
            (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.
            (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d))\b""", re.X)
        ip = ipv4_address.findall(line)
        if ip:
            ip = ip[0]  # take the 1st ip and ignore the rest
            if IP(ip).iptype() == 'PUBLIC':
                r = reader.country(ip).country
                if r.iso_code and r.name:
                    return {
                        'iso_code': r.iso_code.lower(),
                        'country_name': r.name
                    }
    return dict(country=getCountryForIP)


def getHeaderVal(h, data, rex='\s*(.*?)\n\S+:\s'):
    r = re.findall('%s:%s' % (h, rex), data, re.X | re.DOTALL | re.I)
    if r:
        return r[0].strip()
    else:
        return None


def email_header(header):
    mail_data = header
    r = {}
    n = HeaderParser().parsestr(mail_data)
    received = n.get_all('Received')
    if received:
        received = [i for i in received if ('from' in i or 'by' in i)]
    else:
        received = re.findall(
            'Received:\s*(.*?)\n\S+:\s+', mail_data, re.X | re.DOTALL | re.I)
    c = len(received)
    for i in range(len(received)):
        if ';' in received[i]:
            line = received[i].split(';')
        else:
            line = received[i].split('\r\n')
        line = list(map(str.strip, line))
        line = [x.replace('\r\n', ' ') for x in line]
        try:
            if ';' in received[i + 1]:
                next_line = received[i + 1].split(';')
            else:
                next_line = received[i + 1].split('\r\n')
            next_line = list(map(str.strip, next_line))
            next_line = [x.replace('\r\n', '') for x in next_line]
        except IndexError:
            next_line = None

        if line[0].startswith('from'):
            data = re.findall(
                """
                from\s+
                (.*?)\s+
                by(.*?)
                (?:
                    (?:with|via)
                    (.*?)
                    (?:\sid\s|$)
                    |\sid\s|$
                )""", line[0], re.DOTALL | re.X)
        else:
            data = re.findall(
                """
                ()by
                (.*?)
                (?:
                    (?:with|via)
                    (.*?)
                    (?:\sid\s|$)
                    |\sid\s
                )""", line[0], re.DOTALL | re.X)

    summary = {
        'From': n.get('From') or getHeaderVal('from', mail_data),
        'To': n.get('to') or getHeaderVal('to', mail_data),
        'Cc': n.get('cc') or getHeaderVal('cc', mail_data),
        'Subject': n.get('Subject') or getHeaderVal('Subject', mail_data),
        'MessageID': n.get('Message-ID') or getHeaderVal('Message-ID', mail_data),
        'Date': n.get('Date') or getHeaderVal('Date', mail_data),
    }
    # ips = set(re.findall( r'[0-9]+(?:\.[0-9]+){3}', mail_data ))
    ips = set(re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', mail_data))
    emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", mail_data)
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    urls = re.findall(regex, mail_data)

    security_headers = ['Received-SPF', 'Authentication-Results',
                        'DKIM-Signature', 'ARC-Authentication-Results']

    data = {
        "ips": ips,
        "emails": emails,
        "urls": urls,
        "security_headers": security_headers,
        "summary": summary,
        "n": n
    }
    return data


def analyse_header(request):
    if request.method == "POST":
        header = request.POST.get("header")
        data = email_header(header)
        # print("asdfasdfasdf",type(data["n"]))
        request.session['emailheader'] = header
        return render(request, "user/analyse_header.html", {
            "header" : header,
            "summary": data["summary"],
            "ips": data["ips"],
            "urls": data["urls"],
            "emails": set(data["emails"]),
            "is_true": True

        })

    return render(request, "user/analyse_header.html")


def malware_analysis(request):
    if request.method == "POST":
        print(request.FILES)
        form = MalwareUploadForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            case_number = form.cleaned_data.get("case_number")
            file = form.cleaned_data.get("malware_file")
            # case_obj = Case.objects.get_or_create(case_number=case_number)
            mal_obj = MalwareFile.objects.create(case_number=case_number, malware_file=file)
            print(mal_obj.malware_file.path)
            mal_obj.save()
            file_type_output = subprocess.run(["/home/falcon/Desktop/Git Repo/Final-Year-Project/Feb/Spoor/user/filetype.sh", mal_obj.malware_file.path], capture_output=True)
            file_type_output = file_type_output.stdout
            file_type_output = file_type_output.decode('ascii')

            hashing_output = subprocess.run(["/home/falcon/Desktop/Git Repo/Final-Year-Project/Feb/Spoor/user/hashing.sh", mal_obj.malware_file.path], capture_output=True)
            hashing_output = hashing_output.stdout
            hashing_output = hashing_output.decode('ascii')

            hash_ = hashing_output[10:51]

            
            API_KEY = "b47c1974a73b366eb24810ab6b2855e10ab86a022c311f891bf1ec5bf9d83a24"
            
            EICAR = hash_.encode('utf-8')
            EICAR_SHA256 = hashlib.sha256(EICAR).hexdigest()
            vt = VirusTotalPublicApi(API_KEY)

            response = vt.get_file_report(EICAR_SHA256)
            virus_total = json.dumps(response, sort_keys=False, indent=4)
            form = MalwareUploadForm()
            return render(request, "user/malware_analysis.html", {
                "form": form, "file_type_output": file_type_output, "hashing_output": hashing_output, "is_true": True, "virus_total": virus_total
            })

    form = MalwareUploadForm()

    return render(request, "user/malware_analysis.html", {
        "form": form
    })


def get_gps_from_image(uploaded_file):
    gps = {}
    tags = exifread.process_file(uploaded_file, details=False)
    for tag in tags.keys():
        if tag.startswith('GPS'):
            gps_key = 'GPS' + tag[3:]
            gps[gps_key] = str(tags[tag])
    return gps



def image_analysis(request):
    if request.method == "POST":
        print(request.FILES)
        form = ImageUploadForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            
            imagename = form.cleaned_data.get("image_file")
            exif_data = Exif.get_exif_for_file(imagename)
            # exif_data = Exif.get_exif(imagename)
            # print(type(exif_data))
            # print(exif_data)
            
            uploaded_file = form.cleaned_data.get("image_file")
            gps = get_gps_from_image(uploaded_file)
            print(gps)
            latitude = gps.get('GPS GPSLatitude')
            latitude_ref = gps.get('GPS GPSLatitudeRef')
            print(latitude)
            print(latitude_ref)

            longitude = gps.get('GPS GPSLongitude')
            longitude_ref = gps.get('GPS GPSLongitudeRef')
            print(longitude)
            print(type(longitude))
            print(longitude_ref)


            lat_degrees, lat_minutes, lat_seconds = eval(latitude)
            lon_degrees, lon_minutes, lon_seconds = eval(longitude)

            print(lat_degrees)
            print(lat_minutes)
            print(lat_seconds)
            latitude = lat_degrees + (lat_minutes / 60) + (lat_seconds / 3600)
            longitude = lon_degrees + (lon_minutes / 60) + (lon_seconds / 3600)

            latitude_ref = 'N' if lat_degrees >= 0 else 'S'
            longitude_ref = 'E' if lon_degrees >= 0 else 'W'

            google_maps_link = f'https://www.google.com/maps/place/{abs(latitude)}{latitude_ref},{abs(longitude)}{longitude_ref}'
            print(google_maps_link)        

            exif_data['map_link']=google_maps_link
            exif_data['latitude']= str(latitude) +' '+ latitude_ref
            exif_data['longitude']=str(longitude) +' '+ longitude_ref
            exif_data['is_true'] = True

            # exif_dict = {"Name: ", exif_data['FileName'], "DateTime: ", exif_data['DateTime'],
            #              "Make: ", exif_data['Make'], "GPSInfo: ", exif_data['GPSInfo'],
            #              "ImageHeight: ", exif_data['ImageHeight'], "ImageWidth: ", exif_data['ImageWidth'],
            #              "ImageFormat: ", exif_data['ImageFormat'], "IsAnimated: ", exif_data['IsAnimated'],
            #              "map_link: ",str(map_link)
            #              }

            # print(exif_dict)

            return render(request, "user/image_analysis.html", {'exif_data': exif_data})
    form = ImageUploadForm()

    return render(request, "user/image_analysis.html", {
        "form": form
    })


def GenerateReport(request): #Email render
    # case_number = request.GET.get("case_number", None)
    print("check")

    # if request.method == "POST":
    header = request.session['emailheader']
    data = email_header(header)
    emaildata = { 
            "summary": data["summary"],
            "ips": data["ips"],
            "urls": data["urls"],
            "emails": set(data["emails"]),
            "is_true": True,
            }
    pdf = render_to_pdf('user/email_analysis_report.html', emaildata)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Email_Report.pdf"
        content = "inline; filename='%s'" % (filename)
        content = "attachment; filename=%s" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1", 'ignore')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
