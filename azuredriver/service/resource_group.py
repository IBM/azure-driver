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

class ResourceGroupResourceManager(AzureResourceManager):
    logger.info("Loading ResourceGroup")
    # Will create a VPC using a Cloudformation template
    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        self.validate_name(resource_properties.get('resourcegroup_name'))
        return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, None, None)

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
       return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)

    def __create_resource_name(self, system_properties, resource_properties, resource_name):
        system_properties['resourceName'] = self.get_resource_name(system_properties)
        return system_properties['resourceName']
  
    def validate_name(self, resourcegroup_name):
        resourcegroup_name_len = len(resourcegroup_name)
        if (resourcegroup_name_len < 1 or resourcegroup_name_len > 64) or (not bool(re.match('^[a-zA-Z0-9\-_]*$', resourcegroup_name))):
             raise ValueError('Invalid resource group name value provided. Resource group name must be between 1 and 64 characters in length and use numbers, letters and special characters like (-_) only')
