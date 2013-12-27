"""
This file provides a convenient way to use Fabric on your Vagrant box

Import the local vagrant instance (at the bottom) into your fabfile and
then you can call .run & .sudo and have them work on your current vagrant
instance
"""
import fabric.api as fab

import tempfile
import subprocess

class VagrantRunner(object):
    """
    A simple object that allows you to 'run' or 'sudo' on your Vagrant box
    """
    ssh_setup = False

    def setup_ssh(self):
        """
        Setup our local ssh config, only called once & when needed
        """
        if self.ssh_setup:
            return

        # create our ssh config
        self.ssh_config = tempfile.NamedTemporaryFile()

        # put our config in the file
        fab.local("vagrant ssh-config > %s" % self.ssh_config.name)

        self.orig_use_ssh_config = fab.env.use_ssh_config
        self.orig_ssh_config_path = fab.env.ssh_config_path

        self.ssh_setup = True

    def execute(self, command):
        """
        Shortcut used by run & sudo
        """
        self.setup_ssh()

        # make fabric use our config
        fab.env.use_ssh_config = True
        fab.env.ssh_config_path = self.ssh_config.name

        fab.execute(command, host='default')

        # restore the original values
        fab.env.use_ssh_config = self.orig_use_ssh_config
        fab.env.ssh_config_path = self.orig_ssh_config_path

    def run(self, *args, **kwargs):
        """
        Wrapper to fabric's run that runs on the current vagrant instance
        """
        @fab.task
        def vagrant_run():
            fab.run(*args, **kwargs)

        self.execute(vagrant_run)

    def sudo(self, *args, **kwargs):
        """
        Wrapper to fabric's sudo that runs on the current vagrant instance
        """
        @fab.task
        def vagrant_sudo():
            fab.sudo(*args, **kwargs)

        self.execute(vagrant_sudo)

# create an importable instance of our runner object
vagrant = VagrantRunner()
