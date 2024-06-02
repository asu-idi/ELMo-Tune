
import configparser
from utils.filter import key_filter

def dict_to_configparser(dictionary):
    '''
    Function to convert a dictionary to a configparser object

    Parameters:
    - dictionary (dict): The dictionary to be converted

    Returns: 
    - config (configparser.ConfigParser): The configparser object
    '''
    config = configparser.ConfigParser()

    for section, options in dictionary.items():
        config[section] = {}
        for key, value in options.items():
            config[section][key] = value

    return config

def configparser_to_string(config_parser):
    '''
    Function to convert a configparser object to a string

    Parameters:
    - config_parser (configparser.ConfigParser): The configparser object

    Returns:
    - string_representation (str): The string representation of the configparser object
    '''
    string_representation = ''
    for section in config_parser.sections():
        string_representation += f"[{section}]\n"
        for key, value in config_parser[section].items():
            key = key_filter(key)
            string_representation += f"  {key}={value}\n"
        string_representation += '\n'
    return string_representation