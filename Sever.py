#coding:utf-8
import multiprocessing
import multiprocessing.managers
import random,time
import Queue

task_queue=Queue.Queue()#任务
result_queue=Queue.Queue()#结果


def return_task():#返回任务队列
    return task_queue

def return_result():#返回结果对了
    return result_queue

class QueueManage(multiprocessing.managers.BaseManager):
    pass

if __name__=="__main__":
    multiprocessing.freeze_support()#开启分布式支持
    QueueManage.register("get_task",callable=return_task)#注册函数给客户端调用
    QueueManage.register("get_result",callable=return_result)
    manager=QueueManage(address=("192.168.137.1",8848),authkey="123456")#创建一个管理器设置地址，密码
    manager.start()
    task,result=manager.get_task(),manager.get_result()
    namelist=["python","java"]
    for name in namelist:
        print  name
        savefilepath = name+".txt"
        # print savefilepath
        # savefile = open(savefilepath, "wb")
        task.put(name)
    print "watting for----------"
    for name in namelist:
        savefile=result.get()
        print savefile + "get."

    manager.shutdown()
