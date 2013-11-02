import datetime
import os

import fabric.api as fab

import yaml

@fab.task
def deploy(target, config_file="deploy.conf"):
    """
    Deploy your application to the specified 'target' in deploy.conf
    """
    # load our config file
    if not config_file.startswith("/"):
        fab_path = os.path.dirname(fab.env.real_fabfile)
        config_file = os.path.join(fab_path, config_file)

    if not os.path.isfile(config_file):
        return fab.error("No config file found. Looked for: %s" % config_file)

    with open(config_file, 'r') as f:
        try:
            config = yaml.load(f.read())
        except yaml.YAMLError as e:
            line = column = -1
            if hasattr(e, 'problem_mark'):
                line = e.problem_mark.line + 1
                column = e.problem_mark.column + 1
            return fab.error("Error in deploy.conf YAML syntax. Line %d, column %d" % (line, column))

    # make sure our deployment target exists
    if target not in config:
        return fab.error("The target '%s' is not defined in the config." % target)

    # reset our config to the target as the root
    config = config[target]

    # setup our host roles
    if 'hosts' not in config:
        return fab.error("The target '%s' does not define any hosts." % target)

    roles = {}
    for hostname, hostconfig in config['hosts'].iteritems():
        for role in hostconfig['roles']:
            if role not in roles:
                roles[role] = [hostname]
            else:
                roles[role].append(hostname)

    # set the roles with fabric
    fab.env.roledefs.update(roles)

    # prepare the release file
    if 'git_ref' not in config:
        return fab.error("The target '%s' does not specify a git_ref." % target)
    release_file = prepare_release(config['git_ref'])

    # send the release to the hosts
    fab.execute(send_release, release_file)

    # clean up
    os.remove("/tmp/%s.tar" % release_file)

@fab.task
def prepare_release(ref):
    """
    Create a git archive of the current working directory
    """
    fab.puts("Preparing release file for ref: %s" % ref)

    # this ensures our ref exists as fabric will bail out if it doesn't
    short_ref = fab.local("git rev-parse --short %s" % ref, capture=True)

    # generate a release filename
    now = datetime.datetime.utcnow()
    release_name = "%s-%s-%s" % (
        now.strftime("%Y.%m.%d"),
        now.strftime("%H.%M.%S"),
        short_ref
    )

    # use git to archive it locally
    fab.local("git archive --format=tar --prefix=%s/ %s > /tmp/%s.tar" % (
        release_name,
        short_ref,
        release_name
    ))

    return release_name

@fab.task
@fab.roles('app', 'db')
def send_release(release_file):
    fab.run("mkdir -p ~/releases/")
    fab.put("/tmp/%s.tar" % release_file, "~/releases/%s.tar" % release_file)
    with fab.cd("~/releases"):
        fab.run("tar xpf ./%s.tar" % release_file)
        fab.run("rm -f ./%s.tar" % release_file)
