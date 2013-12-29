import os

import fabric.api as fab

import yaml

def load(target, config_file):
    """
    Load into the environment the target config from the specified file

    :param target: The name of the target to load in the config
    :param config_file: The config file to load, relative to the fabfile
    :return: None
    """
    if 'config_loaded' in fab.env and \
            fab.env.config_loaded == (target, config_file):
        # we've already loaded our config for this target
        return

    if not config_file.startswith("/"):
        fab_path = os.path.dirname(fab.env.real_fabfile)
        config_file = os.path.join(fab_path, config_file)

    if not os.path.isfile(config_file):
        return fab.abort("No config file found. Looked for: %s" % config_file)

    with open(config_file, 'r') as f:
        try:
            config = yaml.load(f.read())
        except yaml.YAMLError as e:
            line = column = -1
            if hasattr(e, 'problem_mark'):
                line = e.problem_mark.line + 1
                column = e.problem_mark.column + 1
            return fab.abort("Error in %s YAML syntax. Line %d, column %d" % (
                config_file, line, column)
            )

    # make sure our deployment target exists
    if target not in config:
        return fab.abort("The target '%s' is not defined in the config." % target)

    # reset our config to the target as the root
    fab.env.config = config[target]
    fab.env.config_loaded = (target, config_file)

    # setup our host roles
    if 'hosts' not in fab.env.config:
        return fab.abort("The target '%s' does not define any hosts." % target)

    roles = {
        'all': []
    }
    for hostname, hostconfig in fab.env.config['hosts'].iteritems():
        roles['all'].append(hostname)

        for role in hostconfig['roles']:
            if role not in roles:
                roles[role] = [hostname]
            else:
                roles[role].append(hostname)

    # set the roles with fabric
    fab.env.roledefs.update(roles)

@fab.task
def show(target, config_file):
    """
    Loads and pretty prints the specified targets config (for debugging)
    """
    load(target, config_file)

    import pprint
    pprint.pprint(fab.env.config)
