import fabric.api as fab

from .config import variable_template


def run(commands, prefix=None, cd=None, shell_env=None):
    """
    This is a shell around the fabric run command that allows for conditional
    use of the prefix, cd & shell_env context managers.

    :param commands: A list of commands to run
    :param prefix: An optional prefix to use
    :param cd:  An optional working directory
    :param shell_env: An optional dict of shell env variables
    :return:
    """
    def _run():
        "closure to make running the commands reusable"
        for command in commands:
            fab.run(command)

    # this is so ugly, but I couldn't come up with a better way to do it
    # without making things terribly complicated
    # TODO make this better somehow
    # XXX maybe this can help: http://stackoverflow.com/a/5359988
    if prefix is not None and cd is not None and shell_env is not None:
        with fab.cd(cd):
            with fab.prefix(prefix):
                with fab.shell_env(**shell_env):
                    _run()
    elif prefix is not None and shell_env is not None:
        with fab.prefix(prefix):
            with fab.shell_env(**shell_env):
                _run()
    elif cd is not None and shell_env is not None:
        with fab.cd(cd):
            with fab.shell_env(**shell_env):
                _run()
    elif cd is not None and prefix is not None:
        with fab.cd(cd):
            with fab.prefix(prefix):
                _run()
    elif cd is not None:
        with fab.cd(cd):
            _run()
    elif prefix is not None:
        with fab.prefix(prefix):
            _run()
    elif shell_env is not None:
        with fab.shell_env(**shell_env):
            _run()
    else:
        _run()


def execute(category, release):
    """
    Run all stages in the specified category for the specified release

    :param category: The category of stages to run (before or after)
    :param release: The name of the release on the host
    :return: None
    """
    if 'stages' not in fab.env.config:
        return fab.warn("No stages defined in your config")

    if category not in fab.env.config['stages']:
        return fab.warn("No stages defined in the '%s' category" % category)

    for stage in fab.env.config['stages'][category]:
        if 'id' not in stage:
            fab.warn("No 'id' defined for stage: %s" % stage)
            continue

        if 'commands' not in stage:
            fab.warn("No 'commands' defined for stage: %s" % stage)
            continue

        if not isinstance(stage['commands'], (list, tuple)):
            fab.warn("The supplied commands are no in the correct format: %s" % stage['commands'])
            continue

        roles = stage.get('roles')

        fab.puts("\nRunning stage: %s (roles: %s)" % (stage['id'],
                                                      ", ".join(roles)))

        prefix = variable_template(stage.get('prefix'))
        cd = variable_template(stage.get('cd'))

        if 'shell_env' in stage:
            shell_env = {}
            for env_name in stage['shell_env']:
                shell_env[env_name] = variable_template(stage['shell_env'][env_name])
        else:
            shell_env = None

        commands = [
            variable_template(command)
            for command in stage['commands']
        ]

        fab.execute(run, commands, prefix, cd, shell_env,
                    roles=roles)
