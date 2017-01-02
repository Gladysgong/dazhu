# coding:utf-8
from django.shortcuts import render
from django.template import loader, Context
from django.http import HttpResponse
from models import Photoes
from urllib import quote
import datetime
import dazhu
import tools.webTools as tools
from django.views.decorators.csrf import csrf_exempt
import account.secu as secu
try:
    import Image
except:
    from PIL import Image
import os
import random
from twisted.python.filepath import FilePath
from django.views.generic.base import TemplateView
import json
import album


def getAlbum(pages,is_login):
    pageCount = 12
    tools.debug("islogin",is_login)
    pages = int(pages)
    
    allCounts = Photoes.objects.count()
    allPages = allCounts // pageCount + 1
    posts = None
    if is_login:
        posts = Photoes.objects.all().order_by("-timestamp")[(pages - 1) * pageCount:pages * pageCount]
    else:
        posts = Photoes.objects.filter(phototype='public').order_by("-timestamp")[(pages - 1) * pageCount:pages * pageCount]
    
    return posts,allPages

class index(TemplateView):    
    template_name = "album/index.html" 
    def get_context_data(self, **kwargs):
        context = super(index, self).get_context_data(**kwargs)
        pages = 1
        try:
            pages = self.args[0]
        except:
            pass
        pages = int(pages)        
        posts = getAlbum(pages,self.request.user.is_authenticated())[0]
        
        context['posts'] = posts
        context['title'] = u'相册'
        
        return context
    
class show(TemplateView):
    template_name = "album/show.html" 
    def get_context_data(self, **kwargs):
        context = super(show, self).get_context_data(**kwargs)
        inputName = None
        try:
            inputName = self.args[0]
        except:
            pass
        pic = Photoes.objects.get(rndName = inputName)
        
        context['pic'] = pic
        context['title'] = pic.showName
        next = Photoes()
        next.rndName = "nomore"
        next.showName = "no more..."
        try:
            if self.request.user.is_authenticated():
                next = Photoes.objects.filter(timestamp__lt=pic.timestamp).order_by("-timestamp")[0]
            else:
                next = Photoes.objects.filter(phototype='public').filter(timestamp__lt=pic.timestamp).order_by("-timestamp")[0]
        except Exception as error:
            tools.debug("next find fail",error)
            pass
        context['next']=next
        return context

def ajaxGetAlbum(request,pages):
    tools.debug("ajax get posts ",pages)
    try:
        pages=int(pages)
    except:
        pages = 1
    
    pagesInfo = getAlbum(pages,request.user.is_authenticated())
    posts = pagesInfo[0]
    allpages = pagesInfo[1]
    
    if allpages < pages:
        tools.debug("allpages < pages ",allpages,pages)
        return HttpResponse()    
    
    result = []
    for item in posts:
        result.append({'rndName':item.rndName,'showName':item.showName,})
    
    return HttpResponse(json.dumps(result, ensure_ascii=False))

def ajaxGetFirst6Album(request):
    pages = 1
    
    pagesInfo = getAlbum(pages,request.user.is_authenticated())
    posts = pagesInfo[0]
    allpages = pagesInfo[1]
    
    if allpages < pages:
        tools.debug("allpages < pages ",allpages,pages)
        return HttpResponse()    
    
    result = []
    i = 0
    for item in posts:
        i+=1
        if i==7:
            break
        result.append({'rndName':item.rndName,'showName':item.showName,})
    
    return HttpResponse(json.dumps(result, ensure_ascii=False))


@csrf_exempt
@secu.login_filter
def upload(request):
    """ 上传文件 """  
    source_filename = request.POST.get('name', '')    
    tools.debug(source_filename)  
    # print("request aid is ",request.POST['aid'])
    fileObj = request.FILES.get('file')
    tools.debug(fileObj)  
    
    response = HttpResponse()  
    
    if fileObj: 
        filename = quote(fileObj.name.encode("utf8"))
        fileExt = ""
        fileInfo = []
        if "." in filename:            
            fileInfo = filename.split('.')
            fileExt = fileInfo[len(fileInfo) - 1]
            fileExt = '.' + fileExt
            tools.debug("fileext is " + fileExt)
            
        def convert_name_html_valid(input_name):
            file_name = os.path.split(input_name)
            file_name_arr = os.path.splitext(file_name[1])
            quote_name_arr = [x for x in file_name_arr]
            quote_name_arr[0] = "%s_%s" % (quote_name_arr[0], random.randint(1, 99))
            return quote_name_arr

        file_name = convert_name_html_valid(filename)[0]
        tools.debug("文件名",file_name)
        
        album_folder = dazhu.settings.BASE_DIR + "/dazhu/static/album/"
        if not os.path.exists(album_folder):
            os.makedirs(album_folder)
            
        mini_folder = album_folder + "mini/"
        if not os.path.exists(mini_folder):
            os.makedirs(mini_folder)
            
        normal_folder = album_folder + "normal/"
        if not os.path.exists(normal_folder):
            os.makedirs(normal_folder)
        
        fileData = tools.readFile(dazhu.settings.BASE_DIR + "/dazhu/static/ueditor/net/config.json")
        allowExt = None
        configJson = json.loads(fileData)
        try:
            allowExt = configJson["imageManagerAllowFiles"]
        except Exception as errors:
            tools.debug("json load file types error")
            tools.debug(errors)
            return response
        
        if allowExt == None:
            tools.debug("不能获取 file types")
            return response
    
        
        if fileExt.lower() in allowExt:
            file_path = normal_folder + file_name + "tmp" + fileExt
            mini_path = mini_folder + file_name + fileExt
            normal_path = normal_folder + file_name + fileExt
            
            try:
                with open(file_path, 'wb+') as f:
                    for chunk in fileObj.chunks():
                        f.write(chunk)
                #make normal pic
                im = Image.open(file_path)

                width = im.size[0]
                height = im.size[1]
                if width > 2048 or height > 2048:
                    im.thumbnail((2048, 2048))
                im.save(normal_path)

                # make small pic            
                im = Image.open(file_path)
                im.thumbnail((180, 180))

                #如果宽大于高
                width = im.size[0]
                height = im.size[1]
                if height // width > 90 // 120:
                    #height 高了。以width为准 切height
                    curHeight = width * 90 // 120
                    dx = height - curHeight
                    box = (0, dx / 2, width, curHeight + dx / 2)
                    im = im.crop(box)
                else:
                    #width 大了，以height为准，切width
                    curwidth = height * 120 // 90
                    dx = width - curwidth
                    box = (dx / 2, 0, curwidth + dx / 2, height)
                    im = im.crop(box)

                im.save(mini_path)

                if os.path.isfile(file_path):
                    os.remove(file_path)

                tempPhoto = Photoes()
                tempPhoto.rndName = file_name + fileExt
                tempPhoto.showName = source_filename
                tempPhoto.timestamp = datetime.datetime.now()
                tempPhoto.phototype = 'private'
                tempPhoto.save()
            except Exception as errors:
                tools.debug("upload album error",errors)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                if os.path.isfile(mini_path):
                    os.remove(mini_path)
                if os.path.isfile(normal_path):
                    os.remove(normal_path)

            
    return response

import xml.dom.minidom as dom
import os
def recover(request):
    # xmldoc = dom.parse(dazhu.settings.BASE_DIR +'/photoes.xml')
    # itemlist = xmldoc.getElementsByTagName('photo')
    # result = "over"
    # tools.debug("start import")
    # for item in itemlist:
    #     tempguid = item.attributes['id'].value
    #     tools.debug("current id is ",tempguid)
    #     try:
    #         tempphoto = Photoes.objects.get(id=tempguid)
    #     except:
    #         tools.debug(tempguid,"tempguid is exist")
    #         result += tempguid + " imported <br>"
    #         tempphoto = Photoes()
    #         tempphoto.id = item.attributes["id"].value
    #         tempphoto.category = item.attributes["category"].value
    #         tempphoto.rndName = item.attributes["rndName"].value
    #         tempphoto.showName = item.attributes["sourceName"].value
    #
    #         tempphoto.timestamp = datetime.datetime.strptime(item.attributes["timestamp"].value, "%Y%m%d %H%M%S")
    #
    #         tempphoto.save()
    # tempphoto = Photoes.objects.all()
    # for item in tempphoto:
    #     item.phototype = "private"
    #     item.save()
    return HttpResponse()




