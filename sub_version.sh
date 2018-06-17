#!/usr/bin/env bash

if [ $1 == "init" ]
then
  echo "Initializing submodule"
  git remote add my-subtree git@gitlab.com:Rosebay/fintech_helpers.git
  git subtree add --prefix modana/helpers my-subtree master
elif [ $1 == "pull" ]
then
  echo "Pulling protos"
  git subtree pull --prefix modana/helpers -squash my-subtree master
elif [ $1 == "push" ]
then
  echo "Pushing protos"
  git subtree push --prefix modana/helpers -squash my-subtree some-branch
fi
