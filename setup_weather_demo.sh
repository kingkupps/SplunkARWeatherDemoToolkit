#!/usr/bash

if  [[ ! -d "SplunkARWeatherDemoToolkit" ]]; then
  git clone "https://github.com/kingkupps/SplunkARWeatherDemoToolkit.git" || exit 1
fi

cd "SplunkARWeatherDemoToolkit" || exit 1
git pull

pip3 install -r requirements.txt
python3 -m weatherdemo.server
