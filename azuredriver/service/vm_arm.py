'''Python script for VM ARM'''
import logging
from azuredriver.service.azureresourcemanager import *


logger = logging.getLogger(__name__)


class VMResourceManager(AzureResourceManager):
    '''This class is used to manage VM'''
    logger.debug("Loading VMResourceManager")
    # Will create a VPC using a Cloudformation template

    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(
            f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        super().create_resource_name(system_properties,
                                     self.get_resource_name(system_properties), None)
        return super().remove(resource_id, lifecycle_name, system_properties,
        resource_properties, request_properties, associated_topology, azure_location)
