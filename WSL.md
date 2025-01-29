# Installing the project in WSL

Note: please only use this if you absolutely must work under Windows. If you are dual booting Linux or have a WM setup, that is much preferred (and might be easier than the installation process below.......)

## If you have not yet configured WSL:

- make sure "Virtual Machine Platform" and "Windows Subsystem for Linux" are activated in Windows Features (Just press start and search "Windows Features") and that you are using PowerShell for the following commands
- install WSL: `wsl --install`
- set a username and password when prompted
- update system: `sudo apt update && sudo apt upgrade`

## Install project prerequisites:

- `sudo apt install npm python3 python3-pip python3-venv gettext pcregrep`
- `sudo pip3 install pre-commit`
- `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash`
- press `Ctrl+d` to exit
- `wsl --shutdown`
- `wsl`
- `nvm install lts/hydrogen`

## Setup docker:

- install Docker Desktop on Windows: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
- during installation, make sure that "use WSL2 instead of Hyper-V" is checked
- log out, log in, open docker, skip the sign up
- go to Settings > Resources > WSL integration, ensure your WSL is selected, "Apply & Restart"

## Configure github credentials inside WSL:

- (or handle this from Windows, your choice)
- easiest: `sudo apt install gh`, then `gh auth login` and follow the steps (make sure to select SSH)

## Install the project:

- `git clone git@github.com:JonasDju/HospiTool.git`
- `cd HospiTool`
- `nvm use node`
- `./tools/install.sh --pre-commit --python=python3` (since Ubuntu ships with 3.10 instead of the default 3.9 from the script...)

## Run the project:

- every time you want to run the project after having been logged in, run nvm use node
- `./tools/run.sh`
- open your browser to `http://localhost:8086`

## If you are working with VSCode:

- VSCode should automatically prompt you to install the "WSL" plugin, otherwise do so manually
- install the "Remote Development" plugin (it's an official plugin from Microsoft)
- (while you are at it, make sure you also have plugins for eslint, pylint, djlint, black, and prettier...)
- in the bottom left, you should now have a button where you can "Connect to WSL"
- in the Explorer tab, select your project folder where you cloned it
