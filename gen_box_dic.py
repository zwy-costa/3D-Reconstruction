def gen_box_dic(m,n):
    'm为行，n为列'

    '1生成点列表'
    point_ori_list = []
    point_list = []
    point_num = (m+1) * (n+1)
    '1-1生成点初始列表'
    for i in range(point_num):
        i += 1
        point_ori_list.append(i)
    '1-2生成类矩阵列表'
    for i in range(m+1):
        list_tran =[]
        list_tran = point_ori_list[:n+1]
        point_ori_list = point_ori_list[n+1:]
        point_list.append(list_tran)

    '2循环生成字典 1-1: [1,2,6,7]'
    res_dic = {}
    for i in range(m):
        for j in range(n):
            dic_key_str = ''
            dic_key_str = str(i+1) + '-' + str(j+1)
            dic_value_list = []
            dic_value_list = [point_list[i][j],point_list[i][j+1],point_list[i+1][j],point_list[i+1][j+1]]
            res_dic.setdefault(dic_key_str,dic_value_list)

    return res_dic

'''测试步骤'''
x= gen_box_dic(2,4)
print(x)