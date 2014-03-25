import copy
import os
import yaml

import fabric.api as fab

from collections import OrderedDict


class GarmentConfigError(Exception):
    pass


def variable_template(value, variables=None):
    '''
    Apply the config variables to the supplied value
    '''
    if value:
        if not isinstance(value, basestring):
            return value

        if variables is None:
            variables = fab.env.config['variables']

        try:
            return value.format(**variables)
        except KeyError as exc:
            fab.abort('Undefined variable requested: {exc}\n'
                      'Original value we tried to parse: {value}'.format(
                          exc=exc,
                          value=value
                      ))


def conf(name):
    '''
    Shortcut function for getting config items
    '''
    return variable_template(fab.env.config[name])


def load(target, config_file):
    '''
    Load into the environment the target config from the specified file

    :param target: The name of the target to load in the config
    :param config_file: The config file to load, relative to the fabfile
    :return: None
    '''
    if 'config_loaded' in fab.env and \
            fab.env.config_loaded == (target, config_file):
        # we've already loaded our config for this target
        return

    if not config_file.startswith('/'):
        fab_path = os.path.dirname(fab.env.real_fabfile)
        config_file = os.path.join(fab_path, config_file)

    if not os.path.isfile(config_file):
        return fab.abort('No config file found. Looked for: %s' % config_file)

    with open(config_file, 'r') as f:
        try:
            config = yaml.load(f.read())
        except yaml.YAMLError as e:
            line = column = -1
            if hasattr(e, 'problem_mark'):
                line = e.problem_mark.line + 1
                column = e.problem_mark.column + 1
            return fab.abort('Error in %s YAML syntax. Line %d, column %d' % (
                config_file, line, column)
            )

    # make sure our deployment target exists
    if target not in config:
        return fab.abort('The target "%s" is not defined in the config.' % (
            target
        ))

    # are we extending another item in the config
    if 'extends' in config[target]:
        extends = config[target]['extends']

        if extends not in config:
            return fab.abort('The target "%s" requested to extend "%s", '
                             'but "%s" is not defined in the config' % (
                                 target,
                                 extends,
                                 extends
                             ))

        # copy the item we're extending
        extended_config = copy.deepcopy(config[extends])

        # drop hosts, it is never extended
        try:
            del extended_config['hosts']
        except KeyError:
            pass

        # merge our values
        for key in config[target]:
            if key == 'extends':
                # don't copy the extends value
                continue
            elif key == 'variables':
                # if our target sets a variable that's also set in the config
                # its extending then the variable must be set in the same order
                # so that resolution will work properly

                # go through list on target and build a list & dict
                var_names = []
                var_values = {}
                for kvpair in config[target]['variables']:
                    for key, val in kvpair.iteritems():
                        var_names.append(key)
                        var_values[key] = val

                # now go through the extended config
                # when we find a key that exists in var_names we use the value
                # in var_values instead
                if 'variables' not in extended_config:
                    extended_config['variables'] = []

                new_variables = []
                for kvpair in extended_config['variables']:
                    for key, val in kvpair.iteritems():
                        if key in var_names:
                            new_variables.append({key: var_values[key]})

                            # delete it from var_names
                            var_names.remove(key)
                        else:
                            new_variables.append({key: val})

                # finally, anything left in var_names just gets appended
                for key in var_names:
                    new_variables.append({key: var_values[key]})

                extended_config['variables'] = new_variables

            elif key == 'stages':
                # stages are similar to variables, but we need to handle our
                # four stages specifically
                new_stages = {}
                for stage in ['before', 'after', 'cleanup', 'rollback']:

                    if stage not in config[target]['stages']:
                        # if the stage does not exist in our target but does
                        # exist in our extended config then just copy the
                        # whole stage from the extended one
                        if stage in extended_config['stages']:
                            new_stages[stage] = copy.deepcopy(
                                extended_config['stages'][stage]
                            )
                            continue
                    else:
                        # the stage does exist in our target config
                        # if it doesn't exist in the extended config then just
                        # copy the whole stage from the target
                        if stage not in extended_config['stages']:
                            new_stages[stage] = copy.deepcopy(
                                config[target]['stages'][stage]
                            )
                            continue

                        # the stage exists in both configs at this point
                        # merge them
                        stage_names = []
                        stage_data = {}
                        for step in config[target]['stages'][stage]:
                            step_id = None
                            for key, val in step.iteritems():
                                if key == 'id':
                                    step_id = val

                            stage_names.append(step_id)
                            stage_data[step_id] = step

                        new_stage = []

                        # check to see if we're over writing any existing steps
                        for step in extended_config['stages'][stage]:
                            step_id = None
                            for key, val in step.iteritems():
                                if key == 'id':
                                    step_id = val
                                    break

                            if step_id in stage_names:
                                new_stage.append(stage_data[step_id])
                                stage_names.remove(step_id)
                            else:
                                new_stage.append(step)

                        # anything left gets appended
                        for step_id in stage_names:
                            new_stage.append(stage_data[step_id])

                        # set it
                        new_stages[stage] = new_stage

                # set it
                extended_config['stages'] = new_stages

            else:
                extended_config[key] = copy.deepcopy(config[target][key])

        # reset config
        config[target] = extended_config

    # reset our config to the target as the root
    fab.env.config = config[target]
    fab.env.config_loaded = (target, config_file)

    # enable agent forwarding by default
    if 'forward_agent' in config and config['forward_agent'] is False:
        fab.env.forward_agent = False
    else:
        fab.env.forward_agent = True

    # setup our host roles
    if 'hosts' not in fab.env.config:
        return fab.abort('The target "%s" does not define any hosts.' % target)

    roles = {
        'all': []
    }
    for hostname, hostconfig in fab.env.config['hosts'].iteritems():
        roles['all'].append(hostname)

        if hostconfig and 'roles' in hostconfig:
            for role in hostconfig['roles']:
                if role not in roles:
                    roles[role] = [hostname]
                else:
                    roles[role].append(hostname)

    # set the roles with fabric
    fab.env.roledefs.update(roles)

    variables = OrderedDict([])

    # check required config items
    for name in ('repo_url', 'git_ref', 'deploy_dir'):
        if name not in fab.env.config:
            raise GarmentConfigError('You must supply a "%s" value '
                                     'in the target "%s"' % (
                                         name,
                                         target
                                     ))

        # push it into the variables
        variables[name] = fab.env.config[name]

    # set our defaults
    def default(name, default):
        if name not in fab.env.config:
            fab.env.config[name] = default

        # push it into the variables
        variables[name] = variable_template(fab.env.config[name], variables)

    default('source_dir', '{deploy_dir}/source')
    default('releases_dir', '{deploy_dir}/releases')
    default('current_symlink', '{deploy_dir}/current')
    default('keep_releases', 10)

    # process variables
    if 'variables' in fab.env.config:
        for definition in fab.env.config['variables']:
            for name, val in definition.iteritems():
                variables[name] = variable_template(val, variables)

    fab.env.config['variables'] = variables


@fab.task
def show(target, config_file='deploy.conf'):
    '''
    Loads and pretty prints the specified targets config (for debugging)
    '''
    load(target, config_file)

    import pprint
    pprint.pprint(fab.env.config)
