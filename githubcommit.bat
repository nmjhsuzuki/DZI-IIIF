@echo off
if '%1'=='' goto endend
echo [git commit -m %1] �����s���܂��D
pause
git commit -m %1
echo [[git remote add origin https://github.com/nmjhsuzuki/DZI-IIIF.git]] �� Github �ɓo�^����Ă��܂��D
echo [git push -u origin master] �����s���܂��D
pause
git push -u origin master
:endend
