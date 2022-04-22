'利用json格式标注文件生成tif格式文件，可用于contextcapture生成mask'
import os
import cv2
import json
from PIL import Image,ImageDraw

#json_root_path = r'C:\Users\zhangweiye\PycharmProjects\json2tiff\json'
#root_path = r'C:\Users\zhangweiye\PycharmProjects\json2tiff'
json_root_path = r'D:\深大_大文件\无人机数据\4-4nigegaosu_json\json'
root_path = r'D:\深大_大文件\无人机数据\4-4nigegaosu_json'

# 创建新文件存结果
tiff_path = root_path + '\\' + 'tiff'#tiff改为tif，会出错
isExists = os.path.exists(tiff_path)
if not isExists:
    os.makedirs(tiff_path)

for json_i in os.listdir(json_root_path):
    json_path = os.path.join(json_root_path,json_i)

    print(json_path)

    image = Image.new('RGB',(4000,3000),(255,255,255))#创建背景
    image_add = ImageDraw.ImageDraw(image)

    with open(json_path,'r') as fp:
        data = json.load(fp)
        shapes = data["shapes"]#加载每个标注框
        for rec_i in shapes:
            point_1 = tuple(rec_i["points"][0])#提取左上角点，并转tuple格式
            point_2 = tuple(rec_i["points"][1])
            image_add.rectangle((point_1,point_2),fill='black')

    image_name = json_i[:-5] + '_mask.tif'#只要修改备注，不要修改保存形式
    image_path = tiff_path + '//' + image_name
    image.save(image_path,"tiff")
    #image = os.path.join(os.getcwd(),image_name)
    #image = cv2.imread(image)
