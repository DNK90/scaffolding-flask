from modules.errors import ReplaceError

# Strings to test.bash
test_script_string = """
#TESTS
#Tests for {resources}
{python_string} app/{resources}/test_{resources}.py
#End Tests for {resources}"""


def replace_string(resource, resources, python_string, file, string_to_insert_after, new_string):
    new_string = new_string.format(resources=resources, resource=resource, Resource=resource.title(),
                                   Resources=resources.title(), python_string=python_string)

    with open(file, 'r+', encoding="utf-8") as old_file:
        filedata = old_file.read()
    if string_to_insert_after in filedata:
        # replace the first occurrence
        new_filedata = filedata.replace(
            string_to_insert_after, new_string, 1)
        with open(file, 'w', encoding="utf-8") as new_file:
            new_file.write(new_filedata)
            print("Updated", file)
    else:
        error_msg = """Unable to replace {string_to_insert_after}, with {new_string}
                      in file {file} """.format(string_to_insert_after=string_to_insert_after, new_string=new_string,
                                                file=file)
        raise ReplaceError(error_msg)
