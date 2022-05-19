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
    
    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):        
        logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        self.validate_name(resource_properties.get('resourcegroup_name'))
        stack_id = self.get_stack_id(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)
        if stack_id is None:
            resourcemanager_driver = azure_location.resourcemanager_driver
            # Create resource name
            resource_name = self.__create_resource_name(system_properties)
            try:                
                # create resource/deployment
                stack_id = resourcemanager_driver.create_resourcegroup(resource_properties.get('resourcegroup_name'), resource_properties.get('resourcegroup_location'))
                logger.info(f'Created Stack Id: {stack_id}')
            except Exception as e:
                raise ResourceDriverError(str(e)) from e

            if stack_id is None:
                raise ResourceDriverError('Failed to create deployment in azure')

        request_id = build_request_id(CREATE_REQUEST_PREFIX, stack_id)
        associated_topology = AZUREAssociatedTopology()
        associated_topology.add_stack_id(resource_name, stack_id)
        return LifecycleExecuteResponse(request_id, associated_topology=associated_topology)

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
       return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)

    def __create_resource_name(self, system_properties):
        system_properties['resourceName'] = self.get_resource_name(system_properties)
        return system_properties['resourceName']
  
    def validate_name(self, resourcegroup_name):
        resourcegroup_name_len = len(resourcegroup_name)
        if (resourcegroup_name_len < 1 or resourcegroup_name_len > 64) or (not bool(re.match('^[a-zA-Z0-9\-_]*$', resourcegroup_name))):
             raise ValueError('Invalid resource group name value provided. Resource group name must be between 1 and 64 characters in length and use numbers, letters and special characters like (-_) only')
