import os

import fabric.api as fab

import yaml

@fab.task
def load(target, config_file):
    """
    Load into the environment the target config from the specified file

    :param target: The name of the target to load in the config
    :param config_file: The config file to load, relative to the fabfile
    :return: None
    """
    if not config_file.startswith("/"):
        fab_path = os.path.dirname(fab.env.real_fabfile)
        config_file = os.path.join(fab_path, config_file)

    if not os.path.isfile(config_file):
        return fab.abort("No config file found. Looked for: %s" % config_file)

    with open(config_file, 'r') as f:
        try:
            fab.env.config = yaml.load(f.read())
        except yaml.YAMLError as e:
            line = column = -1
            if hasattr(e, 'problem_mark'):
                line = e.problem_mark.line + 1
                column = e.problem_mark.column + 1
            return fab.abort("Error in %s YAML syntax. Line %d, column %d" % (
                config_file, line, column)
            )

    # make sure our deployment target exists
    if target not in fab.env.config:
        return fab.abort("The target '%s' is not defined in the config." % target)

    # reset our config to the target as the root
    fab.env.config = fab.env.config[target]

@fab.task
def show(target, config_file):
    """
    Loads and pretty prints the specified targets config (for debugging)
    """
    load(target, config_file)

    import pprint
    pprint.pprint(fab.env.config)