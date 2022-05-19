
from ignition.model.lifecycle import LifecycleExecuteResponse
from ignition.service.resourcedriver import ResourceDriverError
from azuredriver.service.common import CREATE_REQUEST_PREFIX, build_request_id
from azuredriver.location import *
from azuredriver.model.exceptions import *
from azuredriver.service.azureresourcemanager import *
from azuredriver.service.topology import AZUREAssociatedTopology
import logging
import json


logger = logging.getLogger(__name__)

class StorageAccountResourceManager(AzureResourceManager):
    logger.debug("Loading StorageAccountResourceManager")
    # Will create a VPC using a Cloudformation template
    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        
        self.validate_storage_account_name(resource_properties.get('storage_account_name'))
        return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, 'arm_storage_account.json', 'arm_storage_account_parameters.json')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        self.__create_resource_name(system_properties, resource_properties, self.get_resource_name(system_properties))
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)

    def __create_resource_name(self, system_properties, resource_properties, resource_name):
        system_properties['resourceName'] = self.get_resource_name(system_properties)
        return system_properties['resourceName']
  
    def validate_storage_account_name(self, storage_account_name):
        if not storage_account_name.isalnum():
            raise ValueError('Invalid storage account name value provided. Use numbers and lower-case letters only')
        


