'''App Script'''
import pathlib
import os
import ignition.boot.api as ignition
import azuredriver.config as driverconfig
from azuredriver.service.resourcedriver import ResourceDriverHandler


DEFAULT_CONFIG_DIR_PATH = str(pathlib.Path(driverconfig.__file__).parent.resolve())
default_config_path = os.path.join(DEFAULT_CONFIG_DIR_PATH, 'default_config.yml')


def create_app():
    '''This method is used to create app'''
    app_builder = ignition.build_resource_driver('AZURE Driver')
    app_builder.include_file_config_properties(default_config_path, required=True)
    app_builder.include_file_config_properties('./azuredriver_config.yml', required=False)
    # custom config file e.g. for K8s populated from Helm chart values
    app_builder.include_file_config_properties('/var/azuredriver/azuredriver_config.yml', required=False)
    app_builder.include_environment_config_properties('AZUREDRIVER_CONFIG', required=False)

    app_builder.add_service(ResourceDriverHandler)
    return app_builder.configure()


def init_app():
    '''This method is used to initialize app'''
    app = create_app()
    return app.run()
