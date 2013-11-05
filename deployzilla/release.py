import datetime

import fabric.api as fab

@fab.task
def prepare(ref):
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
    fab.local("git archive --format=tar --prefix=%s/ %s | (cd /tmp; tar xf -)" % (
        release_name,
        short_ref,
    ))

    # now find any submodules
    fab.puts("Looking for submodules...")
    git_submodules = fab.local("find . -mindepth 2 -name .git -print | xargs grep -l '^gitdir:'", capture=True)
    for submodule in git_submodules.splitlines():
        submodule = submodule.lstrip("./").rstrip("/.git")

        submodule_ref = fab.local("git submodule status %s | awk '{print $1}'" % submodule, capture=True)

        # archive it
        fab.local("(cd %s; git archive --format=tar --prefix=%s/%s/ %s) | (cd /tmp; tar xf -)" % (
            submodule,
            release_name,
            submodule,
            submodule_ref
        ))

    # now pack up the main archive and clean up our working dir
    fab.local("(cd /tmp; tar zcf %s.tar %s && rm -fr %s)" % (
        release_name,
        release_name,
        release_name
    ))

    return release_name

@fab.task
@fab.roles('app', 'db')
def send(release_name):
    """
    Sends the specified release file to the 'app' & 'db' servers

    :param release_name: The release name (returned from prepare_release)
    :return: None
    """
    releases_dir = fab.env.config.get('releases_dir', '~/releases/')
    fab.run("mkdir -p %s" % releases_dir)
    fab.put("/tmp/%s.tar" % release_name,
            "%s%s.tar" % (releases_dir, release_name))
    with fab.cd("~/releases"):
        fab.run("tar zxpf ./%s.tar" % release_name)
        fab.run("rm -f ./%s.tar" % release_name)

@fab.task
@fab.roles('app', 'db')
def make_current(release_name):
    """
    Makes the specified release the current one

    :param release_name: The release name (returned from prepare_release)
    :return:
    """
    releases_dir = fab.env.config.get('releases_dir', '~/releases/')
    current_symlink = fab.env.config.get('current_symlink', '~/current')
    fab.run("rm -f %s && ln -s %s/%s %s" % (current_symlink, releases_dir, release_name, current_symlink))
