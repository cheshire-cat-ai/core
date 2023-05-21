#!/bin/bash

REPO_NAME="cheshire-cat"

Help()
{
   # Display Help
   echo "Check if the repo must be updated and update it rebuilding the images."
   echo ""
   echo "Syntax: ./update-cheshire-cat [-h|-r]"
   echo "options:"
   echo "h     Print the help."
   echo "r     After the update and rebuild start the containers automatically."
   echo
}


opt_restart=false
opt_daemon=""

# Get the options
while getopts ":h:r" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      r) # restart after the update
         opt_restart=true
         echo "Restart: YES"
         ;;
      \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done


if git diff-index --quiet HEAD --; then
  # No changes
  echo "$REPO_NAME is already updated"
else
  # Changes
  echo "$REPO_NAME Must be updated"
  echo "Update the $REPO_NAME"
  git pull origin main 
  echo "Rebuild the images"
  docker-compose build --no-cache
  if $opt_restart; then
      echo "Shutdown the containers"
      docker-compose down
      echo "Restart the containers"
      docker-compose up $opt_daemon
  fi
fi
