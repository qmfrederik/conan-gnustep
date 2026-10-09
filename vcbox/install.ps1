# Mark the network profile as private, so inbound connections (e.g. SSH) work correctly
Get-NetConnectionProfile -Name Network | Set-NetConnectionProfile -NetworkCategory Private

# Because the Vagrant user has Administrator privileges, the authorized keys are stored in
# C:\ProgramData\ssh\administrators_authorized_keys
copy "C:\Users\vagrant\.ssh\authorized_keys" "C:\ProgramData\ssh\administrators_authorized_keys"

# Install Chocolatey
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install LLVM
choco install -y llvm

# Install the Visual Studio 2022 build tools, and then add the C++ build tools workload
choco install -y visualstudio2022buildtools
choco install -y visualstudio2022-workload-vctools

# Install git and gpg
choco install -y git
git config --global credential.credentialStore dpapi 
choco install -y gnupg

# Install Conan
choco install -y conan

# Install Cmake, ninja
choco install -y cmake ninja

# Disable anti-virus scanning for the C:\Users\vagrant folder
Add-MpPreference -ExclusionPath "$env:USERPROFILE"
