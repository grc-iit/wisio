@ECHO OFF

pushd %~dp0

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build
set SPHINXOPTS=-W --keep-going

if "%1" == "" goto help
if "%1" == "livehtml" goto livehtml

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
goto end

:livehtml
sphinx-autobuild %SOURCEDIR% %BUILDDIR%\html %SPHINXOPTS% --open-browser
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

:end
popd
