echo 设置临时环境变量
set Path=%Path%;D:\Python36-32
set Path=%Path%;D:\Python36-32\Scripts


cd %cd%

echo 使用清华源
python3.6 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
python3.6 -m pip install pipenv


echo 设置临时环境变量
#set Path=%Path%;C:\Users\hewei\AppData\Roaming\Python\Python36\Scripts

pipenv --venv
echo 建立虚拟环境
pipenv --python "D:\Python36-32\python3.6.exe"

echo 安装模块
pipenv run pip install mariadb pandas dash dash_bootstrap_components

echo 安装pyinstaller
pipenv run pip install pyinstaller

echo 安装pyinstaller
pipenv run pip install pyinstaller

echo 开始打包
pipenv run pyinstaller BQ.py --distpath=%cd%

echo 删除虚拟环境
#pipenv --rm

cmd /k echo.