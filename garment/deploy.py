import os

import fabric.api as fab

import iso8601

import config
import release
import stages

__all__ = ('deploy', 'list')

@fab.task
def deploy(target, config_file="deploy.conf"):
    """
    Deploy your application to the specified 'target' in deploy.conf
    """
    # load our config file
    config.load(target, config_file)

    # get our release name
    release_name = release.name()

    fab.puts("Deploying new release: %s" % release_name)

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

@fab.task
def list(target, config_file="deploy.conf"):
    """
    Lists the releases available on your hosts
    """
    # load our config file
    config.load(target, config_file)

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

    fab.puts("Available releases:")
    for rel in releases:
        try:
            ts, ref = rel.split("-")
            iso8601_date = iso8601.parse_date(ts)
            release_name = " ".join([
                "-",
                iso8601_date.strftime("%a, %d %b %Y %H:%M:%S +0000"),
                "GIT reference",
                ref
            ])
        except ValueError:
            release_name = "- No info available"

        fab.puts("* {rel} {release_name}".format(
            rel=rel,
            release_name=release_name
        ))
