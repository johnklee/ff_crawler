#!/usr/bin/python3
import os
from .extractor_base import Handler, DummyPP


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''


################################
# Function(s)
################################
def simple_fact(ext_title=False):
    handler = PlainTextHandler()

    if ext_title:
        handler.pp_list.append(DummyPP('title'))

    return handler


################################
# Class Definition
################################
class PlainTextHandler(Handler):
    def __init__(self):
        super(PlainTextHandler, self).__init__()

    def handle(self, url, content):
        return content
