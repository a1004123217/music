import os
import json
path = "/Users/wzy/PycharmProjects/pythonProject/music/data/json" #文件夹目录
files= os.listdir(path) #得到文件夹下的所有文件名称
txts = []
for file in files: #遍历文件夹
    position = path+'/'+ file #构造绝对路径，"\\"，其中一个'\'为转义符
    #print (position)
    print(file)
    with open(position, "r",encoding='utf-8') as f:    #打开文件
        json_data = json.load(f)
        #print(position)
        print(json_data['markers'])
        txt_position = "/Users/wzy/PycharmProjects/pythonProject/music/data/txt/" + file[:-5] + '.txt'
        print(txt_position)
        with open(txt_position,'a') as txtloader:
            for i in json_data['markers']:
                txtloader.write(str(i/1000))  # 写入
                txtloader.write('\n')
        txtloader.close()
        #print(data.strip().split(','))