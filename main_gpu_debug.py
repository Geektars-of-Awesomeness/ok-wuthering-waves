from config import config
from ok.OK import OK

config = config
config['debug'] = True
config['ocr']['lib'] = 'paddleocr'
ok = OK(config)
ok.start()