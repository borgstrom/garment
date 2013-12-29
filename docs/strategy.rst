Deployment Strategy
===================
This document serves to outline the approach to deployment that Garment takes,
and the associated conventions it defines based on this approach. See the
:ref:`configuration` documentation for how the strategy is configured.


Environments
------------
Environments are containers for your various deployment scenarios, you might
have just a ``production`` environment, or you may have more complex setups
that involve multiple environments (``qa``, ``staging``, etc).

Their names are free form and you can call them anything you like that suits
your deployment needs.


Releases
--------
Releases refer to an archive of an application that is identified by a time
stamp (ISO8601) and the GIT reference from the ref that was deployed::

    20131228T202753-4634f44

Releases are maintained in a designated folder on each of the Hosts and a
configurable number of historical releases are kept around for easy rollbacks
should a deployment go awry.

Each Host keeps a full copy of the repository. On each deployment the local
copy of the repository is updated using ``git pull``.

To create a release the ``git archive`` command is used. We also support adding
files from the submodules in a project.


Roles
-----
Roles are arbitrary items that you create that can be used to control which of
the different Stages you define run on which Hosts.

There is a special role named ``all`` that is used for targeting all hosts by
internal Garment operations (like sending the release)


Hosts
-----
Hosts are the targets that you wish to deploy your application to. They can be
assigned any number of roles that can be used to target them when running your
Stages.


Stages
------
Stages make up the workflow of the deployment process and are named as follows:

* **before**
* **after**
* **rollback**
* **cleanup**

Tasks within the Stages are defined as an ordered list and run in the order
that they are defined.

Inside each stage is some configuration about the execution environment
(working directory, command prefixes, environment variables, etc) and then
an ordered list of shell commands that will be executed.

All commands in a Stage must succeed for the Stage to be considered a success,
if a Stage fails then deployment stops. This means that you can require that
your projects tests pass prior to doing a production deployment to ensure you
don't leave production broken due to an uncaught error.

Currently no clean up is done on failed deployments to ensure that you have the
opportunity to investigate the failure manually while implementing your config.
Your deployment shouldn't ever fail after that point so if it does leaving the
machine in the broken state allows you to fix it properly.


Deployment preparation
~~~~~~~~~~~~~~~~~~~~~~
When a release is being deployed Garment will first prepare the release by
generating a name, as described above, and then making an archive of the
repository into the releases directory under this new name.

This is done entirely automatically and can only be influenced through the
:ref:`base-configuration`.


Before stage
~~~~~~~~~~~~
The **before** stage is run once the release is prepared and it allows you to
prepare the application for becoming the running release. It also allows you
to do any backup related tasks that can be used during the **rollback** stage.

If your application does not require any special preparation you do not need
to specify any tasks in the before stage and it can be omitted.

Examples of things that are done in the **before** stage:

* Installing dependencies (virtualenv, rvm, composer, etc)
* Run database migrations
* Managing/preparing static content
* Backing up the current environment
* Backing up the database


Updating current symlink
~~~~~~~~~~~~~~~~~~~~~~~~
Now that the application is prepared the symlink that is used to represent the
active deployment version is updated to point to our new release.

This is done entirely automatically and can only be influenced through the
:ref:`base-configuration`.


After stage
~~~~~~~~~~~
Like the **before** stage the **after** stage allows you to further prepare
the application for becoming the running release. You can also preform any
backup tasks you'd like as well.

If your application does not require any special preparation you do not need
to specify any tasks in the before stage and it can be omitted.

Examples of things that are done in the **after** stage:

* Restarting application servers



Operations
----------
Operations are the different workflows that Garment exposes. The following
describes each of the operations and specifies which stages are run and in
which order.

Deploy
~~~~~~
When you ask Garment to deploy it does the following:

#. Prepares the release
#. Runs the **before** stage
#. Makes the new release the current release
#. Runs the **after** stage

Rollback
~~~~~~~~
When you ask Garment to rollback it does the following:

#. Runs the **rollback** stage
#. Makes the rollback release the current release
#. Runs the **after** stage


