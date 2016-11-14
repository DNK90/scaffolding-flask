#!/usr/bin/env python
import os
import shutil
import sys
import subprocess
import json
import inflect
import json
from modules.replace_string import *
from modules.errors import BlueprintError

from custom_fields import *

test_script = 'tests.bash'
json_file = sys.argv[1]


# Error classes
def make_plural(resource):
    # https://pypi.python.org/pypi/inflect
    p = inflect.engine()
    if p.singular_noun(resource):
        resources = resource
        resource = p.singular_noun(resource)
        return resource, resources
    else:
        resources = p.plural(resource)
        return resource, resources


def generate_files(module_path, resource, resources, add_fields, db_rows, schema, meta,
                   init_self_vars, init_args, test_add_fields, test_update_fields, app_name, app_version):
    app_files = ['views.txt', 'models.txt', '__init__.txt', 'tests.txt']

    for file in app_files:

        # Generate App files
        if file == "views.txt":
            with open(os.path.join(module_path, 'views.py'), "w") as new_file:
                with open(os.path.join("app", "views.txt"), "r") as old_file:
                    for line in old_file:
                        new_file.write(line.format(resource=resource,
                                                   resources=resources,
                                                   Resources=resources.title(),
                                                   Resource=resource.title(),
                                                   add_fields=add_fields))

        elif file == "models.txt":
            with open(os.path.join(module_path, 'models.py'), "w") as new_file:
                with open(os.path.join("app", "models.txt"), "r") as old_file:
                    for line in old_file:
                        new_file.write(line.format(resource=resource, resources=resources,
                                                   Resource=resource.title(),
                                                   db_rows=db_rows,
                                                   schema=schema, meta=meta,
                                                   init_self_vars=init_self_vars,
                                                   init_args=init_args))

        elif file == "__init__.txt":
            with open(os.path.join(module_path, '__init__.py'), "w") as new_file:
                with open(os.path.join("app", "__init__.txt"), "r") as old_file:
                    for line in old_file:
                        new_file.write(line)

        # Tests
        elif file == "tests.txt":
            with open(os.path.join(module_path, 'test_{}.py'.format(resources)), "w") as new_file:
                with open(os.path.join("app", "tests.txt"), "r") as old_file:
                    for line in old_file:
                        new_file.write(line.format(resource=resource, resources=resources,
                                                   Resource=resource.title(),
                                                   test_add_fields=json.dumps(
                                                       test_add_fields),
                                                   test_update_fields=json.dumps(
                                                       test_update_fields
                                                   ), app=app_name, app_version=app_version))


def register_blueprints(project_dir, app, version, resources):
    string_to_insert_after = '# Blueprints'
    new_blueprint = """
    # Blueprints
    from app.{resources}.views import {resources}
    app.register_blueprint({resources}, url_prefix='/{app}/{version}/{resources}')""".format(
        app=app,
        version=version,
        resources=resources)

    blueprint_file = os.path.join(project_dir, "app", "__init__.py")

    with open(blueprint_file, 'r+') as old_file:
        file_data = old_file.read()
    if string_to_insert_after in file_data:
        # replace the first occurrence
        new_file_data = file_data.replace(
            string_to_insert_after, new_blueprint, 1)
        with open(blueprint_file, 'w') as new_file:
            new_file.write(new_file_data)
            print("Registered Blueprints for ", resources)
    else:
        raise BlueprintError()


def clean_up(module_path):
    if os.path.isdir(module_path):
        shutil.rmtree(module_path)


def run_pip_install(project_dir, pip_string):
    try:
        cmd_output = subprocess.check_output(
            [pip_string, "install", "-r", os.path.join(project_dir, "requirements.txt")])
        print("Ran {} install".format(pip_string))
    except subprocess.CalledProcessError:
        print("{} install failed".format(pip_string))
        raise


def run_autopep8(project_dir):
    try:
        cmd_output = subprocess.check_output(
            ['autopep8', '--in-place', '--recursive', os.path.join(project_dir, 'app')])
        print("Ran autopep8")
    except subprocess.CalledProcessError:
        print("autopep8 failed")
        raise


# Main Code Start
#
# Parse JSON file
def scaffold(file):
    with open(file) as data_file:
        data = json.load(data_file)

        # project path
        project_dir = os.path.join(data["project_path"], data["app"])

        # python command
        try:
            python_string = data["python_command"][0]
            pip_string = data["python_command"][1]
        except KeyError as e:
            python_string = "python"
            pip_string = "pip"

        # A list that stores table info
        tables = []

        # loop through columns.
        for module in data["db"]:
            # make module name plural
            resource, resources = make_plural(module["table"])

            # Start strings to insert into models
            db_rows = ""
            schema = ""
            meta = ""
            init_self_vars = ""
            init_args = ""
            # End strings to insert into models

            # Start strings to insert into views
            add_fields = ""

            # strings to insert into tests.py
            test_add_fields = {}
            test_update_fields = {}

            if module["columns"]:
                for column in module["columns"]:

                    field = column["name"]
                    field_type = column["type"]

                    # Get primary key if exists
                    try:
                        is_primary_key = column["primary_key"]
                        primary_key = " primary_key=True,"
                    except KeyError as e:
                        is_primary_key = False
                        primary_key = ""

                    nullable = "False"
                    try:
                        if column["nullable"]:
                            nullable = "True"
                    except KeyError as e:
                        pass

                    # Get foreign key if exists
                    try:
                        foreign_key = " db.ForeignKey('{}'),".format(column["foreign_key"])
                        nullable = "True"
                    except KeyError as e:
                        foreign_key = ""

                    if field_type == "string":
                        db_rows += """
    {} = db.Column(db.String(250),{}{} nullable={})""".format(field, primary_key, foreign_key, nullable)

                        if not is_primary_key and nullable == "False":
                            schema += """
    {} = fields.String(validate=not_blank)""".format(field)
                            test_add_fields[field] = string_test
                            test_update_fields[field] = update_string_test
                        elif is_primary_key:
                            schema += """
    {} = fields.String(dump_only=True)""".format(field)

                    elif field_type == "boolean":
                        db_rows += """
    {} = db.Column(db.Boolean,{}{} nullable={})""".format(field, primary_key, foreign_key, nullable)
                        if not is_primary_key and nullable == "False":
                            schema += """
    {} = fields.String(validate=not_blank)""".format(field)
                            test_add_fields[field] = string_test
                            test_update_fields[field] = update_string_test
                        elif is_primary_key:
                            schema += """
    {} = fields.String(dump_only=True)""".format(field)

                    elif field_type == "integer":
                        db_rows += """
    {} = db.Column(db.Integer,{}{} nullable={})""".format(field, primary_key, foreign_key, nullable)
                        if not is_primary_key:
                            schema += """
    {} = fields.Integer()""".format(field)
                            if nullable == "False":
                                test_add_fields[field] = string_test
                                test_update_fields[field] = update_string_test
                        else:
                            schema += """
    {} = fields.Integer(dump_only=True)""".format(field)

                    elif field_type == "biginteger":
                        db_rows += """
    {} = db.Column(db.BigInteger,{}{} nullable={})""".format(field, primary_key, foreign_key, nullable)
                        if not is_primary_key:
                            schema += """
    {} = fields.Integer()""".format(field)
                            if nullable == "False":
                                test_add_fields[field] = string_test
                                test_update_fields[field] = update_string_test
                        else:
                            schema += """
    {} = fields.Integer(dump_only=True)""".format(field)

                    elif field_type == "email":
                        db_rows += """
    {} = db.Column(db.String(250),{}{} nullable={})""".format(field, primary_key, foreign_key, nullable)

                        if not is_primary_key and nullable == "False":
                            schema += """
    {} = fields.String(validate=not_blank)""".format(field)
                            test_add_fields[field] = string_test
                            test_update_fields[field] = update_string_test
                        elif is_primary_key:
                            schema += """
    {} = fields.String(dump_only=True)""".format(field)

                    elif field_type == "url":

                        db_rows += """
    {} = db.Column(db.String(250),{}{} nullable={})""".format(field, primary_key, foreign_key, nullable)

                        if not is_primary_key and nullable == "False":
                            schema += """
    {} = fields.String(validate=not_blank)""".format(field)
                            test_add_fields[field] = string_test
                            test_update_fields[field] = update_string_test
                        elif is_primary_key:
                            schema += """
    {} = fields.String(dump_only=True)""".format(field)

                    elif field_type == "datetime":

                        db_rows += """
    {} = db.Column(db.TIMESTAMP,{}{} server_default=db.func.current_timestamp(),nullable=False)"""\
                            .format(field, primary_key, foreign_key)

                        if not is_primary_key and nullable == "False":
                            schema += """
    {} = fields.String(validate=not_blank)""".format(field)
                            test_add_fields[field] = string_test
                            test_update_fields[field] = update_string_test
                        elif is_primary_key:
                            schema += """
    {} = fields.String(dump_only=True)""".format(field)

                    elif field_type == "date":

                        db_rows += """
    {} = db.Column(db.Date,{}{} nullable={})""".format(field, primary_key, foreign_key, nullable)

                        if not is_primary_key and nullable == "False":
                            schema += """
    {} = fields.String(validate=not_blank)""".format(field)
                            test_add_fields[field] = string_test
                            test_update_fields[field] = update_string_test
                        elif is_primary_key:
                            schema += """
    {} = fields.String(dump_only=True)""".format(field)

                    elif field_type == "decimal":

                        db_rows += """
    {} = db.Column(db.Numeric,{}{} nullable={})""".format(field, primary_key, foreign_key, nullable)

                        if not is_primary_key and nullable == "False":
                            schema += """
    {} = fields.String(validate=not_blank)""".format(field)
                            test_add_fields[field] = string_test
                            test_update_fields[field] = update_string_test
                        elif is_primary_key:
                            schema += """
    {} = fields.String(dump_only=True)""".format(field)

                    elif field_type == "text":

                        db_rows += """
    {} = db.Column(db.Text,{}{} nullable={})""".format(field, primary_key, foreign_key, nullable)

                        if not is_primary_key and nullable == "False":
                            schema += """
    {} = fields.String(validate=not_blank)""".format(field)
                            test_add_fields[field] = string_test
                            test_update_fields[field] = update_string_test
                        elif is_primary_key:
                            schema += """
    {} = fields.String(dump_only=True)""".format(field)

                    if not is_primary_key:
                        # models
                        meta += """ '{}', """.format(field)
                        init_args += """ {}, """.format(field)

                        if nullable == "False":
                            init_self_vars += """
        self.{field} = {field}""".format(field=field)
                            # Views
                            add_fields += add_string.format(field)
                        else:
                            init_self_vars += """
        if {field}:
            self.{field} = {field}""".format(field=field)
                            add_fields += add_string_none

                # Generate files with the new fields
                module_dir = os.path.join(project_dir, 'app', resources)

                # create list
                tables.append({"table": resource, "sources": [module_dir, resource, resources, add_fields, db_rows, schema,
                                                        init_self_vars, meta, init_args, test_add_fields,
                                                          test_update_fields]})

        # loop through relationships
        for module in data["db"]:
            resource, resources = make_plural(module["table"])
            try:
                relationships = module["relationships"]
                for relationship in relationships:
                    relationship_string = """
    # addition_relationship
    {} = db.relationship('{}', backref='{}', lazy='dynamic')""".format(resources, resource.title(),relationship)
                    try:
                        index, table = find(tables, relationship)
                        table["sources"][4] += relationship_string

                        tables[index] = table
                    except TypeError:
                        append_relationship(relationship, relationship_string, project_dir)

            except KeyError:
                pass

        for table in tables:
            sources = table["sources"]
            module_dir = sources[0]
            resource = sources[1]
            resources = sources[2]
            add_fields = sources[3]
            db_rows = sources[4]
            schema = sources[5]
            init_self_vars = sources[6]
            meta = sources[7]
            init_args = sources[8]
            test_add_fields = sources[9]
            test_update_fields = sources[10]
            try:
                os.mkdir(module_dir)
                try:
                    generate_files(module_dir, resource, resources, add_fields, db_rows, schema, meta,
                                   init_self_vars, init_args, test_add_fields, test_update_fields,
                                   data["app"], data["version"])
                    print('{} created successfully'.format(module_dir))
                    register_blueprints(project_dir, data["app"], data["version"], resources)

                    # Add tests to test.bash
                    test_dir = os.path.join(project_dir, test_script)
                    replace_string(resource, resources, python_string, test_dir, "#TESTS", test_script_string)

                    run_pip_install(project_dir, pip_string)
                    run_autopep8(project_dir)
                except:
                    clean_up(module_dir)
                    raise

            except:
                raise


def append_relationship(relationship, relationship_string, project_dir):
    # Need to have project_dir, app, relationship (plural), models.py
    string_to_insert_after = "# addition_relationship"
    element, elements = make_plural(relationship)
    model_path = os.path.join(project_dir, "app", elements, "models.py")
    with open(model_path, 'r+') as old_file:
        file_data = old_file.read()
        if string_to_insert_after in file_data:
            # replace the first occurrence
            new_file_data = file_data.replace(
                string_to_insert_after, relationship_string, 1)
            with open(model_path, 'w') as new_file:
                new_file.write(new_file_data)


def find(lists, ref):
    
    assert isinstance(lists, list)
    for element in lists:
        if element["table"] == ref:
            return lists.index(element), element

if __name__ == "__main__":
    scaffold(json_file)
