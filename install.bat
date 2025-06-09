@echo off
REM ----------------------------------------
REM Скрипт install.bat
REM Автоматически создаёт conda-окружение
REM и устанавливает все зависимости
REM ----------------------------------------

set ENV_NAME=idm_sim_env

echo Создаём conda-окружение "%ENV_NAME%" на основе environment.yml...
call conda env create -f environment.yml

echo.
echo Окружение "%ENV_NAME%" успешно создано.
echo Чтобы активировать его, выполните:
echo     conda activate %ENV_NAME%
echo.
echo После этого вы сможете запускать проект командами:
echo     python main.py simulate ...
echo     python main.py visualize ...
echo.
echo Если при выполнении скрипта возникнут ошибки, проверьте, что conda находится в PATH.
pause
