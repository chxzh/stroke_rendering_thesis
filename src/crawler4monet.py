import pycurl, os
root = 'D:\\personal_files\\workplace\\graduate_thesis\\'
url = 'http://gallerix.asia/cdn/sr/442966767/_EX/349580296/'
listfile = open(root+'data\\list.txt', "r")
failedlist = open(root+'data\\failed_list.txt', "w")
os.chdir(root)
i = 0
urllist = listfile.readlines()
urlnum = len(urllist)
for url in urllist:
    url = url[:-1]
    target_path = root + 'data\\monet1\\'+ str(i)+'.jpg'
    commend = "res\\libcurl_ssl\\curl " + url + ">" + target_path
    status = os.system(commend)
    if status != 0:
        failedlist.write(url+"\n")
        failedlist.flush()
    i += 1
    print str(i) + "/" + str(urlnum)
failedlist.close()
listfile.close()