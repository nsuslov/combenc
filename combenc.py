#!/usr/bin/python3

import os
import yaml
import argparse
from ad_connector import ADConnector
from combiner import Combiner


def get_config(file):
    with open(file) as config_file:
        return yaml.load(config_file, yaml.FullLoader)


def get_environment(config, hostname):
    environments = config.get('environments', {}) or {}
    for env_name, env_hosts in environments.items():
        env_hosts = env_hosts or {}
        if hostname in env_hosts: return env_name
    return 'production'


def get_ldap_groups(config, hostname):
    ad_connector = ADConnector(
        config['ldap']['uri'], 
        config['ldap']['user'], 
        config['ldap']['cred'], 
        config['ldap']['base_dn']
    )
    return ad_connector.get_groups(hostname)


def get_yaml_file_list(rules_folder, ldap_groups, hostname):
    yaml_files = list()
    yaml_files.append(rules_folder + 'default.yaml')
    for group in ldap_groups:
        yaml_files.append(rules_folder + 'groups/' + group + '.yaml')
    yaml_files.append(rules_folder + 'hosts/' + hostname + '.yaml')
    return yaml_files


def get_classes(yaml_files):
    combiner = Combiner()
    for filepath in yaml_files:
        if (os.path.exists(filepath)):
            with open(filepath) as yaml_file: 
                input_classes = yaml.load(yaml_file, yaml.FullLoader)
                combiner.append_classes(input_classes)
    return combiner.result()


def main():
    parser = argparse.ArgumentParser(prog = 'combenc')
    parser.add_argument('hostname', type=str)
    parser.add_argument('--verbose', help='Вывод примененных файлов', action='store_true')
    args = parser.parse_args()

    root_path = os.path.dirname(os.path.realpath(__file__)) + '/'
    config = get_config(root_path + 'config.yaml')
    environment = get_environment(config, args.hostname)
    rules_folder = config['rules']['folder'] + '/' + environment + '/combenc/'
    ldap_groups = get_ldap_groups(config, args.hostname)
    yaml_files = get_yaml_file_list(rules_folder, ldap_groups, args.hostname)

    if (args.verbose): print(yaml.dump(yaml_files))

    classes = get_classes(yaml_files)
    output = {
        'classes': classes,
        'environment': environment
    }
    print(yaml.dump(output))


if __name__ == '__main__':
    main()