'''Python script for Resource group'''
import logging
from ignition.model.lifecycle import LifecycleExecuteResponse
from ignition.service.resourcedriver import ResourceDriverError
from azuredriver.service.common import CREATE_REQUEST_PREFIX, build_request_id
from azuredriver.service.azureresourcemanager import AzureResourceManager
from azuredriver.service.topology import AZUREAssociatedTopology
import re

logger = logging.getLogger(__name__)


class ResourceGroupResourceManager(AzureResourceManager):
    """
    This is a class for Resource Group.
    """

    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        '''This method is used to create resource group'''
        logger.info(
            f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        self.validate_name(resource_properties.get('resourcegroup_name'))
        stack_id = self.get_stack_id(resource_properties, azure_location)
        if stack_id is None:
            resourcemanager_driver = azure_location.resourcemanager_driver
            # Create resource name
            resource_name = super().create_resource_name(
                system_properties, self.get_resource_name(system_properties), None)
            try:
                # create resource/deployment
                stack_id = resourcemanager_driver.create_resourcegroup(resource_properties.get(
                    'resourcegroup_name'), resource_properties.get('resourcegroup_location'))
                logger.info('Created Stack Id: %s', stack_id)
            except Exception as ex:
                raise ResourceDriverError(str(ex)) from ex

            if stack_id is None:
                raise ResourceDriverError(
                    'Failed to create deployment in azure')

        request_id = build_request_id(CREATE_REQUEST_PREFIX, stack_id)
        associated_topology = AZUREAssociatedTopology()
        associated_topology.add_stack_id(resource_name, stack_id)
        return LifecycleExecuteResponse(request_id, associated_topology=associated_topology)

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        '''This method is used to remove resource group'''
        return super().remove(resource_id, lifecycle_name, system_properties,
        resource_properties, request_properties, associated_topology, azure_location)

    def validate_name(self, resourcegroup_name):
        '''This method is used to validate resource group name.'''
        resgrp_name_len = len(resourcegroup_name)
        if (resgrp_name_len < 1 or resgrp_name_len > 64) or (not bool(re.match('^[a-zA-Z0-9\-_]*$', resourcegroup_name))):
            raise ValueError(
                'Invalid resource group name value provided. Resource group name must be between 1 and 64 characters in length and use numbers, letters and special characters like (-_) only')
