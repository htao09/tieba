#coding:utf-8
import urllib2
import urllib
import re
import gevent
from log import Log
import multiprocessing
import multiprocessing.managers
import random,time
import Queue

class QueueManage(multiprocessing.managers.BaseManager):
    pass

log = Log().logger

def gettiebalistnumbers(name):
    url = "http://tieba.baidu.com/f?"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
    word = {"kw": name}
    word = urllib.urlencode(word)
    url = url + word
    request = urllib2.Request(url, headers=headers)
    request.add_header("Connection", "keep-alive")
    response = urllib2.urlopen(request)
    data = response.read()
    str = "<span class=\"card_infoNum\">([\s\S]*?)</span>"
    regex = re.compile(str,re.IGNORECASE)
    mylist = regex.findall(data)
    numbers=mylist[0].replace(",","")
    numbers=eval(numbers)
    str = "<span class=\"card_menNum\">([\s\S]*?)</span>"
    regex = re.compile(str, re.IGNORECASE)
    mylist = regex.findall(data)
    penumbers = mylist[0].replace(",", "")
    penumbers = eval(penumbers)
    return penumbers,numbers

def gettiebalist(name):
    numberstuple = gettiebalistnumbers(name)
    tienumbers = numberstuple[1]
    tiebalist = []
    if tienumbers%50==0:
        for i in range(tienumbers//50):
            tiebalist.append("http://tieba.baidu.com/f?kw="+name+"&ie=utf-8&pn="+str(i*50))
    else:
        for i in range(tienumbers//50+1):
            tiebalist.append("http://tieba.baidu.com/f?kw=" + name + "&ie=utf-8&pn=" + str(i * 50))
    return tiebalist

def getlistfrompage(url):
    urllist = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
    request = urllib2.Request(url, headers=headers)
    request.add_header("Connection", "keep-alive")
    response = urllib2.urlopen(request)
    data = response.read()
    str ="<li class=\" j_thread_list clearfix\" data-([\s\S]*?)</li>"
    regex = re.compile(str, re.IGNORECASE)
    mylists = regex.findall(data)
    for list in mylists:
        str1 = "<a rel=\"noreferrer\" href=\"([\s\S]*?)\" title="
        regex = re.compile(str1, re.IGNORECASE)
        data = regex.findall(list)
        urllist.append("http://tieba.baidu.com"+data[0])
    return urllist

def getlistnumbersformpage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
    request = urllib2.Request(url, headers=headers)
    request.add_header("Connection", "keep-alive")
    response = urllib2.urlopen(request)
    data = response.read()
    str = "<a rel=\"noreferrer\" href=\"([\s\S]*?)\" title="
    regex = re.compile(str, re.IGNORECASE)
    mylists = regex.findall(data)

def getemaillistfrompage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
    request = urllib2.Request(url, headers=headers)
    request.add_header("Connection", "keep-alive")
    response = urllib2.urlopen(request)
    data = response.read()
    emaillist = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", data)
    if len(emaillist)>0:
        # emaillist=emaillist.encode('utf-8')
        return emaillist
    else:
        return ""


def getqqlistfrompage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
    request = urllib2.Request(url, headers=headers)
    request.add_header("Connection", "keep-alive")
    response = urllib2.urlopen(request)
    QQlist = []
    while True:
        line = response.readline()
        if not line:
            break
        if line.find("QQ")!=-1 or line.find("Qq")!=-1 or line.find("qq")!=-1 or line.find("qQ")!=-1:
            restr = "[1-9]\\d{4,10}"
            regex = re.compile(restr,re.IGNORECASE)
            qq = regex.findall(line)
            QQlist.extend(qq)
    return QQlist

def get_findAll_mobiles(text):
    """
    :param text: 文本
    :return: 返回手机号列表
    """
    mobiles = re.findall(r"1\d{10}", text)
    return mobiles

def getmailsfromurllist(urllist,file):
    # emaillist=[]
    for url in urllist:
        emaillist = getemaillistfrompage(url)
        print emaillist
        if len(emaillist)>0:
            log.debug(emaillist)
            file.write(str(emaillist))
    # return emaillist


if __name__=="__main__":
    QueueManage.register("get_task")  # 注册函数给客户端调用
    QueueManage.register("get_result")
    manager = QueueManage(address=("192.168.137.1", 8848), authkey="123456")  # 创建一个管理器设置地址，密码
    manager.connect()#连接服务器
    task = manager.get_task()
    result = manager.get_result()
    print "-------------"
    try:
        name=task.get()
        print "-------------"
        print name
        tiebalist = gettiebalist(name)
        print tiebalist
        subtiebalist = [[], [], [], [], [], [], [], [], [], []]
        N = len(subtiebalist)
        savefilepath = name + ".txt"
        savefile = open(savefilepath, "wb")
        for i in range(len(tiebalist)):
            subtiebalist[i % N].append(tiebalist[i])
        tasklist = []
        for i in range(N):
            log.debug(subtiebalist[i])
            print subtiebalist[i]
            tasklist.append(gevent.spawn(getmailsfromurllist(subtiebalist[i], savefile)))
        gevent.joinall(tasklist)
        savefile.close()
        result.put(name)
    except:
        print "111111111-------------"
        pass

# savefilepath="python.txt"
# savefile=open(savefilepath,"wb")
# tiebalist = gettiebalist("python")
# print tiebalist
# subtiebalist=[[],[],[],[],[],[],[],[],[],[]]
# N=len(subtiebalist)
# for i in range(len(tiebalist)):
#     subtiebalist[i%N].append(tiebalist[i])
# tasklist=[]
# for i in range(N):
#     log.debug(subtiebalist[i])
#     print subtiebalist[i]
#     tasklist.append(gevent.spawn(getmailsfromurllist(subtiebalist[i],savefile)))
# gevent.joinall(tasklist)
# savefile.close()

#
# for url in tiebalist:
#     urlist = getlistfrompage(url)
#     print urlist
#     for url2 in urlist:
#         emaillist=getemaillistfrompage(url2)
#         print emaillist
#         savefile.write(str(emaillist) + "\r\n")
# savefile.close()




# mylist = getemaillistfrompage("http://tieba.baidu.com/p/6299026953")
#
# print mylist
# savefilepath="python3.txt"
# savefile=open(savefilepath,"w")
# savefile.writelines(str(mylist) + "\n")
# savefile.close()
