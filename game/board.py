from .config import Config

class Board:
    def __init__(self):
        Config.test_and_generate_default()

        self.width = int(Config.get_config_option("defaultwidth"))
        self.height = int(Config.get_config_option("defaultheight"))

        print(self.width,self.height)

