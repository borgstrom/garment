Vagrant wrapper
===============
Garment provides a simple interface to utilize Fabric on your Vargrant_
instances. It does this by providing you an object named ``vagrant`` that you
can import into your ``fabfile.py`` that exposes ``run`` & ``sudo`` methods
that work on the Vagrant_ instance of the current working directory.

Usage
-----
You can import the ``vagrant`` object from the ``garment.vagrant`` package and
then use it's methods within your tasks.

Here's a basic example::

    from fabric.api import task

    from garment.vagrant import vagrant

    @task
    def uptime():
        vagrant.run('uptime')


This would produce output similar to the following::

    [1279] ❯❯❯ fab uptime
    [localhost] local: vagrant ssh-config > /var/folders/_v/195_x2f97vv_y4yrgvtf_2t00000gp/T/tmpAbg0_7
    [default] Executing task 'vagrant_run'
    [default] run: uptime
    [default] out:  17:23:43 up  3:03,  2 users,  load average: 0.19, 0.18, 0.21
    [default] out: 

    Done.
    Disconnecting from vagrant@127.0.0.1:2222... done.

How it works
------------
THe interface simply uses Fabric's ``local`` command to first dump the ssh
config via the ``vagrant`` command, then modifies Fabric's environment and
finally it uses the ``execute`` method to run your command on the ``default``
host, which is what Vagrant names the box by default.

When it's done it restores Fabric's environment and removes the temporary file
used to hold the ssh config.

TODO / Improvements
-------------------

* Auto detect hostname from the ``ssh-config`` output

.. _Vagrant: http://vagrantup.com/
