#!/bin/bash

# launch GNU screen session to run a couple of forever-running scripts

# determine directory this script is running from
# https://stackoverflow.com/questions/59895/getting-the-source-directory-of-a-bash-script-from-within
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# change working directory to peer directory 'install'
cd "${DIR}/../install" || exit 2

# run screen with command file that lives in original directory here
screen -c "$DIR/startup.screenrc"
