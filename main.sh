#!/usr/bin/env zsh

source ~/.zshrc

./iptables.sh
mkdir -p ./log
gunicorn -c gunicorn.py main:app