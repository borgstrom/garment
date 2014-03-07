import fabric.api as fab

import datetime
import os

from .config import conf

_HIDE = ['output', 'running']


def name(target):
    '''
    Generate a release name with the ISO8601 date and the short rev tag
    from the ref in our repository
    '''
    with fab.hide(*_HIDE):
        now = datetime.datetime.utcnow()
        release_ref = fab.local('git ls-remote {repo_url} {git_ref} | '
                                'head -n 1 | '
                                "awk '{{print substr($1,0,7)}}'".format(
                                    repo_url=conf('repo_url'),
                                    git_ref=conf('git_ref'),
                                ),
                                capture=True)
        release_name = "-".join((
            now.strftime("%Y%m%dT%H%M%S%z"),
            release_ref
        ))

    # set some extra variables
    fab.env.config['variables']['release'] = release_name
    fab.env.config['variables']['release_dir'] = os.path.join(
        conf('releases_dir'),
        release_name
    )

    return release_name


def create(release_name):
    '''
    Create a release on each host with the name specified
    '''
    git_ref = conf('git_ref')
    repo_url = conf('repo_url')
    source_dir = conf('source_dir')
    releases_dir = conf('releases_dir')

    fab.puts("Getting latest commits from our repository...")
    with fab.hide(*_HIDE):
        fab.run("test -d {source_dir} || "
                "git clone --recursive {repo_url} {source_dir}".format(
                    repo_url=repo_url,
                    source_dir=source_dir
                ), pty=False)

    with fab.hide(*_HIDE):
        with fab.cd(source_dir):
            host_repo_url = fab.run("git remote -v | grep ^origin | head -n 1 | awk '{print $2}'")

            if host_repo_url != repo_url:
                return fab.abort("The repository URL doesn't match the URL in our config. "
                                 "Cowardly refusing to continue...")

            fab.run("git checkout {git_ref}".format(git_ref=git_ref))
            fab.run("git pull origin")

            # use git to archive it
            fab.puts("Archiving release...")
            fab.run("test -d {releases_dir} || mkdir -p {releases_dir}".format(
                releases_dir=releases_dir
            ))
            fab.run("git archive --format=tar --prefix={release_name}/ {git_ref} | "
                    "(cd {releases_dir}; tar xf -)".format(
                        release_name=release_name,
                        git_ref=git_ref,
                        releases_dir=releases_dir
                    ))

            # now find any submodules
            fab.puts("Looking for submodules...")
            with fab.settings(fab.hide('warnings'), warn_only=True):
                # we hide warnings and don't fail here as xargs returns a non-zero
                # exit status if there is no input passed to it
                git_submodules = fab.run("find . -mindepth 2 -name .git -print | "
                                         "xargs grep -l '^gitdir:'")

            for submodule in git_submodules.splitlines():
                submodule = submodule.lstrip("./").rstrip("/.git")

                submodule_ref = fab.run("git submodule status %s | awk '{print $1}'" % submodule)
                prefix = "{release_name}/{submodule}/".format(
                    submodule=submodule,
                    release_name=release_name,
                )

                # archive it
                fab.puts(" -> Archiving %s..." % submodule)
                fab.run("("
                        "cd {submodule}; "
                        "git archive --format=tar --prefix={prefix} {submodule_ref}"
                        ") | "
                        "(cd {releases_dir}; tar xf -)".format(
                            submodule_ref=submodule_ref,
                            prefix=prefix,
                            releases_dir=releases_dir
                        ))


def make_current(release_name):
    '''
    Makes the specified release the current one

    :param release_name: The release name (returned from prepare_release)
    :return:
    '''
    with fab.hide(*_HIDE):
        releases_dir = conf('releases_dir')
        current_symlink = conf('current_symlink')
        fab.run("rm -f {current_symlink} && "
                "ln -s {releases_dir}/{release_name} {current_symlink}".format(
                    current_symlink=current_symlink,
                    releases_dir=releases_dir,
                    release_name=release_name
                ))


def cleanup():
    '''
    Cleans up the release folder

    :return: None
    '''
    keep_releases = conf('keep_releases')
    releases_dir = conf('releases_dir')

    # build the command line to cleanup the releases directory
    commands = [
        "find %s/* -maxdepth 0 -printf '%%T@ %%p\\n'" % releases_dir,
        "sort -k 1 -n",
        "awk '{print $2}'",
        "head -n -%d" % keep_releases,
        "xargs rm -fr"
    ]

    fab.run("|".join(commands))


def list():
    '''
    Lists all of the releases on the host

    :return: list of releases
    '''
    releases_dir = conf('releases_dir')
    ret = fab.run("/bin/ls {releases_dir}".format(
        releases_dir=releases_dir
    ))
    return ret.split()
