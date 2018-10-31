
import ctypes
import os

APP_ROOT="E:\\work\\proc\\video_web"
APP_DATA="E:\\work\\proc\\video_web\\data"
os.chdir(os.path.join(APP_ROOT, "dll"))
pd_dll = ctypes.cdll.LoadLibrary((os.path.join(APP_ROOT, "dll", "PosterDetector.dll")))
handle=pd_dll.PosterDetect_CreateHandle()
pd_dll.PosterDetect_SetPosterImageFilename(handle, os.path.join(APP_DATA,"demo","poster_1.bmp"))
if pd_dll.PosterDetect_OpenVideo(handle, os.path.join(APP_DATA,"demo","video_2.wmv")):
    result_path = os.path.join(APP_DATA, 'demo','result')
    while(True):
        flag = pd_dll.PosterDetect_QueryNextFrameAndSaveResult(handle,result_path)
        if flag==0 or flag==1:break
    # for idx in range(10000):
    #     if flag==0:break
    #     flag = pd_dll.PosterDetect_QueryNextFrameAndSaveResult(handle,result_path)
    #     print(flag)
    #     print(idx)

