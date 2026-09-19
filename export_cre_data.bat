@echo off
setlocal enabledelayedexpansion
cd "D:\BA_Benchmarks"



if not exist "results\data" mkdir "results\data"


git -C D:\CREX\CRExplorer checkout -- app/src/main/resources/version.txt

echo.
echo Pruefe, ob D:\CREX\CRExplorer sauber ist ...
for /f %%i in ('git -C D:\CREX\CRExplorer status --porcelain') do (
    echo FEHLER: D:\CREX\CRExplorer hat unversionierte Aenderungen. Bitte erst committen/verwerfen.
    pause
    exit /b 1
)

call :export_cre "climate100LEV_base"   "load_and_cluster100LEV.crs"  "main"       "sqlite"
call :export_cre "climate100COS_base"   "load_and_cluster100COS.crs"  "main"       "sqlite"
call :export_cre "climate100JACC_base"  "load_and_cluster100JACC.crs" "main"       "sqlite"

call :export_cre "climate100LEV_crosscompare"   "load_and_cluster100LEV.crs"  "c1" "sqlite"
call :export_cre "climate100COS_crosscompare"   "load_and_cluster100COS.crs"  "c1" "sqlite"
call :export_cre "climate100JACC_crosscompare"  "load_and_cluster100JACC.crs" "c1" "sqlite"

call :export_cre "climate100LEV_10000batch"   "load_and_cluster100LEV.crs"  "c2" "sqlite"
call :export_cre "climate100COS_10000batch"   "load_and_cluster100COS.crs"  "c2" "sqlite"
call :export_cre "climate100JACC_10000batch"  "load_and_cluster100JACC.crs" "c2" "sqlite"

call :export_cre "climate100LEV_crosscompare_batch"   "load_and_cluster100LEV.crs"  "c1c2" "sqlite"
call :export_cre "climate100COS_crosscompare_batch"   "load_and_cluster100COS.crs"  "c1c2" "sqlite"
call :export_cre "climate100JACC_crosscompare_batch"  "load_and_cluster100JACC.crs" "c1c2" "sqlite"

call :export_cre "climate100LEV_c1c2d5b"   "load_and_cluster100LEV.crs"  "c1c2d1b" "postgres"
call :export_cre "climate100COS_c1c2d5b"   "load_and_cluster100COS.crs"  "c1c2d1b" "postgres"
call :export_cre "climate100JACC_c1c2d5b"  "load_and_cluster100JACC.crs" "c1c2d1b" "postgres"

call :export_cre "climate100LEV_postgres"   "load_and_cluster100LEV.crs"  "d1b" "postgres"
call :export_cre "climate100COS_postgres"   "load_and_cluster100COS.crs"  "d1b" "postgres"
call :export_cre "climate100JACC_postgres"  "load_and_cluster100JACC.crs" "d1b" "postgres"

call :export_cre "climate100LEV_d1bd2"   "load_and_cluster100LEV.crs"  "d1bd2" "postgres"
call :export_cre "climate100COS_d1bd2"   "load_and_cluster100COS.crs"  "d1bd2" "postgres"
call :export_cre "climate100JACC_d1bd2"  "load_and_cluster100JACC.crs" "d1bd2" "postgres"

call :export_cre "climate100LEV_c1d1bd2"   "load_and_cluster100LEV.crs"  "c1d1bd2" "postgres"
call :export_cre "climate100COS_c1d1bd2"   "load_and_cluster100COS.crs"  "c1d1bd2" "postgres"
call :export_cre "climate100JACC_c1d1bd2"  "load_and_cluster100JACC.crs" "c1d1bd2" "postgres"

call :export_cre "climate100LEV_c1c2d1bd2"   "load_and_cluster100LEV.crs"  "c1c2d1bd2" "postgres"
call :export_cre "climate100COS_c1c2d1bd2"   "load_and_cluster100COS.crs"  "c1c2d1bd2" "postgres"
call :export_cre "climate100JACC_c1c2d1bd2"  "load_and_cluster100JACC.crs" "c1c2d1bd2" "postgres"

echo.
echo Setze CRExplorer-Repo zurueck auf main ...
git -C D:\CREX\CRExplorer checkout main

echo.
echo Alle .cre-Dateien gesammelt in results\data\
pause
exit /b 0


:export_cre
set GROUND=%~1
set SCRIPT=%~2
set BRANCH=%~3
set ENGINE=%~4

echo.
echo ==================================================
echo  CRE-Export: %GROUND%   (Branch: %BRANCH%, Engine: %ENGINE%)
echo ==================================================

echo [1/3] Wechsle Git-Branch auf %BRANCH% ...
git -C D:\CREX\CRExplorer checkout -- app/src/main/resources/version.txt
git -C D:\CREX\CRExplorer checkout %BRANCH%
if errorlevel 1 (
    echo FEHLER: git checkout %BRANCH% fehlgeschlagen. Abgebrochen.
    exit /b 1
)

echo [2/3] Fuehre Clustering aus ...
if "%ENGINE%"=="postgres" (
    call D:\CREX\CRExplorer\gradlew.bat -p D:\CREX\CRExplorer :app:runScript --args="%SCRIPT% -db=jdbc:postgresql://localhost:5432/crexplorer?user=cre"
) else (
    call D:\CREX\CRExplorer\gradlew.bat -p D:\CREX\CRExplorer :app:runScript --args="%SCRIPT% -db=jdbc:sqlite:%GROUND%.db"
)
if errorlevel 1 (
    echo FEHLER: Java-Prozess fehlgeschlagen. Abgebrochen.
    exit /b 1
)

echo [3/3] Sichere .cre-Datei, lösche Rest
if exist "datafile.cre" (
    move /Y "datafile.cre" "results\data\%GROUND%.cre"
    echo     ^> results\data\%GROUND%.cre
) else (
    echo     WARNUNG: datafile.cre nicht gefunden
)
if exist "%GROUND%.db" del /F "%GROUND%.db"
if exist "CRE.log" del /F "CRE.log"

echo  %GROUND% abgeschlossen.
exit /b 0
