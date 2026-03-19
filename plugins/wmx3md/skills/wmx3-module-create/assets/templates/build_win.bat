@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "FOLDER_PATH=%~dp0"

REM **************************
REM * 빌드 대상 선언
REM * {{MODULE_NAME}} 모듈의 Windows / RTX64 / C++Builder 빌드 타겟 목록
REM **************************
set "TargetCount=6"
set "appSolutionFileFullPath1=!FOLDER_PATH!{{MODULE_NAME}}.sln"
set "appSolutionFileFullPath2=!FOLDER_PATH!{{MODULE_NAME}}.sln"
set "appSolutionFileFullPath3=!FOLDER_PATH!{{MODULE_NAME}}.sln"
set "appSolutionFileFullPath4=!FOLDER_PATH!{{MODULE_NAME}}.sln"
set "appSolutionFileFullPath5=!FOLDER_PATH!C++ Builder\{{MODULE_NAME}}Api.cbproj"
set "appSolutionFileFullPath6=!FOLDER_PATH!C++ Builder\{{MODULE_NAME}}Api.cbproj"

REM 빌드 타겟 구성 (Windows x64 / RTX64 4.x Win32 / RTX64 4.x x64 / RTX64 3.0 x64 / C++Builder Win64 / Win32)
set "appBuildTarget1=Windows"
set "appBuildTarget2=RTX64 4.x"
set "appBuildTarget3=RTX64 4.x"
set "appBuildTarget4=RTX64 3.0"
set "appBuildTarget5=Release"
set "appBuildTarget6=Release"
set "appBuildPlatform1=x64"
set "appBuildPlatform2=Win32"
set "appBuildPlatform3=x64"
set "appBuildPlatform4=x64"
set "appBuildPlatform5=Win64"
set "appBuildPlatform6=Win32"

REM NuGet 패키지 복원 필요 여부 (0=불필요)
set "appNugetRequire1=0"
set "appNugetRequire2=0"
set "appNugetRequire3=0"
set "appNugetRequire4=0"
set "appNugetRequire5=0"
set "appNugetRequire6=0"

REM **************************
REM * 변수 선언
REM **************************
set "vsVerName="
set "vsMSBuildFullPath="
set "vsMSBuildFullPath2012=C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe"
set "vsMSBuildFullPath2013=C:\Program Files (x86)\MSBuild\12.0\Bin\MSBuild.exe"
set "vsMSBuildFullPath2015=C:\Program Files (x86)\MSBuild\14.0\Bin\MSBuild.exe"
set "vsMSBuildFullPath2017=C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\MSBuild\15.0\Bin\MSBuild.exe"
set "vsMSBuildFullPath2019=C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe"
set "vsMSBuildFullPath2022=C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe"

REM Visual Studio 메이저 버전 번호 → 연도명 매핑
set "vsMajorVerToName11=2012"
set "vsMajorVerToName12=2013"
set "vsMajorVerToName14=2015"
set "vsMajorVerToName15=2017"
set "vsMajorVerToName16=2019"
set "vsMajorVerToName17=2022"

REM Embarcadero RAD Studio 내부 버전 (C++Builder 빌드에 사용)
set "radStudioInternalVersion=15.0"

REM 로그 파일명: 스크립트명_날짜_시간.log
set "CURDATE=%date%"
set "CURDATE=%CURDATE: =_%"
set "CURDATE=%CURDATE:/=_%"
set "HOUR=%time:~0,2%"
set "MINUTE=%time:~3,2%"
set "SECOND=%time:~6,2%"
set "LOGFILENAME=%~n0_%CURDATE%_%HOUR: =0%-%MINUTE: =0%-%SECOND: =0%.log"

REM **************************
REM * 빌드 루프
REM **************************
echo [Info]  Rebuild...(Please wait a moment.)
echo;
set /a TargetNumber=0
set /a RetCode=0

:FOREACH_BUILD
set /a TargetNumber=TargetNumber+1
set "appSolutionFileFullPath=!appSolutionFileFullPath%TargetNumber%!"
set "appBuildTarget=!appBuildTarget%TargetNumber%!"
set "appBuildPlatform=!appBuildPlatform%TargetNumber%!"
set "appNugetRequire=!appNugetRequire%TargetNumber%!"
set "cppBuilder=0"
set "PATH_BAK=%PATH%"

REM 타겟 카운트 초과 시 루프 종료
if %TargetNumber% gtr %TargetCount% goto :FOREACH_BUILD_END

if not "!appSolutionFileFullPath!"=="" (
    call :GetVisualStudioVersion "!appSolutionFileFullPath!"
    if !vsMSBuildFullPath!==!nullStr! (
        echo [Error] Visual Studio 버전이 지원되지 않거나 .sln 형식 오류입니다.
        echo [Error]    Sln      = !appSolutionFileFullPath!
        echo [Error]    Target   = !appBuildTarget!
        echo [Error]    Platform = !appBuildPlatform!
        echo;
        set /a RetCode=1
        goto :FOREACH_BUILD
    )

    if not exist !vsMSBuildFullPath! (
        echo [Error] 필요한 Visual Studio 버전이 설치되어 있지 않습니다.
        echo [Error]    Sln      = !appSolutionFileFullPath!
        echo [Error]    Target   = !appBuildTarget!
        echo [Error]    Platform = !appBuildPlatform!
        echo [Error]    RequiredMSBuild = !vsMSBuildFullPath!
        echo;
        set /a RetCode=1
        goto :FOREACH_BUILD
    )

    cd > nul
    if !cppBuilder! equ 1 (
        REM C++Builder 빌드 경로: RAD Studio 환경 변수 설정 후 MSBuild 실행
        set "radStudioBdsFilePath=C:\Program Files (x86)\Embarcadero\Studio\!radStudioInternalVersion!\bin\bds.exe"
        if not exist "!radStudioBdsFilePath!" (
            echo [Info]  필요한 RAD Studio 버전이 설치되어 있지 않아 C++Builder 타겟을 건너뜁니다.
            echo [Info]    Sln      = !appSolutionFileFullPath!
            echo [Info]    Target   = !appBuildTarget!
            echo [Info]    Platform = !appBuildPlatform!
            echo [Info]    MSBuild  = !vsMSBuildFullPath!
            echo [Info]    RequiredBdsBin = !radStudioBdsFilePath!
            echo.
            set /a RetCode=1
            goto :FOREACH_BUILD
        )

        REM RAD Studio 환경 변수 설정
        set "BDS=C:\Program Files (x86)\Embarcadero\Studio\!radStudioInternalVersion!"
        set "BDSINCLUDE=C:\Program Files (x86)\Embarcadero\Studio\!radStudioInternalVersion!\include"
        set "BDSCOMMONDIR=C:\Users\Public\Documents\Embarcadero\Studio\!radStudioInternalVersion!"
        set "FrameworkDir=C:\Windows\Microsoft.NET\Framework\v4.0.30319"
        set "FrameworkVersion=v4.5"
        set "FrameworkSDKDir="
        set "PATH=%FrameworkDir%;%FrameworkSDKDir%;C:\Program Files (x86)\Embarcadero\Studio\!radStudioInternalVersion!\bin;C:\Program Files (x86)\Embarcadero\Studio\!radStudioInternalVersion!\bin64;C:\Program Files (x86)\Embarcadero\Studio\!radStudioInternalVersion!\cmake;%PATH%"
        set "LANGDIR=JA"
        set "PLATFORM="
        set "PlatformSDK="
        "!vsMSBuildFullPath!" /v:diag "%appSolutionFileFullPath%" /t:Build /p:"Config=%appBuildTarget%" /p:"Platform=%appBuildPlatform%" >> "%LOGFILENAME%" 2>&1
        if not !ERRORLEVEL! equ 0 (
            REM Win64 첫 빌드 실패 버그 우회: /t:Make 로 재시도
            "!vsMSBuildFullPath!" "%appSolutionFileFullPath%" /v:diag /t:Make /p:"Config=%appBuildTarget%" /p:"Platform=%appBuildPlatform%" >> "%LOGFILENAME%" 2>&1
        )
        REM RAD Studio 환경 변수 정리
        set "BDS="
        set "BDSINCLUDE="
        set "BDSCOMMONDIR="
        set "FrameworkDir="
        set "FrameworkVersion="
        set "FrameworkSDKDir="
        set "PATH=!PATH_BAK!"
        set "LANGDIR="
        set "PLATFORM="
        set "PlatformSDK="
    ) else (
        REM 일반 Visual Studio 빌드
        if !appNugetRequire! equ 1 (
            REM NuGet 패키지 복원 필요 시
            "!vsMSBuildFullPath!" "%appSolutionFileFullPath%" /v:diag /t:Rebuild /p:RestorePackagesConfig=true /p:Configuration="%appBuildTarget%";Platform="%appBuildPlatform%" >> "%LOGFILENAME%" 2>&1
        ) else (
            "!vsMSBuildFullPath!" "%appSolutionFileFullPath%" /v:diag /t:Rebuild /p:Configuration="%appBuildTarget%";Platform="%appBuildPlatform%" >> "%LOGFILENAME%" 2>&1
        )
    )

    if not !ERRORLEVEL! equ 0 (
        echo [Error] 빌드 실패. MSBuild 오류 코드=!ERRORLEVEL!
        echo [Error]    Sln      = !appSolutionFileFullPath!
        echo [Error]    Target   = !appBuildTarget!
        echo [Error]    Platform = !appBuildPlatform!
        echo [Error]    MSBuild  = !vsMSBuildFullPath!
        echo;
        set /a RetCode=1
        goto :FOREACH_BUILD
    ) else (
        echo [Info] 빌드 성공.
        echo [Info]    Sln      = !appSolutionFileFullPath!
        echo [Info]    Target   = !appBuildTarget!
        echo [Info]    Platform = !appBuildPlatform!
        echo [Info]    MSBuild  = !vsMSBuildFullPath!
        echo;
    )

    goto :FOREACH_BUILD
)

:FOREACH_BUILD_END
echo [Info]  완료.
pause

exit /b !RetCode!

REM **************************
REM * 서브루틴
REM **************************
REM ===================
REM  서브루틴: 문자열 치환
REM ===================
:ReplaceLine
set "line=!line:%~1=%~2!"
exit /b

REM ===================
REM  서브루틴: Visual Studio 버전 감지
REM  .sln 파일 또는 .cbproj 파일에서 VS 버전을 자동 탐지하여
REM  vsMSBuildFullPath 변수에 MSBuild 경로를 설정합니다.
REM ===================
:GetVisualStudioVersion
set "vsMSBuildFullPath="
set "slnLine="
set "nullStr="
set "vsVerMajorNum="
set "vsVerName="
set "replace1=VisualStudioVersion "
set "replace1Exclude1=Minimum"
set "replace1Exclude2=Maximum"
set "replace2=Visual Studio"
set "replace2Exclude1=Solution"
set "replace3=Visual Studio Version"
set "loop=1"

REM .cbproj 파일이면 C++Builder 빌드로 처리
echo "%~1" | findstr /i /c:".cbproj" >nul && (
    set "vsMSBuildFullPath=%vsMSBuildFullPath2012%"
    set /a cppBuilder=1
    exit /b
)

REM "VisualStudioVersion" 키 탐색
for /f "tokens=* usebackq delims=" %%a in ("%~1") do (
    set "slnLine=%%a"
    set "line=%%a"
    call :ReplaceLine "!replace1!",!nullStr!
    if not "!line!" == "%%a" (
        set "line=%%a"
        call :ReplaceLine "!replace1Exclude1!",!nullStr!
        if "!line!" == "%%a" (
            set "line=%%a"
            call :ReplaceLine "!replace1Exclude2!",!nullStr!
            if "!line!" == "%%a" (
                set "slnLine=!slnLine:.=,!"
                for %%y in (!slnLine!) do (
                    if !loop!==2 (
                        set "vsVerMajorNum=%%y"
                        goto :breakVsMajor
                    )
                    set /a loop=loop+1
                )
            )
        )
    )
)

REM "# Visual Studio Version" 키 탐색
for /f "tokens=* usebackq delims=" %%a in ("%~1") do (
    set "line=%%a"
    call :ReplaceLine "!replace3!",!nullStr!
    if not "!line!"=="%%a" (
        set "line=%%a"
        for %%y in (%%a) do (
            if !loop!==5 (
                set "vsVerName=%%y"
                goto :breakVsName
            )
            set /a loop=loop+1
        )
    )
)

REM "# Visual Studio" 키 탐색
for /f "tokens=* usebackq delims=" %%a in ("%~1") do (
    set "line=%%a"
    call :ReplaceLine "!replace2!",!nullStr!
    if not "!line!"=="%%a" (
        set "line=%%a"
        call :ReplaceLine "!replace2Exclude1!",!nullStr!
        if "!line!" == "%%a" (
            for %%y in (%%a) do (
                if !loop!==4 (
                    set "vsVerName=%%y"
                    goto :breakVsName
                )
                set /a loop=loop+1
            )
        )
    )
)
goto :breakGetVsVer

:breakVsMajor
for /l %%a in (1, 1, 20) do (
    if %%a == !vsVerMajorNum! (
        set "vsVerName=!vsMajorVerToName%%a!"
        set "vsMSBuildFullPath=!vsMSBuildFullPath!vsVerName!!"
    )
)
for /l %%a in (2000, 1, 2050) do (
    if %%a == !vsVerName! (
        set "vsMSBuildFullPath=!vsMSBuildFullPath%%a!"
    )
)
goto :breakGetVsVer

:breakVsName
REM "# Visual Studio 14" 와 "# Visual Studio 2015" 모두 가능하므로 양쪽 매핑 처리
for /l %%a in (1, 1, 20) do (
    if %%a == !vsVerName! (
        set "vsVerName=!vsMajorVerToName%%a!"
        set "vsMSBuildFullPath=!vsMSBuildFullPath!vsVerName!!"
    )
)
for /l %%a in (2000, 1, 2050) do (
    if %%a == !vsVerName! (
        set "vsMSBuildFullPath=!vsMSBuildFullPath%%a!"
    )
)
goto :breakGetVsVer

:breakGetVsVer
if !vsMSBuildFullPath!==!nullStr! (
    exit /b 19
)

exit /b
