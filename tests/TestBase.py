"""
A top-level class for testing.
"""
import os
import json
import yaml

from unittest import TestCase


CWD = os.path.abspath(os.path.dirname(__file__))
OUTPUT_DATAPATH = os.path.join(CWD, 'outputs')


class TestBase(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestBase, self).__init__(*args, **kwargs)
        self.logger = None

    def pretty_json(self, details):
        return json.dumps(details, indent=4, separators=(',', ': '))

    def print_json(self, details):
        print(self.pretty_json(details))

    def read_file(self, filename):
        inp_file = open(filename, 'r')
        file = inp_file.read()
        inp_file.close()
        return file

    def read_json(self, name):
        # filename = "{}.json".format(name)
        # inp_file = open(name, 'r')
        # result = json.load(inp_file)
        # inp_file.close()
        with open(name, 'r') as f:
            result = json.loads(f.read())

        return result

    def read_yaml(self, name):
        # filename = "{}.yml".format(name)
        # inp_file = open(name, 'r')
        # result = yaml.load(inp_file, Loader=yaml.FullLoader)
        # inp_file.close()
        with open(name, 'r') as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)

        return result

    def write_json(self, name, details):
        # out_file = open(fpath, 'w+')
        # content = self.pretty_json(details)
        # out_file.write(content)
        # out_file.close()
        filename = "{}.json".format(name)
        fpath = os.path.join(OUTPUT_DATAPATH, filename)
        with open(fpath, 'w+') as f:
            content = self.pretty_json(details)
            f.write(content)
