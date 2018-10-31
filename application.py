# coding=utf8
import ConfigParser
import ctypes
import os
import shutil
import sys
import time

import cv2
from flask import Flask, render_template, request, make_response, Response
from skimage.measure import compare_ssim

reload(sys)
sys.setdefaultencoding('utf8')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

face_img_fix = "jpg"
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DATA = os.path.join(APP_ROOT, 'data')
config_data = os.path.join(APP_DATA, 'config_data')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/do_save', methods=['POST'])
def do_save():
    if len(request.files) < 1:
        return "请上传模板"
    group_ids = request.form['ids']
    if group_ids is None or group_ids == "" or len(group_ids) < 1:
        return "请选择门店"

    file_data = request.files["file_model"]
    if not allowed_file(file_data.filename) or not file_data:
        return "模板格式有误，请重新上传"

    group_ids = request.form['ids']
    interval = request.form['interval']

    for shop_name in str(group_ids).split(","):
        if shop_name is not None and shop_name != "":
            check_cf = ConfigParser.ConfigParser()
            check_cf.read(config_data)
            if not check_cf.has_section(shop_name):
                check_cf.add_section(shop_name)
            check_cf.set(shop_name, "interval", interval)
            # 更新offset
            check_cf.write(open(config_data, "w"))
            img_path = os.path.join(APP_DATA, 'file', shop_name, "file_model." + face_img_fix)
            if not os.path.exists(os.path.join(APP_DATA, 'file', shop_name)):
                os.mkdir(os.path.join(APP_DATA, 'file', shop_name))
            file_data.save(img_path)

    result = "设置成功"
    return result


@app.route('/do_check', methods=['POST'])
def do_check():
    result_path = os.path.join(APP_DATA, 'check', "result")
    check_path = os.path.join(APP_DATA, 'check', "file_check." + face_img_fix)
    pic_path = os.path.join(APP_DATA, 'check', "file_pic." + face_img_fix)
    video_path = os.path.join(APP_DATA, 'check', "file_vdo")
    return find_pic(pic_path, video_path, result_path, check_path)


@app.route('/do_upload_origin', methods=['POST'])
def do_upload_origin():
    if len(request.files) < 1:
        return "请上传文件"
    file_data = request.files["file_pic"]
    if file_data and allowed_file(file_data.filename):
        img_path = os.path.join(APP_DATA, 'check', "file_pic." + face_img_fix)
        if not os.path.exists(os.path.join(APP_DATA, 'check')):
            os.mkdir(os.path.join(APP_DATA, 'check'))
        file_data.save(img_path)
    result = "成功"
    return result


@app.route('/do_upload_vdo', methods=['POST'])
def do_upload_vdo():
    if len(request.files) < 1:
        return "请上传文件"
    file_data = request.files["file_vdo"]
    if file_data:
        img_path = os.path.join(APP_DATA, 'check', "file_vdo")
        if not os.path.exists(os.path.join(APP_DATA, 'check')):
            os.mkdir(os.path.join(APP_DATA, 'check'))
        file_data.save(img_path)
    result = "成功"
    return result


@app.route('/show_photo/<string:filename>', methods=['GET'])
def show_photo(filename):
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(os.path.join(APP_DATA, 'check/%s' % filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def find_pic(pic_path, video_path, result_path, check_path):
    result = "识别失败"
    # 删除历史识别的文件
    # if os.path.exists(check_path):
    #     os.remove(check_path)
    # 清除result目录下的文件
    if os.path.exists(result_path):
        shutil.rmtree(result_path)
    os.mkdir(result_path)
    os.chdir(os.path.join(APP_ROOT, "dll"))
    pd_dll = ctypes.cdll.LoadLibrary((os.path.join(APP_ROOT, "dll", "PosterDetector.dll")))
    handle = pd_dll.PosterDetect_CreateHandle()
    pd_dll.PosterDetect_SetPosterImageFilename(handle, pic_path)
    if pd_dll.PosterDetect_OpenVideo(handle, video_path):
        while True:
            flag = pd_dll.PosterDetect_QueryNextFrameAndSaveResult(handle, result_path)
            last_file=str(max([int(str(i).replace(".jpg","")) for i in os.listdir(result_path)]))+".jpg"
            # 文件结束或者海报搜到则返回结果
            if flag == 1:
                shutil.copyfile(os.path.join(result_path, last_file), check_path)
                # time.sleep(3)
                result = "识别成功"
                break
            elif flag == 2:
                shutil.copyfile(os.path.join(result_path, last_file), check_path)
            elif flag == 0:
                break
    return result


# def find_pic_old(pic_path, video_path, result_path):
#     result = "识别失败"
#     cap = cv2.VideoCapture(video_path)  # 读入视频文件
#     c = 0
#     while cap.isOpened():
#         success, frame = cap.read()
#         c = c + 1
#         if frame is not None:
#             if c % 10 == 0:
#                 now_pic = frame[435:710, 155:675]
#                 # cv2.imshow("now_pic",now_pic)
#                 image_a = cv2.imread(pic_path)
#                 image_b = cv2.resize(now_pic, (image_a.shape[1], image_a.shape[0]))
#                 score = simi(image_a, image_b)
#                 print(score)
#                 if score > 0.98:
#                     time.sleep(3)
#                     cv2.imwrite(result_path, frame)
#                     result = "识别成功"
#                     break
#         else:
#             break
#         # if cv2.waitKey(1) & 0xFF == ord('q'):
#         #     break
#     cap.release()
#     return result


# def simi(image_a, image_b):
#     # convert the images to grayscale
#     gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
#     gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)
#     (score, diff) = compare_ssim(gray_a, gray_b, full=True)
#     return score


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8081', debug=False, threaded=True)
