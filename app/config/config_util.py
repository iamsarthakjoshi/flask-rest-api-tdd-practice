import configparser
import os


class ConfigUtil:
    @staticmethod
    def read_file(file_name):
        # Get current path
        curr_path = os.path.abspath(os.path.dirname(__file__))
        config = configparser.ConfigParser()
        config.read(curr_path + "/" + file_name)
        return config
