from osgeo import gdal
import numpy as np
import pymap3d as p3d
import open3d as o3d
#import cv2

gdal.AllRegister()
dsm_path = r'C:\Users\zhangweiye\PycharmProjects\dsm2mesh\Production_wgs84_DSM_merge_UE.tif'
pcd_path = r'C:\Users\zhangweiye\PycharmProjects\dsm2mesh\goal.pcd'
dataset = gdal.Open(dsm_path)

adfGeoTransfrom = dataset.GetGeoTransform()
band = dataset.GetRasterBand(1)
elevation = band.ReadAsArray()#高度矩阵，用索引进行提取
elevation[elevation == -9999] = 0#消除误差

nXSize = dataset.RasterXSize#假设列数4
nYSize = dataset.RasterYSize#假设行数5

#X,Y经纬度分别搞一个矩阵，进行计算。但是从wgs84到ned坐标，也需要每个坐标进行遍历
x_ones = np.ones([nYSize,nXSize], dtype = int)#调整5,4的值即可，前5后4
y_ones = np.ones([nYSize,nXSize], dtype = int)
x_geo_ori = x_ones * adfGeoTransfrom[0]#初始化矩阵，x为经度
y_geo_ori = y_ones * adfGeoTransfrom[3]#y为纬度
#print(x_geo_ori)

#搞一个等差数组，[1,2,3,4,5]，有n行
row = np.arange(nXSize,dtype = int)#每行有4列,改变参数4
columm = np.arange(nYSize,dtype = int).reshape(nYSize,1)#每列有5行

row_all = np.tile(row,(nYSize,1))#将一行扩充到总行数
columm_all = np.tile(columm,(1,nXSize))#将一列扩充到总列数

#生成最终的经纬度矩阵
x_geo = x_geo_ori + adfGeoTransfrom[1] * columm_all + adfGeoTransfrom[2] * row_all
y_geo = y_geo_ori + adfGeoTransfrom[4] * columm_all + adfGeoTransfrom[5] * row_all
#print(x_geo)
#print(y_geo)

#以下是试验代码，试验pymap3d是否能接收矩阵。答案是可以，生成三个矩阵
x_geo_50_5000 = x_geo[50:550,5000:5500]
y_geo_50_5000 = y_geo[50:550,5000:5500]
elevation_50_5000 = elevation[50:550,5000:5500]#最后一个元素不包含
#y_ned_50_5000,x_ned_50_5000,h_ned_50_5000 = p3d.geodetic2ned(y_geo_50_5000,x_geo_50_5000,elevation_50_5000,22.5080262,113.92552351,0.74242926)
y_ned_50_5000,x_ned_50_5000,h_ned_50_5000 = p3d.geodetic2ned(y_geo,x_geo,elevation,26.001319288281337,117.35990679469063,18.439312)
#用下面这三行代码确定可用坐标值
#print(elevation[500,600])
#print(x_geo[500,600])
#print(y_geo[500,600])
#以上函数调用，后面经纬度的值需要换


#合并矩阵，然后转化成pcd格式
n = nYSize*nXSize
#n = 10487 *13225
y = y_ned_50_5000.reshape(n,1)#
x = x_ned_50_5000.reshape(n,1)
h = h_ned_50_5000.reshape(n,1)

txt = np.concatenate((x,y,h),axis=1)

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(txt)
o3d.visualization.draw_geometries([pcd])
o3d.io.write_point_cloud(pcd_path,pcd,write_ascii=True)
