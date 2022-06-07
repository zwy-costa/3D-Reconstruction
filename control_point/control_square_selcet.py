#在一个2.5D范围内,指定一个圆心，找50m半径内，符合15m*15m可放控制点的区域(最小)
from osgeo import gdal
import pymap3d as p3
import math
import cv2
import numpy as np

gdal.AllRegister()

'''以下：一些参数'''
dsm_path = r'D:\CC projects\12-1houhaixiaoxue\Productions\Production_wgs84\Production_wgs84_DSM_merge.tif'
img_path = r'D:\CC projects\12-1houhaixiaoxue\Productions\Production_wgs84\Production_wgs84_ortho_merge.tif'
#center_pixel=(7000,5500)
center_geo = (113.927348641083,22.507894897965798)
radius=50
diagonal=15

dataset = gdal.Open(dsm_path)
img = cv2.imread(img_path, 1)
adfGeoTransform = dataset.GetGeoTransform()


#主函数-new:计算最大最小高程差距最小(最平缓)的矩形，得到其中心坐标
def main(dsm_data,adfGeoTransform,img_data,center_geo = (113.927348641083,22.507894897965798),radius=50,diagonal=15):

    #经纬度转图像坐标
    center_pixel = pixel_coor_from_geo(adfGeoTransform,center_geo)
    print("center_pixel:",center_pixel)

    #函数A:这里需要有一个距离判断,图上像素代表实际距离多少
    dist_pixel = geo_by_pixel(adfGeoTransform,center_pixel,radius,diagonal)
    print("dist_pixel_in_main:",dist_pixel)

    #函数B：将后面函数需要用的数据统一进行生成
    contours,contours_img = dataset_deal(img_data,center_pixel,dist_pixel)

    #函数C:需要获取圆内所有像素坐标
    inside_pixel = allpixel_from_round(contours_img,center_pixel,dist_pixel)
    print("diagonal",diagonal)

    #函数D-修改: 判断当前矩阵是否超出圆形检测范围，若在范围外，则不考虑
    rec_center,rec_subtract = judge_point_inrect(dsm_data,contours,dist_pixel,inside_pixel)
    min_index = rec_subtract.index(min(rec_subtract))
    min_rec_pixel = rec_center[min_index]

    #图像坐标转经纬度
    result_geo = pixel_geo_from_pixel(adfGeoTransform,min_rec_pixel)
    print(min_rec_pixel)

    return result_geo

#由经纬度转像素坐标
def pixel_coor_from_geo(adfGeoTransform,center_geo):
    center_pixel = []

    x = center_geo[0]
    y = center_geo[1]

    xOffset = int((x - adfGeoTransform[0]) / adfGeoTransform[1])
    yOffset = int((y - adfGeoTransform[3]) / adfGeoTransform[5])
    center_pixel.append(xOffset)
    center_pixel.append(yOffset)
    return center_pixel


#函数A:计算目标地理距离代表着多少像素坐标差:输入中心像素坐标和距离，返回像素坐标差
def geo_by_pixel(adfGeoTransform,center_pixel=(7000,5500),radius=50,diagonal=15):
    #
    center_geo = [0,0]
    center_geo[0] = adfGeoTransform[0] + center_pixel[0] * adfGeoTransform[1] + center_pixel[1] * adfGeoTransform[2]
    center_geo[1] = adfGeoTransform[3] + center_pixel[0] * adfGeoTransform[4] + center_pixel[1] * adfGeoTransform[5]

    #
    refer_geo = [0,0]
    refer_geo[0] = adfGeoTransform[0] + (center_pixel[0]+1000) * adfGeoTransform[1] + center_pixel[1] * adfGeoTransform[2]
    refer_geo[1] = adfGeoTransform[3] + center_pixel[0] * adfGeoTransform[4] + center_pixel[1] * adfGeoTransform[5]

    #计算像素坐标差1000，实际距离差距多少(geo的水平高度在ned坐标系下并不水平，但误差很小，忽略）
    refer_ned = p3.geodetic2ned(center_geo[1],center_geo[0],0,refer_geo[1],refer_geo[0],0)
    dist_geo = math.sqrt(refer_ned[0]*refer_ned[0]+refer_ned[1]*refer_ned[1])
    radius_pixel = radius / dist_geo * 1000
    diagonal_pixel = diagonal / dist_geo * 1000
    dist_pixel = [int(radius_pixel),int(diagonal_pixel)]

    print("diagonal_in__geo_by_pixel:",diagonal)
    return dist_pixel

#函数B:数据统一处理
def dataset_deal(ort_dataset,center_pixel=(7000,5500),dist_pixel=[0,0]):
    # 1.先在空白图上画一个圆
    #因为若圆与边界相交，无法识别闭合，故判断并加上边界
    emptyImage = np.zeros(ort_dataset.shape, np.uint8)
    cv2.circle(emptyImage, center_pixel, dist_pixel[0], (0, 0, 255), 20)
    if center_pixel[0] - dist_pixel[0] < 0:
        cv2.line(emptyImage, (0, 0), (0, ort_dataset.shape[0]), (0, 0, 255), 10)  # 左边界
    elif center_pixel[0] + dist_pixel[0] > ort_dataset.shape[1]:
        cv2.line(emptyImage,(ort_dataset.shape[1],10),(ort_dataset.shape[1],ort_dataset.shape[0]),(0,0,255),10)
    elif center_pixel[1] - dist_pixel[0] < 0:
        cv2.line(emptyImage, (0, 10), (ort_dataset.shape[1], 10), (0, 0, 255), 10)  # 上边界
    elif center_pixel[1] + dist_pixel[0] > ort_dataset.shape[0]:
        cv2.line(emptyImage, (0, ort_dataset.shape[0]), (ort_dataset.shape[1], ort_dataset.shape[0]), (0, 0, 255), 10)  # 下边界

    """print("center_pixel**:",center_pixel)
    print("dist_pixel[0]**",dist_pixel[0])"""
    binaryImg = cv2.Canny(emptyImage, 50, 200)  # canny二值化处理

    # 2.再用contours家族根据边界绘制实心圆
    h = cv2.findContours(binaryImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = h[0]
    contours_img = np.zeros(binaryImg.shape, np.uint8)
    print("binaryImg.shape**",binaryImg.shape)
    cv2.drawContours(contours_img, contours, -1, 255, -1)
    return contours,contours_img


#函数C:根据像素距离画空白圆，同时获取园内所有像素坐标
def allpixel_from_round(contours_img,center_pixel=(4000,3000),dist_pixel=[1000,200]):

    #这里需注意：cv像素坐标和np矩阵坐标，xy颠倒
    a = np.where(contours_img == 255)[1].reshape(-1, 1)  # 提取temp中像素值为255坐标的第一点，并转成列向量
    b = np.where(contours_img == 255)[0].reshape(-1, 1)
    coordinate = np.concatenate([a, b], axis=1).tolist()  # axis=1代表对应行的数组进行拼接
    #稀释像素点，加快遍历速度
    inside_pixel = []
    for i in range(len(coordinate)):
        if i % 100 == 0:
            inside_pixel.append(tuple(coordinate[i]))
    #inside_pixel = [tuple(x) for x in coordinate]

    print("center_picel:",center_pixel)
    print("dist_pixel:", dist_pixel)
    print("检测圆范围内总共有{0}个像素值".format(len(inside_pixel)))
    return inside_pixel

#函数D:判断圆内每一个点，以该点为中心的矩形，是否满足要求：
    # 1. 矩形内所有点，均位于圆内
    # 2. 最大最小值差，(小于x，(x人工指定))，最小的点
def judge_point_inrect(dsm_data,contours,dist_pixel=[300,100],inside_rect=[(1,1),(2,2)]):
    rec_center = []
    rec_subtract = []
    n = 0
    for i in range(len(inside_rect)):
        #print("len",len(inside_rect))
        pixel_remain = len(inside_rect) - i
        if rect_in_circle(contours,inside_rect[i],dist_pixel) == True:
            n += 1
            print("第{0}点为中心构成的矩形在圆形测量范围内,中心坐标为({1},{2}),检测范围内还剩{3}个像素点，目前总共有{4}个像素符合要求".format(i,inside_rect[i][0],inside_rect[i][1],pixel_remain,n))
            rec_center.append(inside_rect[i])
            subtract = max_subtract_min(dsm_data,inside_rect[i],dist_pixel)
            rec_subtract.append(subtract)
            continue
        else:
            search_rate = i / len(inside_rect) * 100
            print("第{0}点为中心构成的矩形在圆形测量范围外,中心坐标为({1},{2})，当前搜索进度为{3}%".format(i,inside_rect[i][0],inside_rect[i][1],search_rate))
            continue
    return rec_center,rec_subtract


##函数D1:用cv2.pointPolygonTest函数去判断矩阵四个角的点,是否在检测圆内
#输入，检查矩阵中心点坐标、边长一半，及其所在圆的圆心坐标、半径
#输出，该点是否位于圆内
def rect_in_circle(contours,rec_center=(2500,3000),dist_pixel=[300,100]):
    rec_corner = []
    rec_corner.append((rec_center[0] - dist_pixel[1], rec_center[1] - dist_pixel[1]))
    rec_corner.append((rec_center[0] - dist_pixel[1], rec_center[1] + dist_pixel[1]))
    rec_corner.append((rec_center[0] + dist_pixel[1], rec_center[1] - dist_pixel[1]))
    rec_corner.append((rec_center[0] + dist_pixel[1], rec_center[1] + dist_pixel[1]))
    for i in range(len(rec_corner)):
        if cv2.pointPolygonTest(contours[0],rec_corner[i],False) == 1.0:
            bool = True
            continue
        else:
            bool =  False
            break
    return bool

##函数D2:计算矩形中最大高程和最小高程的差值
#输入：dsm,矩形中心及边长的一半，
#输出：最大高程和最小高程的差值
def max_subtract_min(dsm_data,rec_center=(2500,3000),dist_pixel=[300,100]):
    rec_gdal_array = dsm_data.ReadAsArray(rec_center[0],rec_center[1],dist_pixel[1],dist_pixel[1]).astype(np.float64)
    subtract = rec_gdal_array.max() - rec_gdal_array.min()
    return subtract

#图上像素转wgs84
def pixel_geo_from_pixel(adfGeoTransform,result_pixel):
    result_geo = []
    lon = adfGeoTransform[0] + result_pixel[0] * adfGeoTransform[1] + result_pixel[1] * adfGeoTransform[2]
    lat = adfGeoTransform[3] + result_pixel[0] * adfGeoTransform[4] + result_pixel[1] * adfGeoTransform[5]
    result_geo.append(lon)
    result_geo.append(lat)
    return result_geo

proper_control_point = main(dataset,adfGeoTransform,img)
print(proper_control_point)
