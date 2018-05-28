import os
import sys

from argparse import ArgumentParser
from jinja2 import PackageLoader, Environment, FileSystemLoader

from ..helper import ArgparseHelper
from .tasks import *


class Command(object):
    """
    项目构建工具
    """
    def __init__(self, tasks):
        self.tasks = tasks
        self.args = self.parse_args()
        self.templates_path = self.args.templates
        self.task = tasks[self.args.task.lower()]()

    def create(self):
        if self.templates_path:
            env = Environment(loader=FileSystemLoader(self.templates_path))
        else:
            env = Environment(loader=PackageLoader('star_builder', 'templates'))
        self.task.create(env, **vars(self.args))

    def parse_args(self):
        base_parser = ArgumentParser(
            description=self.__class__.__doc__, add_help=False)
        base_parser.add_argument("-t", "--templates", help="模板路径.")

        parser = ArgumentParser(description="Apistar项目构建工具", add_help=False)
        parser.add_argument('-h', '--help', action=ArgparseHelper,
                            help='显示帮助信息并退出. ')
        sub_parsers = parser.add_subparsers(dest="task", help="创建模块类型. ")

        for name, task in self.tasks.items():
            sub_parser = sub_parsers.add_parser(
                name.lower(), parents=[base_parser], help=task.__doc__)
            task.enrich_parser(sub_parser)
        # 当不提供参数时，len(sys.argv) == 1, 不会打印帮助，需要手动打印
        # add_subparsers无法指定required=True, 这是argparse的bug。
        if len(sys.argv) < 2:
            parser.print_help()
            exit(1)
        return parser.parse_args()


def find_tasks():
    sys.path.insert(0, os.getcwd())
    tasks = dict()

    try:
        model = __import__("tasks")
        for k in dir(model):
            cls = getattr(model, k)
            if cls is not Task and isinstance(cls, type) and issubclass(cls, Task):
                tasks[k.lower()] = cls
    except ImportError:
        pass

    for name, prop in globals().items():
        if prop is not Task and isinstance(prop, type) and issubclass(prop, Task):
            tasks[name.lower()] = prop
    return tasks


def main():
    Command(find_tasks()).create()


if __name__ == "__main__":
    main()