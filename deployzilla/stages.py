import fabric.api as fab


@fab.task
@fab.roles('app', 'db')
def run(category, release):
    """
    Run all stages in the specified category for the specified release

    :param category: The category of stages to run (before or after)
    :param release: The name of the release on the host
    :return: None
    """
    if 'stages' not in fab.env.config:
        return fab.warn("No stages defined in your config")

    if category not in fab.env.config['stages']:
        return fab.warn("No steps defined in the '%s' stage category" % category)

    # set our base command variables
    variables = {
        'release': release
    }

    # if we have command variables in our config merge them
    if 'variables' in fab.env.config:
        # we use a for loop here and apply the command variables to each new
        # item we encounter, this allows you to incrementally use the variables
        for definition in fab.env.config['variables']:
            for name, value in definition.iteritems():
                variables[name] = value % variables

    def command_template(str):
        "closure to make the command templating reusable"
        if str:
            return str % variables

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

        fab.puts("Running stage: %s" % stage['id'])

        prefix = command_template(stage.get('prefix'))
        cd = command_template(stage.get('cd'))

        if 'shell_env' in stage:
            shell_env = {}
            for env_name in stage['shell_env']:
                shell_env[env_name] = command_template(stage['shell_env'][env_name])
        else:
            shell_env = None

        def _run():
            "closure to make running the templated commands reusable"
            for command in stage['commands']:
                fab.run(command_template(command))

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
