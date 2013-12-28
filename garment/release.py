import fabric.api as fab

import os

@fab.task
def create(release_name):
    """
    Create a release on each host with the name specified
    """
    ref = fab.env.config['git_ref']
    repo_url = fab.env.config['git_repo']
    repo_name = os.path.basename(repo_url)
    releases_dir = fab.env.config.get('releases_dir', '~/releases/')

    fab.puts("Getting latest commits from our repository...")
    fab.run("test -d ~/{repo_name} || git clone --recurse-submodules {repo_url} {repo_name}".format(
        repo_name=repo_name,
        repo_url=repo_url
    ), pty=False)

    with fab.cd("~/%s" % repo_name):
        host_repo_url = fab.run("git remote -v | grep ^origin | head -n 1 | awk '{print $2}'")

        if host_repo_url != repo_url:
            return fab.abort("The repository URL doesn't match the URL in our config. Cowardly refusing to continue...")

        fab.run("git checkout {ref}".format(ref=ref))
        fab.run("git pull origin {ref}".format(ref=ref))

        # use git to archive it
        fab.run("git archive --format=tar --prefix={release_name}/ {ref} | (cd {releases_dir}; tar xf -)".format(
            release_name=release_name,
            ref=ref,
            releases_dir=releases_dir
        ))

        # now find any submodules
        fab.puts("Looking for submodules...")
        git_submodules = fab.run("find . -mindepth 2 -name .git -print | xargs grep -l '^gitdir:'")
        for submodule in git_submodules.splitlines():
            submodule = submodule.lstrip("./").rstrip("/.git")

            submodule_ref = fab.run("git submodule status %s | awk '{print $1}'" % submodule)

            # archive it
            fab.run("(cd {submodule}; git archive --format=tar --prefix={release_name}/{submodule}/ {submodule_ref}) | (cd {releases_dir}; tar xf -)".format(
                submodule=submodule,
                release_name=release_name,
                submodule_ref=submodule_ref,
                releases_dir=releases_dir
            ))

@fab.task
def make_current(release_name):
    """
    Makes the specified release the current one

    :param release_name: The release name (returned from prepare_release)
    :return:
    """
    releases_dir = fab.env.config.get('releases_dir', '~/releases/')
    current_symlink = fab.env.config.get('current_symlink', '~/current')
    fab.run("rm -f %s && ln -s %s/%s %s" % (current_symlink, releases_dir, release_name, current_symlink))

@fab.task
def clean_up():
    """
    Cleans up the release folder

    :return: None
    """
    keep_releases = fab.env.config.get('keep_releases', 10)
    releases_dir = fab.env.config.get('releases_dir', '~/releases/')

    # build the command line to cleanup the releases directory
    commands = [
        "find %s/* -maxdepth 0 -printf '%%T@ %%p\\n'" % releases_dir,
        "sort -k 1 -n",
        "awk '{print $2}'",
        "head -n -%d" % keep_releases,
        "xargs rm -fr"
    ]

    fab.run("|".join(commands))
