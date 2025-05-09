@ECHO OFF

setlocal

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=_build
set SPHINXOPTS=-j auto -W --keep-going -w build_errors.txt -N -q

if "%1" == "" goto help
if "%1" == "clean" goto clean

python api_rstgen.py

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
xcopy /s "%SOURCEDIR%\_static\sphx_glr_post_processing_exhaust_manifold_011.png" "%BUILDDIR%\html\_images\" /Y
xcopy /s "%SOURCEDIR%\_static\sphx_glr_post_processing_exhaust_manifold_012.png" "%BUILDDIR%\html\_images\" /Y
goto end

:clean
rmdir /s /q %BUILDDIR% > /NUL 2>&1
rmdir /s /q %SOURCEDIR%\examples > /NUL 2>&1
for /d /r %SOURCEDIR% %%d in (_autosummary) do @if exist "%%d" rmdir /s /q "%%d"
del build_errors.txt > /NUL 2>&1
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
