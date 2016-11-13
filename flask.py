#!/usr/bin/env python
import os
import shutil
import json
import sys
from scaffold import scaffold

import string


class SafeFormat(object):
    def __init__(self, **kw):
        self.__dict = kw

    def __getitem__(self, name):
        return self.__dict.get(name, '{%s}' % name)


arg_1 = sys.argv[1]
arg_2 = sys.argv[2]


def init(file):
    with open(file) as data_file:
        # Read configuration
        data = json.load(data_file)

        # create project dir
        project_path = data["project_path"]
        project_name = data["app"]

        project_dir = os.path.join(project_path, project_name)
        print("mkdir {}".format(project_dir))
        os.mkdir(project_dir)

        # copy requirements, sonar-project.properties, pylintrc, __init__.py, db.py, etc.
        shutil.copy("requirements.txt", project_dir)
        shutil.copy(".pylintrc", project_dir)
        shutil.copy("sonar-project.properties", project_dir)
        shutil.copy("__init__.py", project_dir)
        shutil.copy("db.py", project_dir)
        shutil.copy(".gitignore", project_dir)
        shutil.copy("run.py", project_dir)
        shutil.copy("tests.bash", project_dir)
        shutil.copy("check_styles.bash", project_dir)

        core_dir = os.path.join("core")
        app_dir = os.path.join(project_dir, "app")
        print("mkdir {}".format(app_dir))
        os.mkdir(app_dir)

        shutil.copy(os.path.join(core_dir, "__init__.txt"), os.path.join(app_dir, "__init__.py"))
        shutil.copy(os.path.join(core_dir, "basemodels.py"), app_dir)
        shutil.copy(os.path.join(core_dir, "baseviews.py"), app_dir)

        try:
            db_username = data["db_username"]
            db_password = data["db_password"]
            db_name = data["db_name"]
            db_host_name = data["db_host_name"]
        except KeyError:
            db_username = "root"
            db_password = "root"
            db_name = "sample"
            db_host_name = "localhost"

        with open(os.path.join(project_dir, "config.py"), "w") as new_file:
            with open(os.path.join(core_dir, "config.txt"), "r") as old_file:
                for line in old_file:
                    new_line = string.Formatter().vformat(
                        line, [], SafeFormat(db_username=db_username, db_password=db_password,
                                             db_name=db_name, db_host_name=db_host_name))
                    new_file.write(new_line)

        with open(os.path.join(project_dir, 'setup.py'), "w") as new_file:
            with open(os.path.join(core_dir, "setup.txt"), "r") as old_file:
                for line in old_file:
                    new_file.write(line.format(app_name=project_name))

    scaffold(file)


if arg_1 == "init":
    init(arg_2)

if arg_1 == "scaffold":
    scaffold(arg_2)

