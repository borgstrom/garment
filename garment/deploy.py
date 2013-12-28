import datetime
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

    # prepare the release file
    if 'git_repo' not in fab.env.config:
        return fab.abort("The target '%s' does not specify a git_repo." % target)

    if 'git_ref' not in fab.env.config:
        return fab.abort("The target '%s' does not specify a git_ref." % target)

    # generate a release filename
    now = datetime.datetime.utcnow()
    release_name = "-".join((
        now.strftime("%Y%m%d"),
        now.strftime("%H%M%S")
    ))

    # create the release on the hosts
    fab.execute(release.create, release_name, role='all')

    # run our before tasks for this release
    stages.execute("before", release_name)

    # update the current symlink
    fab.execute(release.make_current, release_name, role='all')

    # run our after tasks for this release
    stages.execute("after", release_name)

    # clean up the releases directory
    fab.execute(release.clean_up, role='all')
