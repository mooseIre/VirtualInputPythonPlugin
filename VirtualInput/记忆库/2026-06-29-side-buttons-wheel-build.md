# 2026-06-29 side buttons and wheel build

## Goal

- Add Python/driver support for mouse side buttons X1/X2.
- Add relative vertical wheel support.
- Build Release x64 and refresh `InputBridge-Package.zip`.

## Code changes

- Relative mouse report changed from 4 bytes to 5 bytes: `reportId, buttons, x, y, wheel`.
- Relative mouse buttons expanded from Button 1-3 to Button 1-5.
- Added HID Wheel usage `0x38` to the relative mouse input report.
- Python wrapper now selects the 5-byte relative mouse output collection.
- Added `BUTTON_X1`, `BUTTON_X2`, `mouse_wheel()`, `wheel_up()`, and `wheel_down()`.

## Build environment notes

Installed with winget:

```powershell
winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --accept-package-agreements --accept-source-agreements --silent --override "--wait --quiet --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK.22621 --add Microsoft.VisualStudio.Component.VC.CMake.Project --includeRecommended --norestart"
winget install --id Microsoft.WindowsWDK.10.0.22621 --exact --accept-package-agreements --accept-source-agreements --silent
winget install --id Microsoft.WindowsWDK.10.0.26100 --exact --accept-package-agreements --accept-source-agreements --silent
```

VS Build Tools still did not register `WindowsKernelModeDriver10.0` into the protected MSBuild install directory from this non-elevated process. The successful route was to create a local `_build_targets/Microsoft/VC/v170` copy from VS Build Tools and overlay `$MSBuild/Microsoft/VC/v170` from:

```text
C:\Program Files (x86)\Windows Kits\10\Vsix\VS2022\10.0.22621.0\WDK.vsix
```

Then build with:

```powershell
& 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\amd64\MSBuild.exe' .\VirtualInput\InputBridge.vcxproj /t:Build /p:Configuration=Release /p:Platform=x64 /p:VCTargetsPath="C:\Users\moose\Desktop\VirtualInputPythonPlugin\_build_targets\Microsoft\VC\v170\" /p:WindowsTargetPlatformVersion=10.0.26100.0 /p:TargetPlatformVersion=10.0.26100.0 /p:WDKBuildFolder=10.0.26100.0 /p:Driver_SpectreMitigation=false /p:SpectreMitigation=false /p:SignMode=Off /p:DriverSign=false /p:RunInf2Cat=false /p:EnableInf2Cat=false /v:minimal
```

This produced:

```text
VirtualInput\x64\Release\InputBridge.sys
VirtualInput\x64\Release\InputBridge.inf
```

## Signing and package

Created a current-user code signing cert:

```powershell
New-SelfSignedCertificate -Type CodeSigningCert -Subject 'CN=InputBridge Test Certificate' -CertStoreLocation Cert:\CurrentUser\My -KeyExportPolicy Exportable -KeyUsage DigitalSignature -HashAlgorithm SHA256 -NotAfter (Get-Date).AddYears(5)
```

Generated catalog:

```powershell
Inf2Cat.exe /driver:"C:\Users\moose\Desktop\VirtualInputPythonPlugin\VirtualInput\x64\Release" /os:10_X64
```

Signed catalog with thumbprint:

```text
7EE72563B4C3C2A478998F3220A76735339D7824
```

`signtool verify` reports the self-signed chain is not trusted until the package install script imports `InputBridgeTest.cer` into LocalMachine Root and TrustedPublisher. That is expected before installation.

Updated package:

```text
C:\Users\moose\Desktop\VirtualInputPythonPlugin\InputBridge-Package.zip
```

## Verification

- `py -3 -m py_compile` passed for source Python files and package Python files.
- `InputBridge-Package.zip` was recreated and successfully expanded for inspection.
- Package includes updated `driver/InputBridge.sys`, `driver/InputBridge.inf`, `driver/InputBridge.cat`, `driver/InputBridgeTest.cer`, Python wrapper, example, README, smoke test, `manage-driver.bat`, uninstall helper, and `devcon.exe`.
