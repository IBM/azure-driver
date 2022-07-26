'''Python script for NSG ARM'''
import logging
import re
from azuredriver.service.azureresourcemanager import AzureResourceManager

logger = logging.getLogger(__name__)


class NSGResourceManager(AzureResourceManager):
    '''This class is used to maintain NSG'''
    create_nsgrule_properties = ['nsg_rule_name',
                                 'network_security_group_name', 'priority']
    logger.debug("Loading NSGResourceManager")
    # Will create a VPC using a Cloudformation template

    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(
            f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        self.validate_name(resource_properties.get(
            'network_security_group_name'))
        return super().create(resource_id, lifecycle_name, driver_files,
        system_properties, resource_properties, request_properties,
        associated_topology, azure_location, 'arm_nsg.json', 'arm_nsg_parameters.json')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        super().create_resource_name(system_properties,
                                     self.get_resource_name(system_properties), None)
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties,
        resource_properties, request_properties, associated_topology, azure_location)

    def validate_name(self, nsg_name):
        '''This method is used to validate NSG name'''
        if not bool(re.match('^[a-zA-Z0-9\-_.]*$', nsg_name)):
            raise ValueError(
                'Invalid network security group name value provided. Use numbers, letters and special characters like (-_.) only')
