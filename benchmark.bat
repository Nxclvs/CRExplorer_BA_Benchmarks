@echo off
setlocal enabledelayedexpansion
cd "D:\BA_Benchmarks"

if not exist "results" mkdir "results"

:: ==================================================================
:: Wiederholungen pro Benchmark 
:: ==================================================================


for %%R in (2 3) do (
    call :benchmark_jar "climate100LEV_base_run%%R"   "climate100"   "load_and_cluster100LEV.crs"   "base"
    call :benchmark_jar "climate100COS_base_run%%R"   "climate100"   "load_and_cluster100COS.crs"   "base"
    call :benchmark_jar "climate100JACC_base_run%%R"   "climate100"   "load_and_cluster100JACC.crs"   "base"
    call :benchmark_jar "climate200LEV_base_run%%R"   "climate200"   "load_and_cluster200LEV.crs"   "base"
    call :benchmark_jar "climate200COS_base_run%%R"   "climate200"   "load_and_cluster200COS.crs"   "base"
    call :benchmark_jar "climate200JACC_base_run%%R"   "climate200"   "load_and_cluster200JACC.crs"   "base"
    call :benchmark_jar "climate500LEV_base_run%%R"   "climate500"   "load_and_cluster500LEV.crs"   "base"
    call :benchmark_jar "climate500COS_base_run%%R"   "climate500"   "load_and_cluster500COS.crs"   "base"
    call :benchmark_jar "climate500JACC_base_run%%R"   "climate500"   "load_and_cluster500JACC.crs"   "base"
)


for %%R in (2 3) do (
    call :benchmark_gradle "climate100LEV_10000batch_run%%R" "climate100" "load_and_cluster100LEV.crs" "c2"
    call :benchmark_gradle "climate100COS_10000batch_run%%R" "climate100" "load_and_cluster100COS.crs" "c2"
    call :benchmark_gradle "climate100JACC_10000batch_run%%R" "climate100" "load_and_cluster100JACC.crs" "c2"
    call :benchmark_gradle "climate200LEV_10000batch_run%%R" "climate200" "load_and_cluster200LEV.crs" "c2"
    call :benchmark_gradle "climate200COS_10000batch_run%%R" "climate200" "load_and_cluster200COS.crs" "c2"
    call :benchmark_gradle "climate200JACC_10000batch_run%%R" "climate200" "load_and_cluster200JACC.crs" "c2"
    call :benchmark_gradle "climate500LEV_10000batch_run%%R" "climate500" "load_and_cluster500LEV.crs" "c2"
    call :benchmark_gradle "climate500COS_10000batch_run%%R" "climate500" "load_and_cluster500COS.crs" "c2"
    call :benchmark_gradle "climate500JACC_10000batch_run%%R" "climate500" "load_and_cluster500JACC.crs" "c2"
)


for %%R in (2 3) do (
    call :benchmark_gradle "climate100LEV_crosscompare_run%%R" "climate100" "load_and_cluster100LEV.crs" "c1"
    call :benchmark_gradle "climate100COS_crosscompare_run%%R" "climate100" "load_and_cluster100COS.crs" "c1"
    call :benchmark_gradle "climate100JACC_crosscompare_run%%R" "climate100" "load_and_cluster100JACC.crs" "c1"
    call :benchmark_gradle "climate200LEV_crosscompare_run%%R" "climate200" "load_and_cluster200LEV.crs" "c1"
    call :benchmark_gradle "climate200COS_crosscompare_run%%R" "climate200" "load_and_cluster200COS.crs" "c1"
    call :benchmark_gradle "climate200JACC_crosscompare_run%%R" "climate200" "load_and_cluster200JACC.crs" "c1"
    call :benchmark_gradle "climate500LEV_crosscompare_run%%R" "climate500" "load_and_cluster500LEV.crs" "c1"
    call :benchmark_gradle "climate500COS_crosscompare_run%%R" "climate500" "load_and_cluster500COS.crs" "c1"
    call :benchmark_gradle "climate500JACC_crosscompare_run%%R" "climate500" "load_and_cluster500JACC.crs" "c1"
)


for %%R in (2 3) do (
    call :benchmark_gradle "climate100LEV_crosscompare_batch_run%%R" "climate100" "load_and_cluster100LEV.crs" "c1c2"
    call :benchmark_gradle "climate100COS_crosscompare_batch_run%%R" "climate100" "load_and_cluster100COS.crs" "c1c2"
    call :benchmark_gradle "climate100JACC_crosscompare_batch_run%%R" "climate100" "load_and_cluster100JACC.crs" "c1c2"
    call :benchmark_gradle "climate200LEV_crosscompare_batch_run%%R" "climate200" "load_and_cluster200LEV.crs" "c1c2"
    call :benchmark_gradle "climate200COS_crosscompare_batch_run%%R" "climate200" "load_and_cluster200COS.crs" "c1c2"
    call :benchmark_gradle "climate200JACC_crosscompare_batch_run%%R" "climate200" "load_and_cluster200JACC.crs" "c1c2"
    call :benchmark_gradle "climate500LEV_crosscompare_batch_run%%R" "climate500" "load_and_cluster500LEV.crs" "c1c2"
    call :benchmark_gradle "climate500COS_crosscompare_batch_run%%R" "climate500" "load_and_cluster500COS.crs" "c1c2"
    call :benchmark_gradle "climate500JACC_crosscompare_batch_run%%R" "climate500" "load_and_cluster500JACC.crs" "c1c2"
)


for %%R in (1) do (
    call :benchmark_gradle_postgres_save "climate100LEV_c1c2d5b_run%%R" "climate100" "load_and_cluster100LEV.crs" "c1c2d1b"
    call :benchmark_gradle_postgres "climate100COS_c1c2d5b_run%%R" "climate100" "load_and_cluster100COS.crs" "c1c2d1b"
    call :benchmark_gradle_postgres "climate100JACC_c1c2d5b_run%%R" "climate100" "load_and_cluster100JACC.crs" "c1c2d1b"
    call :benchmark_gradle_postgres "climate200LEV_c1c2d5b_run%%R" "climate200" "load_and_cluster200LEV.crs" "c1c2d1b"
    call :benchmark_gradle_postgres "climate200COS_c1c2d5b_run%%R" "climate200" "load_and_cluster200COS.crs" "c1c2d1b"
    call :benchmark_gradle_postgres "climate200JACC_c1c2d5b_run%%R" "climate200" "load_and_cluster200JACC.crs" "c1c2d1b"
    call :benchmark_gradle_postgres "climate500LEV_c1c2d5b_run%%R" "climate500" "load_and_cluster500LEV.crs" "c1c2d1b"
    call :benchmark_gradle_postgres "climate500COS_c1c2d5b_run%%R" "climate500" "load_and_cluster500COS.crs" "c1c2d1b"
    call :benchmark_gradle_postgres "climate500JACC_c1c2d5b_run%%R" "climate500" "load_and_cluster500JACC.crs" "c1c2d1b"
)


for %%R in (2 3) do (
    call :benchmark_gradle_postgres "climate100LEV_postgres_run%%R" "climate100" "load_and_cluster100LEV.crs" "d1b"
    call :benchmark_gradle_postgres "climate100COS_postgres_run%%R" "climate100" "load_and_cluster100COS.crs" "d1b"
    call :benchmark_gradle_postgres "climate100JACC_postgres_run%%R" "climate100" "load_and_cluster100JACC.crs" "d1b"
    call :benchmark_gradle_postgres "climate200LEV_postgres_run%%R" "climate200" "load_and_cluster200LEV.crs" "d1b"
    call :benchmark_gradle_postgres "climate200COS_postgres_run%%R" "climate200" "load_and_cluster200COS.crs" "d1b"
    call :benchmark_gradle_postgres "climate200JACC_postgres_run%%R" "climate200" "load_and_cluster200JACC.crs" "d1b"
    call :benchmark_gradle_postgres "climate500LEV_postgres_run%%R" "climate500" "load_and_cluster500LEV.crs" "d1b"
    call :benchmark_gradle_postgres "climate500COS_postgres_run%%R" "climate500" "load_and_cluster500COS.crs" "d1b"
    call :benchmark_gradle_postgres "climate500JACC_postgres_run%%R" "climate500" "load_and_cluster500JACC.crs" "d1b"
)


for %%R in (2 3) do (
    call :benchmark_gradle_postgres "climate100LEV_d1bd2_run%%R" "climate100" "load_and_cluster100LEV.crs" "d1bd2"
    call :benchmark_gradle_postgres "climate100COS_d1bd2_run%%R" "climate100" "load_and_cluster100COS.crs" "d1bd2"
    call :benchmark_gradle_postgres "climate100JACC_d1bd2_run%%R" "climate100" "load_and_cluster100JACC.crs" "d1bd2"
    call :benchmark_gradle_postgres "climate200LEV_d1bd2_run%%R" "climate200" "load_and_cluster200LEV.crs" "d1bd2"
    call :benchmark_gradle_postgres "climate200COS_d1bd2_run%%R" "climate200" "load_and_cluster200COS.crs" "d1bd2"
    call :benchmark_gradle_postgres "climate200JACC_d1bd2_run%%R" "climate200" "load_and_cluster200JACC.crs" "d1bd2"
    call :benchmark_gradle_postgres "climate500LEV_d1bd2_run%%R" "climate500" "load_and_cluster500LEV.crs" "d1bd2"
    call :benchmark_gradle_postgres "climate500COS_d1bd2_run%%R" "climate500" "load_and_cluster500COS.crs" "d1bd2"
    call :benchmark_gradle_postgres "climate500JACC_d1bd2_run%%R" "climate500" "load_and_cluster500JACC.crs" "d1bd2"
)


for %%R in (2) do (
    call :benchmark_gradle_postgres "climate100LEV_c1d1bd2_run%%R" "climate100" "load_and_cluster100LEV.crs" "c1d1bd2"
    call :benchmark_gradle_postgres "climate100COS_c1d1bd2_run%%R" "climate100" "load_and_cluster100COS.crs" "c1d1bd2"
    call :benchmark_gradle_postgres "climate100JACC_c1d1bd2_run%%R" "climate100" "load_and_cluster100JACC.crs" "c1d1bd2"
    call :benchmark_gradle_postgres "climate200LEV_c1d1bd2_run%%R" "climate200" "load_and_cluster200LEV.crs" "c1d1bd2"
    call :benchmark_gradle_postgres "climate200COS_c1d1bd2_run%%R" "climate200" "load_and_cluster200COS.crs" "c1d1bd2"
    call :benchmark_gradle_postgres "climate200JACC_c1d1bd2_run%%R" "climate200" "load_and_cluster200JACC.crs" "c1d1bd2"
    call :benchmark_gradle_postgres "climate500LEV_c1d1bd2_run%%R" "climate500" "load_and_cluster500LEV.crs" "c1d1bd2"
    call :benchmark_gradle_postgres "climate500COS_c1d1bd2_run%%R" "climate500" "load_and_cluster500COS.crs" "c1d1bd2"
    call :benchmark_gradle_postgres "climate500JACC_c1d1bd2_run%%R" "climate500" "load_and_cluster500JACC.crs" "c1d1bd2"
)


for %%R in (2 3) do (
    call :benchmark_gradle_postgres "climate100LEV_c1c2d1bd2_run%%R" "climate100" "load_and_cluster100LEV.crs" "c1c2d1bd2"
    call :benchmark_gradle_postgres "climate100COS_c1c2d1bd2_run%%R" "climate100" "load_and_cluster100COS.crs" "c1c2d1bd2"
    call :benchmark_gradle_postgres "climate100JACC_c1c2d1bd2_run%%R" "climate100" "load_and_cluster100JACC.crs" "c1c2d1bd2"
    call :benchmark_gradle_postgres "climate200LEV_c1c2d1bd2_run%%R" "climate200" "load_and_cluster200LEV.crs" "c1c2d1bd2"
    call :benchmark_gradle_postgres "climate200COS_c1c2d1bd2_run%%R" "climate200" "load_and_cluster200COS.crs" "c1c2d1bd2"
    call :benchmark_gradle_postgres "climate200JACC_c1c2d1bd2_run%%R" "climate200" "load_and_cluster200JACC.crs" "c1c2d1bd2"
    call :benchmark_gradle_postgres "climate500LEV_c1c2d1bd2_run%%R" "climate500" "load_and_cluster500LEV.crs" "c1c2d1bd2"
    call :benchmark_gradle_postgres "climate500COS_c1c2d1bd2_run%%R" "climate500" "load_and_cluster500COS.crs" "c1c2d1bd2"
    call :benchmark_gradle_postgres "climate500JACC_c1c2d1bd2_run%%R" "climate500" "load_and_cluster500JACC.crs" "c1c2d1bd2"
)

echo.
echo Alle Benchmarks abgeschlossen!

shutdown /s /t 180

pause
exit /b 0


:: ============================================================
::  Subroutine: einen einzelnen Benchmark durchfuehren
:: ============================================================
:benchmark_jar
set GROUND=%~1
set DB=%~2
set SCRIPT=%~3
set EXPDIR=%~4

if not exist "results\%EXPDIR%" mkdir "results\%EXPDIR%"

echo.
echo ==================================================
echo  Benchmark: %GROUND%
echo ==================================================

echo [1/4] Starte JFR-Aufzeichnung ...
java -XX:StartFlightRecording=dumponexit=true,filename="%GROUND%.jfr",settings="D:\BA_Benchmarks\ba_profile.jfc" -cp crexplorer.jar cre.Script %SCRIPT% -db=jdbc:sqlite:"%DB%.db"
if errorlevel 1 (
    echo FEHLER: Java-Prozess fehlgeschlagen. Benchmark abgebrochen.
    exit /b 1
)

echo [2/4] Konvertiere JFR-Daten in JSON ...
jfr print --json --events jdk.CPULoad,jdk.GCHeapSummary,jdk.GCHeapMemoryUsage "%GROUND%.jfr" > "%GROUND%.json"

echo [3/4] Erstelle Monitoring-Graph ...
python plot_jfr.py "%GROUND%.json" "results\%EXPDIR%\%GROUND%_monitoring.png"
if errorlevel 1 (
    echo FEHLER: Graph-Erstellung fehlgeschlagen.
)

echo [4/4] Verschiebe Dateien in Ergebnisordner ...
if exist "%DB%.db" (
    move /Y "%DB%.db" "results\%EXPDIR%\%GROUND%.db"
    echo     ^> results\%EXPDIR%\%GROUND%.db
) else (
    echo     WARNUNG: %DB%.db nicht gefunden!
)

if exist "CRE.Log" (
    move /Y "CRE.log" "results\%EXPDIR%\CRE%GROUND%.log"
    echo     ^> results\%EXPDIR%\CRE%GROUND%.log
) else (
    echo     WARNUNG: CRE.log nicht gefunden!
)

if exist "%GROUND%.jfr" (
    move /Y "%GROUND%.jfr" "results\%EXPDIR%\%GROUND%.jfr"
    echo     ^> results\%EXPDIR%\%GROUND%.jfr
) else (
    echo     WARNUNG: %GROUND%.jfr nicht gefunden!
)

if exist "%GROUND%.json" (
    move /Y "%GROUND%.json" "results\%EXPDIR%\%GROUND%.json"
    echo     ^> results\%EXPDIR%\%GROUND%.json
) else (
    echo     WARNUNG: %GROUND%.json nicht gefunden!
)

echo  Benchmark %GROUND% abgeschlossen.
exit /b 0


:benchmark_gradle
set GROUND=%~1
set DB=%~2
set SCRIPT=%~3
set EXPDIR=%~4

if not exist "results\%EXPDIR%" mkdir "results\%EXPDIR%"

echo.
echo ==================================================
echo  Benchmark: %GROUND%
echo ==================================================

echo [1/4] Starte JFR-Aufzeichnung ...
call D:\CREX\CRExplorer\gradlew.bat -p D:\CREX\CRExplorer_batch_crosscompare :app:runScript "-PjvmArg=-XX:StartFlightRecording=dumponexit=true,filename=%GROUND%.jfr,settings=D:\BA_Benchmarks\ba_profile.jfc" --args="%SCRIPT% -db=jdbc:sqlite:%DB%.db"
if errorlevel 1 (
    echo FEHLER: Java-Prozess fehlgeschlagen. Benchmark abgebrochen.
    exit /b 1
)

echo [2/4] Konvertiere JFR-Daten in JSON ...
jfr print --json --events jdk.CPULoad,jdk.GCHeapSummary,jdk.GCHeapMemoryUsage "%GROUND%.jfr" > "%GROUND%.json"

echo [3/4] Erstelle Monitoring-Graph ...
python plot_jfr.py "%GROUND%.json" "results\%EXPDIR%\%GROUND%_monitoring.png"
if errorlevel 1 (
    echo FEHLER: Graph-Erstellung fehlgeschlagen.
)

echo [4/4] Verschiebe Dateien in Ergebnisordner ...
if exist "%DB%.db" (
    move /Y "%DB%.db" "results\%EXPDIR%\%GROUND%.db"
    echo     ^> results\%EXPDIR%\%GROUND%.db
) else (
    echo     WARNUNG: %DB%.db nicht gefunden!
)

if exist "CRE.Log" (
    move /Y "CRE.log" "results\%EXPDIR%\CRE%GROUND%.log"
    echo     ^> results\%EXPDIR%\CRE%GROUND%.log
) else (
    echo     WARNUNG: CRE.log nicht gefunden!
)

if exist "%GROUND%.jfr" (
    move /Y "%GROUND%.jfr" "results\%EXPDIR%\%GROUND%.jfr"
    echo     ^> results\%EXPDIR%\%GROUND%.jfr
) else (
    echo     WARNUNG: %GROUND%.jfr nicht gefunden!
)

if exist "%GROUND%.json" (
    move /Y "%GROUND%.json" "results\%EXPDIR%\%GROUND%.json"
    echo     ^> results\%EXPDIR%\%GROUND%.json
) else (
    echo     WARNUNG: %GROUND%.json nicht gefunden!
)

echo  Benchmark %GROUND% abgeschlossen.
exit /b 0

:benchmark_gradle_postgres
set GROUND=%~1
set DB=%~2
set SCRIPT=%~3
set EXPDIR=%~4

if not exist "results\%EXPDIR%" mkdir "results\%EXPDIR%"

echo.
echo ==================================================
echo  Benchmark: %GROUND%
echo ==================================================

echo [1/4] Starte JFR-Aufzeichnung ...
call D:\CREX\CRExplorer\gradlew.bat -p D:\CREX\CRExplorer :app:runScript "-PjvmArg=-XX:StartFlightRecording=dumponexit=true,filename=%GROUND%.jfr,settings=D:\BA_Benchmarks\ba_profile.jfc" --args="%SCRIPT% -db=jdbc:postgresql://localhost:5432/crexplorer?user=cre"
if errorlevel 1 (
    echo FEHLER: Java-Prozess fehlgeschlagen. Benchmark abgebrochen.
    exit /b 1
)

echo [2/4] Konvertiere JFR-Daten in JSON ...
jfr print --json --events jdk.CPULoad,jdk.GCHeapSummary,jdk.GCHeapMemoryUsage "%GROUND%.jfr" > "%GROUND%.json"

echo [3/4] Erstelle Monitoring-Graph ...
python plot_jfr.py "%GROUND%.json" "results\%EXPDIR%\%GROUND%_monitoring.png"
if errorlevel 1 (
    echo FEHLER: Graph-Erstellung fehlgeschlagen.
)

echo [4/4] Verschiebe Dateien in Ergebnisordner ...
if exist "%DB%.db" (
    move /Y "%DB%.db" "results\%EXPDIR%\%GROUND%.db"
    echo     ^> results\%EXPDIR%\%GROUND%.db
) else (
    echo     WARNUNG: %DB%.db nicht gefunden!
)

if exist "CRE.Log" (
    move /Y "CRE.log" "results\%EXPDIR%\CRE%GROUND%.log"
    echo     ^> results\%EXPDIR%\CRE%GROUND%.log
) else (
    echo     WARNUNG: CRE.log nicht gefunden!
)

if exist "%GROUND%.jfr" (
    move /Y "%GROUND%.jfr" "results\%EXPDIR%\%GROUND%.jfr"
    echo     ^> results\%EXPDIR%\%GROUND%.jfr
) else (
    echo     WARNUNG: %GROUND%.jfr nicht gefunden!
)

if exist "%GROUND%.json" (
    move /Y "%GROUND%.json" "results\%EXPDIR%\%GROUND%.json"
    echo     ^> results\%EXPDIR%\%GROUND%.json
) else (
    echo     WARNUNG: %GROUND%.json nicht gefunden!
)

echo  Benchmark %GROUND% abgeschlossen.
exit /b 0


:benchmark_gradle_postgres_save
set GROUND=%~1
set DB=%~2
set SCRIPT=%~3
set EXPDIR=%~4

if not exist "results\%EXPDIR%" mkdir "results\%EXPDIR%"

echo.
echo ==================================================
echo  Benchmark: %GROUND%
echo ==================================================

echo [1/2] Starte JFR-Aufzeichnung ...
call D:\CREX\CRExplorer\gradlew.bat -p D:\CREX\CRExplorer :app:runScript "-PjvmArg=-XX:StartFlightRecording=dumponexit=true,filename=%GROUND%.jfr,settings=D:\BA_Benchmarks\ba_profile.jfc" --args="%SCRIPT% -db=jdbc:postgresql://localhost:5432/crexplorer?user=cre"
if errorlevel 1 (
    echo FEHLER: Java-Prozess fehlgeschlagen. Benchmark abgebrochen.
    exit /b 1
)

echo [2/2] Verschiebe Dateien in Ergebnisordner ...
if exist "%DB%.db" (
    del /F "%DB%.db"
    echo     ^> results\%EXPDIR%\%GROUND%.db
) else (
    echo     WARNUNG: %DB%.db nicht gefunden!
)

if exist "CRE.Log" (
    del /F "CRE.log" 
) else (
    echo     WARNUNG: CRE.log nicht gefunden!
)

if exist "%GROUND%.jfr" (
    del /F "%GROUND%.jfr" 

) else (
    echo     WARNUNG: %GROUND%.jfr nicht gefunden!
)

if exist "%GROUND%.json" (
    del /F "%GROUND%.json" 
) else (
    echo     WARNUNG: %GROUND%.json nicht gefunden!
)

if exist "datafile.cre" (
    move /Y "datafile.cre" "results/postgres_data/%GROUND%.cre"
)

echo  Benchmark %GROUND% abgeschlossen.
exit /b 0