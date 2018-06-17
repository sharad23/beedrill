# Introduction

We use git flow.

Git flow has 6 of the branch.
* Master - This is a production branch. All of our CI/CD will be carried
out through this branch.This branch should  exist in the remote.
* Develop - This branch should also exist in the remote. This is a starting branch.
* Feature - For creating a new feature we switch to this branch from develop. After completion of a feature
we switch back again to develop branch.This should exist in the remote
* Release - before switching to master switch this branch for env. configuration.This should not exist
in remote. This barnched is merged at the master at the end.
* Hotfix -  If we identify a bug in production we switch to this branch for fixes

## Installation

apt-get install git-flow


### Initialization

To initialize a new repo with the basic branch structure, use:

		git flow init [-d]

This will then interactively prompt you with some questions on which branches
you would like to use as development and production branches, and how you
would like your prefixes be named. You may simply press Return on any of
those questions to accept the (sane) default suggestions.

The ``-d`` flag will accept all defaults.


### Creating feature/release/hotfix/support branches

* To list/start/finish feature branches, use:

  		git flow feature
  		git flow feature start <name> [<base>]
  		git flow feature finish <name>

  For feature branches, the `<base>` arg must be a commit on `develop`.

* To push/pull a feature branch to the remote repository, use:

  		git flow feature publish <name>
		  git flow feature pull <remote> <name>

* To list/start/finish release branches, use:

  		git flow release
  		git flow release start <release> [<base>]
  		git flow release finish <release>

  For release branches, the `<base>` arg must be a commit on `develop`.

* To list/start/finish hotfix branches, use:

  		git flow hotfix
  		git flow hotfix start <release> [<base>]
  		git flow hotfix finish <release>

  For hotfix branches, the `<base>` arg must be a commit on `master`.

* To list/start support branches, use:

  		git flow support
  		git flow support start <release> <base>


# Submodule

* All the  generic modules are which needs to be edited are submodule.
  For example, the helpers module in the modana is the sub tree

* sub-tress: modana/helpers

* To update the submodule
  git submodule update --remote

Note: if u change the subtree and dont make a pull request it wont be reflected in the production mode.
So u need to make a pull request






