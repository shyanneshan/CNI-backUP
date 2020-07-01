import numpy as np
import cv2
from ffmpy3 import FFmpeg
from PIL import Image
import copy
import math
import CRC
import sys

# 将每一个二进制都填补成8bit
def padstring(s):
    s_len = len(s)
    return (10 - s_len) * "0" + s[2:]

# 每一个十进制进来编码成对应二进制形成一个总列表
def dec2bin(bin_str):
    img2 = np.fromfile(bin_str, dtype=np.uint8)
    x = img2.size
    #print(img2[181:281])
    #print(x)
    sum_list = list()
    for i in range(x):
        sum_list.append(padstring(bin(img2[i])))
    return sum_list

def made_row(s, r_len, c_len):
    a = np.zeros((r_len, c_len), dtype=np.uint8)
    strg = ""
    for j in range(len(s)):
        strg = strg + s[j]
    for i in range(8 * len(s)):
        if strg[i] == "0":
            a[0:20, 20 * i:20 * (i + 1)] = 0
        else:
            a[0:20, 20 * i:20 * (i + 1)] = 255
    return a

def is_same_frame(image_dir,image1_dir):
    a=[]
    b=[]
    c=0
    image = cv2.imread(image_dir,0)
    image1 = cv2.imread(image1_dir,0)
    for i in range(20):
        if image[540,760+20*i]<140:
            a.append(0)
        else:
            a.append(1)
        if image1[540,760+20*i]<140:
            b.append(0)
        else:
            b.append(1)
    for i in range(20):
        if a[i]==b[i]:
            c=c+1
    if c>18:
        return 1
    else:
        return 0


def arr2byte(s,v_pixel_size,h_pixel_size):
    strg = ""
    for i in range(8):
        if s[10,20*i+10] < 140:
            strg = strg + "0"
        else:
            strg = strg + "1"
    return int(strg, 2),strg

def draw_detection_pattern():
    a = np.zeros((140, 140), dtype=np.uint8)
    a[0:140,0:140]=0
    a[20:120,20:120]=255
    a[40:100,40:100]=0
    return a

def for_CRC(bin_in):
    list_CRC=list()
    for s in bin_in:
        for i in range(8):
            list_CRC.append(int(s[i]))
    return list_CRC

def form_CRC(crc):
    a=np.zeros((20,960),dtype=np.uint8)
    k=32
    while(k>0):
        if crc.code_list[-k]==1:
            a[0:20,(32-k)*30:(33-k)*30] = 255
            k=k-1
        else:
            k=k-1
    return a

def arr2CRC(a):
    b=list()
    for i in range(32):
        if a[10,15+30*i] < 160: 
            b.append(0)
        else:
            b.append(1)
    return b
    
def encoder(bin_path,out_path,time_lim, width=960, highth=960):
    time_lim=int(time_lim)
    fra = 10
    pixel_size = 20
    bin_in = dec2bin(bin_path)
    x = len(bin_in)
    row_num = int(highth / pixel_size)-1
    col_num = int(width / pixel_size / 8)
    y = int(x // (row_num * col_num))  # 生成的图片数
    if (y > time_lim * fra):
        y = time_lim * fra
    for i in range(y):
        m = i * row_num * col_num
        n = (i + 1) * row_num * col_num
        bin_slice = bin_in[m:n]
        list_CRC=for_CRC(bin_slice)
        crc=CRC.CRC(list_CRC,32)
        #n=crc.code_list
        #m=CRC.check(n)
        #print(m)
        c=form_CRC(crc)
        img = np.zeros((highth+12*pixel_size, width+12*pixel_size), dtype=np.uint8)
        for j in range(row_num):

            img[j* pixel_size+120:(j + 1) * pixel_size+120, 120:width+120] = made_row(bin_slice[j * col_num:(j + 1) * col_num],
                                                                            pixel_size, width)
        img[1060:1080,120:1080]=c
        img[100:1100,100:120]=255
        img[100:1100,1080:1100] = 255
        img[1080:1100,100:1100]=255
        img[100:120,100:1100]=255

        im = Image.fromarray(img)
        im.save(str(i) + ".png")

    ff = FFmpeg(inputs={'': '-f image2 -r ' + str(fra) + ' -i %d.png'}, outputs={out_path: '-vcodec mpeg4'})
    print(ff.cmd)
    ff.run()
    return y

def reshape_image(image):
    '''归一化图片尺寸：短边400，长边不超过800，短边400，长边超过800以长边800为主'''
    width, height = image.shape[1], image.shape[0]
    min_len = width
    scale = width * 1.0 / 400
    new_width = 400
    new_height = int(height / scale)
    if new_height > 800:
        new_height = 800
        scale = height * 1.0 / 800
        new_width = int(width / scale)
    out = cv2.resize(image, (new_width, new_height))
    return out

def find(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ret, binary = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(gray, 100, 150)
    contour_info = []
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    largest_area = 0
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])
        if area > largest_area:
            largest_area = area
            largest_coutour_index = i
    x, y, w, h = cv2.boundingRect(contours[largest_coutour_index])
    c=sorted(contours,key=cv2.contourArea, reverse=True)[1]
    rect = cv2.minAreaRect(c)  # 获取包围盒（中心点，宽高，旋转角度）
    box = np.int0(cv2.boxPoints(rect))
    #draw_img = cv2.drawContours(img.copy(), [box], -1, (0, 0, 255), 3)
    pixel = int(h/50)
    pix=int(w/50)
    new = img[y + 2 + pixel:y + h - 2 - pixel, x + 2 + pix:x + w - pix - 2]
    if (h-4-2*pixel)>150 and (h-4-2*pixel)<210 and (w-4-2*pix)< 210 and (w-4-2*pix)>150:
        return new,1
    else:
        return new,0


def cut(imgpath):
    ori_img = cv2.imread(imgpath)
    img = reshape_image(ori_img)
    processed_img,flag=find(img)
    cv2.imwrite(imgpath,processed_img)
    return flag


def decoder(video_path, bin_path,error_path,highth=960,width=960,row_num=6,col_num=47):
    ff = FFmpeg(inputs={video_path: None},
                outputs={'': '%d.png'})
    print(ff.cmd)
    ff.run()

    
    k=2
    while (1==1):
        image_dire=str(k)+".png"
        if cut(image_dire)==0:
            k=k+1
        else:
            a = np.zeros((col_num, row_num), dtype=np.uint8)
            image = cv2.imread(image_dire,0)
            v_pixel_size=image.shape[0]//col_num
            h_pixel_size=image.shape[1]//(row_num*8)
            re_image=cv2.resize(image, (highth,width))
            #print(re_image.shape)
        
            cccc=list()
            for i in range(col_num):
                for j in range(row_num):
                    a[i][j],strr = arr2byte(re_image[i*20:(i+1)*20,j*160:(j+1)*160],20,20)
                    cccc.append(strr)      
            #print(a.shape)
            ccccc=for_CRC(cccc)
            cccc=arr2CRC(re_image[940:960,0:960])
            for g in cccc:
                ccccc.append(g)
            flag=CRC.check(ccccc)

            if flag==0:
                with open(error_path, 'ab') as f:
                    a3 = np.zeros((col_num, row_num), dtype=np.uint8)
                    a3[0:col_num,0:row_num]=255
                    f.write(a3)
            else:
                with open(error_path, 'ab') as f:
                    a4 = np.zeros((col_num, row_num), dtype=np.uint8)
                    a4[0:col_num,0:row_num]=0
                    f.write(a4)

            with open(bin_path, 'ab') as f:
                f.write(a)
            break
    k=k+5
    z=0
    while(1):
        image_dir = str(k+6*z) + ".png"
        #print(image_dir)
        image_dir_next= str(k+6*z+6) + ".png"
        d=is_same_frame(image_dir,image_dir_next)
        if (d==1):
            break
        cut(image_dir)
        #print(image_dir)
        a = np.zeros((col_num, row_num), dtype=np.uint8)
        image = cv2.imread(image_dir,0)
        v_pixel_size=image.shape[0]//col_num
        h_pixel_size=image.shape[1]//(row_num*8)
        re_image=cv2.resize(image, (highth,width))
       
        ccc=list()
        for i in range(col_num):
            for j in range(row_num):
                a[i][j],strr = arr2byte(re_image[i*20:(i+1)*20,j*160:(j+1)*160],20,20)
                ccc.append(strr)      
        #print(a.shape)
        cc=for_CRC(ccc)
        ccc=arr2CRC(re_image[940:960,0:960])
        for g in ccc:
            cc.append(g)
        flag=CRC.check(cc)

        if flag==0:
            with open(error_path, 'ab') as f:
                a1 = np.zeros((col_num, row_num), dtype=np.uint8)
                a1[0:col_num,0:row_num]=255
                f.write(a1)
        else:
            with open(error_path, 'ab') as f:
                a2 = np.zeros((col_num, row_num), dtype=np.uint8)
                a2[0:col_num,0:row_num]=0
                f.write(a2)
        with open(bin_path, 'ab') as f:
            f.write(a)
        z=z+1

