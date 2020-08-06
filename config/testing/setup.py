import configparser

config = configparser.ConfigParser()

print(config.sections())
config.read('ini_basics.ini')
print(config.sections())

print('DEFAULT' in config)