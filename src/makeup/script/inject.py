import os

from bs4 import BeautifulSoup
from mitmproxy import ctx

import pathlib


ABS_PATH = pathlib.Path(__file__).parent.absolute()


# load in the javascript to inject
path = os.path.join(ABS_PATH, 'inject_content.js')
with open(path, 'r') as f:
    content_js = f.read()


def response(flow):
    # only process 200 responses of html content
    if flow.response.headers['Content-Type'] != 'text/html':
        return
    if not flow.response.status_code == 200:
        return

    # inject the script tag
    html = BeautifulSoup(flow.response.text, 'lxml')
    container = html.head or html.body
    if container:
        script = html.new_tag('script', type='text/javascript')
        script.string = content_js
        container.insert(0, script)
        flow.response.text = str(html)

        ctx.log.info('Successfully injected the content.js script.')
