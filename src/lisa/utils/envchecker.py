import os
import sys
import importlib
from src.lisa.utils import logmanager


logger = logmanager.get_logger(__name__)
install_when_check =False


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
