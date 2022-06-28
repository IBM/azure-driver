'''Python script for VCE ARM'''
import logging
from azuredriver.service.azureresourcemanager import *


logger = logging.getLogger(__name__)


class VCEResourceManager(AzureResourceManager):
    '''This class is used to manage VCE'''
    logger.info("Loading VCEResourceManager")
    # Will create a VCE VM using a Cloudformation template

    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(
            f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        return super().create(resource_id, lifecycle_name, driver_files,
        system_properties, resource_properties, request_properties,
        associated_topology, azure_location, 'arm_vce.json', 'arm_vce_parameters.json')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        super().create_resource_name(system_properties,
                                     self.get_resource_name(system_properties), None)
        return super().remove(resource_id, lifecycle_name, system_properties,
        resource_properties, request_properties, associated_topology, azure_location)

