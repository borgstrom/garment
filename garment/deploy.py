import fabric.api as fab

import iso8601

from . import config
from . import release
from . import stages

__all__ = ('deploy', 'list', 'rollback')


@fab.task
def deploy(target, config_file="deploy.conf", include=None, exclude=None):
    """
    Deploy your app to the 'target' environment specified in deploy.conf
    """
    if include is not None and exclude is not None:
        return fab.abort("You cannot supply include and exclude values")

    # convert include & exclude to lists
    if include is not None:
        include = include.split(',')

    if exclude is not None:
        exclude = exclude.split(',')

    # load our config file
    config.load(target, config_file)

    # get our release name
    release_name = release.name(target)

    fab.puts("Deploying new release: %s" % release_name)

    # create the release on the hosts
    fab.execute(release.create, release_name, role='all')

    # run our before tasks for this release
    stages.execute("before", release_name, include=include, exclude=exclude)

    # update the current symlink
    fab.execute(release.make_current, release_name, role='all')

    # run our after tasks for this release
    stages.execute("after", release_name, include=include, exclude=exclude)

    # clean up the releases directory
    fab.execute(release.cleanup, role='all')


def get_releases():
    with fab.hide('output', 'running'):
        ret = fab.execute(release.list, role='all')

    # calculate the intersection of the results
    ret_lists = [
        r[1]
        for r in ret.items()
    ]
    releases = set.intersection(*[
        set(r)
        for r in ret_lists
    ])

    # sort the releases
    releases = [r for r in releases]
    releases.sort()

    return releases


@fab.task
def list(target, config_file="deploy.conf"):
    """
    Lists the releases available on your hosts
    """
    # load our config file
    config.load(target, config_file)

    releases = get_releases()

    fab.puts("Available releases:")
    for rel in releases:
        try:
            if rel.count("-") == 2:
                ts, ref, user = rel.split("-")
            else:
                ts, ref = rel.split("-")
                user = None
        except ValueError:
            release_name = "- No info available"
        else:
            iso8601_date = iso8601.parse_date(ts)
            parts = [
                iso8601_date.strftime("%a, %d %b %Y %H:%M:%S +0000"),
                "-",
                "GIT reference",
                ref
            ]

            if user is not None:
                parts.append("by")
                parts.append(user)

            release_name = " ".join(parts)

        fab.puts("* {release_name}".format(
            release_name=release_name
        ))


@fab.task
def rollback(target, release, config_file="deploy.conf"):
    # load our config file
    config.load(target, config_file)

    releases = get_releases()

    if release not in releases:
        fab.abort("The release {release} is not valid".format(
            release=release
        ))

    fab.puts("Rolling back to release: {release}".format(
        release=release
    ))

    # run our rollback tasks for this release
    stages.execute("rollback", release)

    # update the current symlink
    fab.execute(release.make_current, release, role='all')

    # run our after tasks for this release
    stages.execute("after", release)
