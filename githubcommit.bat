@echo off
if '%1'=='' goto endend
echo [git commit -m %1] を実行します．
pause
git commit -m %1
echo [[git remote add origin https://github.com/nmjhsuzuki/DZI-IIIF.git]] で Github に登録されています．
echo [git push -u origin master] を実行します．
pause
git push -u origin master
:endend
