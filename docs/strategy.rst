Deployment Strategy
===================
This document serves to outline the approach to deployment that Garment takes,
and the associated conventions it defines based on this approach. See the
Configuration documentation for how the strategy is configured.

Environments
------------
Environments are containers for your various deployment scenarios, you might
have just a ``production`` environment, or you may have more complex setups
that involve multiple environments.

Releases
--------
Releases refer to an archive of an application that is identified by a time
stamp and GIT reference::

    2013.11.18-02.05.38-de20852

Releases are maintained in a designated folder on each of the Hosts and a
configurable number of historical releases are kept around for easy rollbacks
should a deployment go awry.

To create a release the ``git archive`` command is used. We also support adding
files from any submodules in the project.

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
Stages make up the workflow of the deployment process and fall into one of two
categories:

* **before**
* **after**

The **before** stages run prior to the release being switched to the current
one and the **after** stages run following the release being switched.

Stages are defined as an ordered list and run in the order that they are
defined.

Inside each stage is some configuration about the execution environment
(working directory, command prefixes, environment variables, etc) and then
an ordered list of shell commands that will be executed in order.

All commands in a Stage must succeed for the Stage to be considered a success,
if a Stage fails then deployment stops. This means that you can require that
your projects tests pass prior to doing a production deployment to ensure you
don't leave production broken due to an uncaught error.

Currently no clean up is done on failed deployments to ensure that you have the
opportunity to investigate the failure manually while implementing your config.
Your deployment shouldn't ever fail after that point so if it does leaving the
machine in the broken state allows you to fix it properly.
