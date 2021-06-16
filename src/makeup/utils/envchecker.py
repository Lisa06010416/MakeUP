import importlib
import os
import re
import sys
import zipfile

import requests
import wget

from makeup.utils import logmanager

logger = logmanager.get_logger(__name__)
install_when_check = False


def is_in_notebook():
    try:
        get_ipython = sys.modules["IPython"].get_ipython
        if "IPKernelApp" not in get_ipython().config:
            raise ImportError("console")
        if "VSCODE_PID" in os.environ:
            raise ImportError("vscode")
        return importlib.util.find_spec("IPython") is not None
    except (AttributeError, ImportError, KeyError):
        return False


def is_in_colab():
    """
    If the code is running in colab, then set set_install_when_check_par=True
    """
    try:
        from google.colab import drive
        set_install_when_check_par(True)
        logger.info("Runing on colab")
        logger.info("Set install_when_check = True")
    except:
        return False


def set_install_when_check_par(is_install):
    global install_when_check
    install_when_check = is_install


def install_decorator(package):
    def decorator(func):
        def wrap():
            has_package = func()
            if has_package:
                return has_package
            else:
                if install_when_check:
                    os.system("pip install {}".format(package))
                    logger.info("Success install {}".format(package))
                    return True
            logger.info("Don't have {}".format(package))
            return has_package

        return wrap

    return decorator


@install_decorator("mlflow")
def has_mlflow():
    return importlib.util.find_spec('mlflow') is not None


@install_decorator("transformers==4.1.0")
def has_transformers():
    return importlib.util.find_spec('transformers') is not None


@install_decorator("pyngrok")
def has_pyngrok():
    return importlib.util.find_spec('pyngrok') is not None


@install_decorator("efficientnet_pytorch")
def has_efficientnet():
    return importlib.util.find_spec('efficientnet_pytorch') is not None


def set_mlflow_ui():
    if has_mlflow():
        from pyngrok import ngrok
        os.system("mlflow ui --port 5000 &")
        ngrok.kill()
        NGROK_AUTH_TOKEN = ""
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        ngrok_tunnel = ngrok.connect(addr="5000", proto="http", bind_tls=True)
        logger.info("MLflow Tracking UI: {}".format(ngrok_tunnel.public_url))


def getChromeVersion(os_type):
    version_re = re.compile(r'\d+')
    version = ""
    if os_type=="win":
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
            version, type = winreg.QueryValueEx(key, 'version')
            logger.info('Current Chrome Version: {}'.format(version))
        except WindowsError as e:
            logger.warning('check Chrome failed:{}'.format(e))
    elif os_type=="mac":
        version = os.popen(r"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version")
        version = version.read()
    else:
        version = os.popen("google-chrome --product-version")
        version = version.read()
    return version_re.findall(version)[0]


def check_os():
    import platform
    if platform.system().lower() == "windows":
        os = "win"
    elif platform.system().lower() == "darwin":
        os = "mac"
    elif "linux" in platform.system().lower():
        os = "linux"
    else:
        assert False, "Didn't detect os"
    logger.info("Your os is {}".format(os))
    return os


def get_chrom_driver():
    print("QQQQQQ")
    chromedriver_path = "chromedriver.exe" if check_os() == "win" else "chromedriver"
    if not os.path.isfile(chromedriver_path):
        os_type = check_os()
        chromdriver_download_list_url = "https://sites.google.com/a/chromium.org/chromedriver/downloads"
        chromdriver_download_template = "https://chromedriver.storage.googleapis.com/{version}/chromedriver_{os}.zip"
        webpage = requests.get(chromdriver_download_list_url)
        chrom_version = getChromeVersion(os_type)
        drive_version = ""

        chromdriver_download_url = ""
        for line in str(webpage.content).split('"'):
            if "https://chromedriver.storage.googleapis.com/index.html?path=" in line:
                drive_version = re.findall(r'((?:\d+\.*)+)', line)[0]
                if chrom_version == drive_version.split(".")[0]:
                    chromdriver_download_url = line
                    break
        print(drive_version)
        print(chromdriver_download_url)
        if os_type == "win":
            chromdriver_download_url = chromdriver_download_template.format(version=drive_version, os="win32")
        elif os_type == "mac":
            chromdriver_download_url = chromdriver_download_template.format(version=drive_version, os="mac64")
        else:
            chromdriver_download_url = chromdriver_download_template.format(version=drive_version, os="linux64")
        print(chromdriver_download_url)
        if chromdriver_download_url:
            logger.info("Download chromdriver from {}".format(chromdriver_download_url))
            wget.download(chromdriver_download_url, out="./chromdriver.zip")
            zip = zipfile.ZipFile('./chromdriver.zip')
            zip.extractall()
            zip.close()
            os.remove('./chromdriver.zip')
        else:
            logger.warning("Can't download chromdriver, didn't detect download url !")
