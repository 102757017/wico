echo ������ʱ��������
set Path=%Path%;D:\Python36-32
set Path=%Path%;D:\Python36-32\Scripts


cd %cd%

echo ʹ���廪Դ
python3.6 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
python3.6 -m pip install pipenv


echo ������ʱ��������
#set Path=%Path%;C:\Users\hewei\AppData\Roaming\Python\Python36\Scripts

pipenv --venv
echo �������⻷��
pipenv --python "D:\Python36-32\python3.6.exe"

echo ��װģ��
pipenv run pip install mariadb pandas dash dash_bootstrap_components

echo ��װpyinstaller
pipenv run pip install pyinstaller

echo ��װpyinstaller
pipenv run pip install pyinstaller

echo ��ʼ���
pipenv run pyinstaller BQ.py --distpath=%cd%

echo ɾ�����⻷��
#pipenv --rm

cmd /k echo.