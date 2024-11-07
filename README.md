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


## Installation

This section describes how to setup a development environment to start contributing to this project. There are currently two ways to install YCMS, but both methods require you to have Docker installed on your system.
Windows users should use the newest Version of [Docker Desktop](https://www.docker.com/products/docker-desktop/), Linux users should use [Docker Engine](https://docs.docker.com/engine/install/) (including the docker compose plugin).

### Pure Docker installation (Recommended)
```
git clone git@github.com:JonasDju/ycms.git
cd ycms
docker compose --profile dev up
```
Building and starting the container for the first time will take several minutes. Subsequent runs of the project will start much faster.
While the container is running, the WebUI can be accessed via `http://localhost:8086`. Any changes made to the source code or templates will be visible in real time without stopping the container.
The containers can be stopped using `Ctrl+C`. If you wish to reset the database, use `docker compose --profile dev down` after stopping the containers.

### Local installation
**Note:** if you absolutely MUST use Windows, follow the guide in `WSL.md`. No guarantees though.

For Linux and Mac users, the following packages are required before installing the project (install them with your package manager):

* `npm` version 7 or later
* `nodejs` version 12 or later
* `python3` version 3.9 or later
* `python3-pip` (Debian-based distributions) / `python-pip` (Arch-based distributions)
* `python3-venv` (only on Debian-based distributions)

If you want to use the "suggest assignment" functionality, additional steps are needed before installing YCMS:
- clone [TabeaBrandt/patient-to-room_assignment](https://github.com/TabeaBrandt/patient-to-room_assignment/tree/v1) in a folder where you will later clone this repository
- inside `patient-to-room_assignment`, do
    - `python -m venv .venv`
    - `. .venv/bin/activate`
    - `pip install gurobipy`

Continue with the installation of the YCMS project:
````
git clone git@github.com:JonasDju/ycms.git
cd ycms
./tools/install.sh --pre-commit
````

Your folder structure should look like this now:
```
some_folder/
├─ patient-to-room_assignment/
│  └─ ...
└─ ycms/
   ├─ docker
   ├─ docs
   └─ ...
```

To start the development server, run: `./tools/run.sh`
Any changes made to the code or the templates will be visible in real time. If you wish to reset the database, delete the `.postgres` folder inside the `ycms` directory.


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
