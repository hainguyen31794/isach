# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import requests
import os
from shutil import make_archive, copytree
from jinja2 import Environment, FileSystemLoader
from itertools import cycle

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
    print(proxies)
    return proxies

def beauti(url, proxies={"http": "167.99.28.59:8080", "https": "167.99.28.59:8080"}):
    """ Tạo requests đến trang đích """
    res = requests.get(url, proxies=proxies)
    parser = BeautifulSoup(res.text, "html.parser")
    return parser


def link_chapter(url):
    """ Lấy link chapter của mỗi truyện """
    parser = beauti(url)
    links = parser.find_all("div", class_="right_menu_item")
    print(" Dang lay link chapter ! ")
    for link in links:
        yield ("https://isach.info/mobile/" + link.a["href"])


def wFile(docs, name):
    """ghi nội dung vào file"""
    with open(name, "w", encoding="utf-8") as f:
        f.write(docs)
        print("Ghi thanh cong!")
        f.close()


def directory(url):
    """ Lấy tiêu đề tác phẩm"""
    return url[42:-13:] + "_" + url[-4::]

def cover(url):
    """ Lấy ảnh bìa """
    name = url[42:-13:]
    url_image = "https://isach.info/images/story/cover/" + name+".jpg"
    res = requests.get(url_image)
    with open(name+"\\OEBPS\\images\\cover.jpg", "wb") as f:
        f.write(res.content)
        f.close()

def contents(url):
    """ Lấy giá đối tượng soup trong bs4"""
    links = link_chapter(url)
    dic = {}
    for link in links:
        print(link)
        parser = beauti(link)
        # docx = ""
        # docs = parser.find_all("div", class_=re.compile("story_poem|ms_chapter|ms_text"))
        # try:
        #     docs[1].div['class'] = ["dropcap_" + docs[1].div['class'][0][-1]]
        # except:
        #     print("Khong the thay dropcap !")
        # name = url[42:-13:]
        # for doc in docs:
        #     docx += str(doc)
        # wFile(docx, name +"\\OEBPS\\text\\" + directory(link) + ".html")
        dic[directory(link)]=(parser.select("#content_body > form > div.ms_chapter")[0].contents[0])
    return dic
def jinjaepub(file_name, **kwargs):
    file_loader = FileSystemLoader("./template")
    env = Environment(loader=file_loader)
    template = env.get_template(file_name)
    output = template.render(kwargs)
    return output

if __name__ == "__main__":
    print(os.getcwd())

    url = "https://isach.info/mobile/story.php?story=cho_toi_xin_mot_ve_di_tuoi_tho__nguyen_nhat_anh&chapter=0000"
    book = "Hoa Mat Troi"
    items = ["content.opf", "cover.html", "title.html", "toc.ncx"]
    datas = contents(url)
    toc = jinjaepub("toc.ncx", datas=datas, book = book)
    with open("toc.html", "w", encoding = "utf-8") as f:
        f.write(toc)
        f.close()