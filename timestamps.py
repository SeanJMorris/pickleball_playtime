from datetime import datetime
from datetime import datetime

class Timestamps():
    def __init__(self):
        self.now_datetime = datetime.now()
        self.now_string = self.now_datetime.strftime(r"%Y.%m.%d_%H.%M.%S_%a %b %d")