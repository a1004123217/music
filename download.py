from urllib.request import urlretrieve
import os
# 解决
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

'''
通过txt网址文件，现在图片到本地
'''
def download():
    categories = ['music']
    for category in categories:
        # 新建存储ladder文件夹存储图片
        os.makedirs('/Users/wzy/PycharmProjects/pythonProject/music/data/%s' % category, exist_ok=True)
        # 读取txt文件
        with open('/Users/wzy/PycharmProjects/pythonProject/music/beatanddownbeat/uploadfile.txt', 'r') as file:
            urls = file.readlines()
            print(urls)
            #计算链接地址条数
            n_urls = len(urls)
            # 遍历链接地址下载图片
            for i, url in enumerate(urls):
                #print(url.strip())
                #print(url.strip().split('/')[-1])
                tmp = url.strip().split('/')[-1]
                tmp2 = tmp.strip().split('_')
                str1 = ''
                for i in range(len(tmp2)):
                    if i == 2:
                        str1 = tmp2[i]+tmp2[3][:]
                        #print(t)
                        print("str1",str1)
                        #print("tmp2",tmp[2])
               # print(tmp[2])
                print(str1)
                try:
                     # 请求下载图片，并截取最后链接第一最后一节字段命名图片
                     urlretrieve(url.strip(), '/Users/wzy/PycharmProjects/pythonProject/music/data/json/%s' % str1)
                     print('%s %i/%i' % (category, i, n_urls))
                except:

                     print('%s %i/%i' % (category, i, n_urls), 'no image')

if __name__ == '__main__':
    download()