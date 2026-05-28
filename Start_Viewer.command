#!/bin/bash

cd "$(dirname "$0")" || exit 1

if [ ! -f "./Start_Viewer.sh" ]; then
  echo "Could not find Start_Viewer.sh next to this file."
  echo ""
  read -r -p "Press Return to close this window..."
  exit 1
fi

bash ./Start_Viewer.sh
STATUS=$?

if [ "$STATUS" -ne 0 ]; then
  echo ""
  echo "PET Viewer did not start successfully."
  read -r -p "Press Return to close this window..."
fi

exit "$STATUS"
