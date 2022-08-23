# Python Application

The Python package in this driver provides a workable application running with Connexion (on top of Flask). The Ignition framework takes care of configuring the application with the APIs and Python objects to handle the requests.

This application is then wrapped by Gunicorn to provide a production ready deployment. 

Gunicorn command is used to run application after deployment, it creates a central master process and worker processes which handle the application.

## Testing 

Unit tests are expected to be included in the `tests/unit` directory of this project and are executed with the `unittest` module of Python. Ensure you have it installed:

```
python3 -m pip install unittest
```

Now execute `unittest` to run the tests, it will detect the unit test files in the `tests` directory:

```
python3 -m unittest
```

## Packaging and Distribution 

The `setup.py` is a standard file required to manage the installation and distribution of a Python application with the popular [setuptools](https://pypi.org/project/setuptools/) module.

This file defines the metadata of the Python package to be built, including any 3rd party Python modules it depends on. It is configured to include all Python files in the `azuredriver` package and any files specified in the `MANIFEST.in`.

This file also specifies the entry points to the application, so a user may run the driver on the command line after installation:
    - `ald-dev` for a development server

To build a distributable package of your application you will need the `setuptools` and `wheel` Python modules:

```
python3 -m pip install --user --upgrade setuptools wheel
```

Run the `setup.py` script at the root of the project to produce a whl (found in `dist/`):

```
python3 setup.py bdist_wheel
```

This whl file can now be used to install your application with Python:

```
python3 -m pip install <path to whl>
```

The command `azuredriver-dev`, `azuredriver`, `azuredriver-gunicorn` and `azuredriver-uswgi` will now be avaiable from the command line.

## Configuration

Ignition loads configuration properties from any sources provided to the application builder. By default this driver is configured to load properties from:

- `azuredriver/config/default_config.yml` - this is the default configuration file, bundled into the distributed version of your application
- `azuredriver_config.yml` - Ignition will search for a configuration file with this name at the directory the application has been started from (ignored if not found)
- `/var/azuredriver/awsdriver_config.yml` - this configuration file is only used in the Helm chart installation. Ignition will search for a configuration file at this path (ignored if not found)
- `AZUREDRIVER_CONFIG` - set this environment variable to a file path and Ignition will load the configuration file (ignored if the environment variable is not set)

This allows the user flexibility in how to configure the application. When running with Python (using `azuredriver-dev` or `azuredriver`) the best approach is to create a `azuredriver_config.yml` file in the current directory or configure `AZUREDRIVER_CONFIG` with a file path.