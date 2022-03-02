'''提取图片详细信息中的GPS信息'''
import os
import exifread
import re

def read(file_name):
    gps = {}
    date = ''
    file_path = 'D:/12-1houhaixiaoxue/' + file_name
    f = open(file_path,'rb')
    contexts = exifread.process_file(f)
    return contexts

#将字符串转化成浮点数尝试。不能对带/的字符串进行运算
'''def string_to_float(str):
    return float(str)'''

filePath = 'D:/12-1houhaixiaoxue'
list_data = os.listdir(filePath)
file = open('x.txt','w+')
alt_sum = 0
for i in list_data:
    dict1 = read(i)

    #需要先去除括号[]和/2000||除以的位数不是固定的,识别‘/’位置||应该保留/2000，那是一个运算
    #出现字符串‘5837/2000’转化不成浮点数问题
    long = str(dict1['GPS GPSLongitude'])
    lat = str(dict1['GPS GPSLatitude'])
    long_fix = long[1:(len(long)-1)]
    lat_fix = lat[1:(len(lat)-1)]

    #度分秒到小数点转换
    long_split = re.split(r',',long_fix)
    ###将第三位带‘/’字符串转化为数字字符串
    x3 = long_split[2]
    long_num3 = int(x3[1:x3.index('/')]) / int(x3[x3.index('/')+1:])
    long_split[2] = str(long_num3)
    x = [float(j) for j in long_split]
    longitude = x[0] + x[1] / 60 + x[2] / 3600

    lat_split = re.split(r',', lat_fix)
    y3 = lat_split[2]
    lat_num3 = int(y3[1:y3.index('/')]) / int(y3[y3.index('/')+1:])
    lat_split[2] = str(lat_num3)
    z = [float(k) for k in lat_split]
    latitude = z[0] + z[1] / 60 + z[2] / 3600

    #高度
    alt = str(dict1['GPS GPSAltitude'])
    alt = int(alt[:alt.index('/')]) / int(alt[alt.index('/')+1:])
    alt = alt + 20



    file.write(i + ' ' + str(longitude) + ' ' + str(latitude) + ' ' +
               str(alt) + '\n')
file.close()
