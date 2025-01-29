<!-- Copyright [2019] [Integreat Project] -->
<!-- Copyright [2023] [YCMS] -->
<!---->
<!-- Licensed under the Apache License, Version 2.0 (the "License"); -->
<!-- you may not use this file except in compliance with the License. -->
<!-- You may obtain a copy of the License at -->
<!---->
<!--     http://www.apache.org/licenses/LICENSE-2.0 -->
<!---->
<!-- Unless required by applicable law or agreed to in writing, software -->
<!-- distributed under the License is distributed on an "AS IS" BASIS, -->
<!-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. -->
<!-- See the License for the specific language governing permissions and -->
<!-- limitations under the License. -->
[![CircleCI](https://circleci.com/gh/charludo/ycms.svg?style=shield)](https://circleci.com/gh/charludo/ycms)
[![ReadTheDocs](https://readthedocs.org/projects/ycms/badge/?version=latest)](https://ycms.readthedocs.io/en/latest/)

# HospiTool
Hospitals face the challenge of efficiently managing patient stays, medical records, bed allocations and patient data. Existing digital solutions are often complicated and not very intuitive. Although algorithms for automatic bed allocation already exist,
an interface to hospital information systems to use them effectively has been missing until now. Our software offers a user-friendly solution that is specifically optimized for bed management to close this gap.

## Installation

This section describes how to setup a development environment to start contributing to this project. There are currently two ways to install HospiTool, but both methods require you to have Docker installed on your system.
Windows users should use the newest Version of [Docker Desktop](https://www.docker.com/products/docker-desktop/), Linux users should use [Docker Engine](https://docs.docker.com/engine/install/) (including the docker compose plugin).

### Pure Docker installation (Recommended)
```
git clone git@github.com:JonasDju/HospiTool.git
cd HospiTool
docker compose --profile dev up
```
Building and starting the container for the first time will take several minutes. Subsequent runs of the project will start much faster.
While the container is running, the WebUI can be accessed via `http://localhost:8086`. Any changes made to the source code or templates will be visible in real time without stopping the container.
The containers can be stopped using `Ctrl+C`. If you wish to reset the database, use `docker compose --profile dev down` after stopping the containers.

After changing or adding any translation strings inside .py or .html files, you need to stop the container (`Ctrl+C`), make manual modifications to the translation file located at `hospitool/locale/de/LC_MESSAGES/django.po` and then restart the container using `docker compose --profile dev up`.

After implementing some new features, you should add corresponding test cases. Tests are located in the `tests/` directory.
To run existing tests, open a new terminal (while the containers are running) and execute `docker compose exec hospitool-dev ./test.sh`. If you wish to only execute tests affected by recent changes, append the `--changed` flag to the former command.

### Local installation
**Note:** if you absolutely MUST use Windows, follow the guide in `WSL.md`. No guarantees though.

For Linux and Mac users, the following packages are required before installing the project (install them with your package manager):

* `npm` version 7 or later
* `nodejs` version 12 or later
* `python3` version 3.9 or later
* `python3-pip` (Debian-based distributions) / `python-pip` (Arch-based distributions)
* `python3-venv` (only on Debian-based distributions)

If you want to use the "suggest assignment" functionality, additional steps are needed before installing HospiTool:
- clone [TabeaBrandt/patient-to-room_assignment](https://github.com/TabeaBrandt/patient-to-room_assignment/tree/main) in a folder where you will later clone this repository
- inside `patient-to-room_assignment`, do
    - `python -m venv .venv`
    - `. .venv/bin/activate`
    - `pip install gurobipy`

Continue with the installation of the HospiTool project:
````
git clone git@github.com:JonasDju/HospiTool.git
cd HospiTool
./tools/install.sh --pre-commit
````

Your folder structure should look like this now:
```
some_folder/
├─ patient-to-room_assignment/
│  └─ ...
└─ HospiTool/
   ├─ docker
   ├─ docs
   └─ ...
```

Next, the translation files should be compiled with `./tools/translate.sh` to make sure that the german translation is available.
To start the development server, run: `./tools/run.sh`
Any changes made to the code or the templates will be visible in real time. If you wish to reset the database, delete the `.postgres` folder inside the `HospiTool` directory.

After changing or adding any translation strings inside .py or .html files, you are required to update the translation file using `./tools/tranlsate.sh --skip-compile`, make manual modifications to the updated file located at `hospitool/locale/de/LC_MESSAGES/django.po` and then compile the changes using `./tools/tranlsate.sh`. You can check if you forgot some manual translations by running `./tools/check_tranlsations.sh`.

After implementing some new features, you should add corresponding test cases. Tests are located in the `tests/` directory.
To run existing tests, open a new terminal and execute `./tools/test.sh`. If you wish to only execute tests affected by recent changes, append the `--changed` flag to the former command.

## Patient-to-Room Assignment Algorithm
If you want to run the patient-to-room assignment (PRA) algorithm, you need to download a gurobi [WLS license](https://support.gurobi.com/hc/en-us/articles/13232844297489-How-do-I-set-up-a-Web-License-Service-WLS-license) file (`gurobi.lic`) 
and place it inside the `gurobi` folder. An academic or commercial WLS license is needed.
See this [article](https://www.gurobi.com/features/academic-wls-license/) on how to create and download the license file. Please note, that other license types (like the Academic Named-User License) do not work, as they cannot be used inside containers.

You can check if you have the correct type of license file by opening it in a text editor. The content of your `gurobi.lic` file should look like this:
```
WLSACCESSID=203dec48-e3f8-46ac-0184-92d7d6ded944
WLSSECRET=a080cce8-4e01-4e36-955e-61592c5630db
LICENSEID=12127
```


## Using the WebUI

* Install and run the server using one of the options above
* Go to your browser and open the URL `http://localhost:8086`
* By default, the following users exist:

| Personnel ID | Group              |
|--------------|--------------------|
| ROOT_00001   | -                  |
| ZBM_000001   | ZBM                |
| STATION_MG   | STATION_MANAGEMENT |
| DR_0000001   | MEDICAL_PERSONNEL  |
| NURSE_0001   | MEDICAL_PERSONNEL  |

All default users share the password `changeme`.

## Documentation

Read the docs at [ycms.readthedocs.io](https://ycms.readthedocs.io/en/latest/).


## License

This project is licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0), see [LICENSE](./LICENSE) and [NOTICE.md](./NOTICE.md).
It is based on [digitalfabrik/integreat_cms](https://github.com/digitalfabrik/integreat-cms/), Copyright © 2023 [Tür an Tür - Digitalfabrik gGmbH](https://github.com/digitalfabrik) and [individual contributors](https://github.com/digitalfabrik/integreat-compass/graphs/contributors).
All rights reserved.
