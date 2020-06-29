import yaml
from config.globalParameter import CONF_PATH


'''读取配置文件'''
def read_yaml(CONF_PATH):
    with open(CONF_PATH,encoding='utf8') as f:
        config=yaml.load(f.read(), Loader=yaml.FullLoader)
    return config

if __name__ == '__main__':
    config=read_yaml(CONF_PATH)
    print(config)