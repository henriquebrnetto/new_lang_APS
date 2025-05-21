import re

class PrePro():
    def filter(code):
        return re.subn(r'//(.*?)\n|//(.*?)$', '', code)[0]