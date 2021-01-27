from config import configs


class ConfigSetup:
    def __init__(self):
        pass

    def init_app(self, app):
        # load app configs
        if app.debug:
            config_name = "development"
        elif app.testing:
            config_name = "testing"
        else:
            config_name = "production"
        app.config.from_object(configs[config_name])
