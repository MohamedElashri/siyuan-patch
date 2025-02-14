#!/bin/bash
clear
APP="SiYuan.app"
APP_DIR="/Applications/$APP"

if [ ! -d "$APP_DIR" ]; then
  echo "Error: $APP is not installed."
  exit 1
fi

echo "Enter your password to fix '$APP' (it won't be visible while typing)."
sudo xattr -rd com.apple.quarantine "$APP_DIR"

echo "Success! $APP can now be opened."
read -n 1 -s -r -p "Press any key to exit..."
