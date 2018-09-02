# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import requests
import os
from shutil import make_archive, copytree
from jinja2 import Environment, FileSystemLoader

def free_proxy():
    """ Thay đổi địa chỉ ip bằng proxy"""
    url = "https://free-proxy-list.net"
    res = requests.get(url)
    parser = BeautifulSoup(res.text, "html.parser")
    proxies = set()
    for i in parser.select("#proxylisttable > tbody > tr"):
        if (i.select('td')[6].contents[0]) == "yes":
            proxies.add((i.select('td')[0].contents[0]) + ":" + (i.select('td')[1].contents[0]))
    print("Lay proxy thanh cong! ")
    return proxies

def beauti(url, proxies={"http": "81.23.118.106:21231", "https": "81.23.118.106:21231"}):
    """ Tạo requests đến trang đích """
    res = requests.get(url)
    return res
def directory(url):
    return url[42:-13:]

def link_chapter(url):
    """ Lấy link chapter của mỗi truyện """
    res = beauti(url)
    parser = BeautifulSoup(res.text, "html.parser")
    links = parser.find_all("div", class_="right_menu_item")
    print(" Dang lay link chapter ! ")
    list_link = []
    title = parser.title.text
    info = re.split("-|~", title)
    list_link.append(info[0])
    list_link.append(info[1])
    for link in links:
        list_link.append(("https://isach.info/mobile/" + link.a["href"], link.text))
    

    
    return list_link


def noidung_chapter(folder, link_chapters):
    content_chapter = None
    i = 1
    top = """<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><title>Cho Tôi Xin Một Vé Ði Tuổi Thơ</title>
<link href="../css/motsach.css" rel="stylesheet" type="text/css" />
</head>
<body>"""
    bot = """</body>
</html>"""
    for link in link_chapters[2::]:
        source = beauti(link[0]).content.decode("utf-8")
        content_chapter = re.search(r"<div class='ms_chapter'>(.|\n)*<!-- chapter navigator -->", source).group(0)
        
        wFile(top +content_chapter + bot, folder + "/OEBPS/text/" + str(i)+ ".html")
        i += 1
def cover(url):
    name = directory(url)
    res = requests.get("https://isach.info/images/story/cover/"+name +".jpg")
    with open(name + "/OEBPS/images/cover.jpg", "wb") as f:
        f.write(res.content)
        f.close()

def wFile(docs, name):
    """ghi nội dung vào file"""
    with open(name, "w", encoding="utf-8") as f:
        f.write(docs)
        print("Ghi thanh cong!")
        f.close()



def jinjaepub(file_name, *args, **kwargs):
    file_loader = FileSystemLoader("./template")
    env = Environment(loader=file_loader)
    template = env.get_template(file_name)
    output = template.render(kwargs)
    return output

if __name__ == "__main__":
    url = "https://isach.info/mobile/story.php?story=10_van_cau_hoi_vi_sao_hoa_hoc__nguyen_van_mau&chapter=0000"
    folder = directory(url)
    link_chapters = link_chapter(url)
    try:
        copytree("data", folder)
    except:
        pass

    temp = ["content.opf", "toc.ncx", "title.html", "cover.html"]
    for i in temp:
        view = jinjaepub(i , info = link_chapters)
        wFile(view, folder + "/OEBPS/" + i)
    cover(url)
    noidung_chapter(folder, link_chapters)
    make_archive(folder, "zip", folder)
    os.rename(folder + ".zip", folder +".epub")
    print("done !")
    