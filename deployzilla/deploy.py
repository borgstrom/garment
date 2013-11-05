import os

import fabric.api as fab

import config
import release
import stages

@fab.task
def deploy(target, config_file="deploy.conf"):
    """
    Deploy your application to the specified 'target' in deploy.conf
    """
    # load our config file
    config.load(target, config_file)

    # setup our host roles
    if 'hosts' not in fab.env.config:
        return fab.abort("The target '%s' does not define any hosts." % target)

    roles = {}
    for hostname, hostconfig in fab.env.config['hosts'].iteritems():
        for role in hostconfig['roles']:
            if role not in roles:
                roles[role] = [hostname]
            else:
                roles[role].append(hostname)

    # set the roles with fabric
    fab.env.roledefs.update(roles)

    # prepare the release file
    if 'git_ref' not in fab.env.config:
        return fab.abort("The target '%s' does not specify a git_ref." % target)

    release_name = release.prepare(fab.env.config['git_ref'])

    # send the release to the hosts
    fab.execute(release.send, release_name)

    # clean up our local temp copy
    fab.local("rm -f /tmp/%s.tar" % release_name)

    # run our before tasks for this release
    fab.execute(stages.run, "before", release_name)

    # update the current symlink
    fab.execute(release.make_current, release_name)

    # run our after tasks for this release
    fab.execute(stages.run, "after", release_name)

    # clean up the releases
    # TODO
    #fab.execute(release.clean_up)
