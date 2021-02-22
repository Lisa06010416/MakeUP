import wget

def download(url, savepath=None):
    file = wget.download(url, out=savepath)
    print(file)