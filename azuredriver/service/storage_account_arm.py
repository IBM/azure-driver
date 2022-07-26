'''Python script for Storage Account'''
import logging
from azuredriver.service.azureresourcemanager import AzureResourceManager

logger = logging.getLogger(__name__)


class StorageAccountResourceManager(AzureResourceManager):
    '''This class is used to manage storage account'''
    logger.debug("Loading StorageAccountResourceManager")
    # Will create a VPC using a Cloudformation template

    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(
            f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')

        self.validate_storage_account_name(
            resource_properties.get('storage_account_name'))
        return super().create(resource_id, lifecycle_name, driver_files,
        system_properties, resource_properties, request_properties,
        associated_topology, azure_location, 'arm_storage_account.json', 'arm_storage_account_parameters.json')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        super().create_resource_name(system_properties,
                                     self.get_resource_name(system_properties), None)
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties,
        resource_properties, request_properties, associated_topology, azure_location)

    def validate_storage_account_name(self, storage_account_name):
        '''This method is used to validate storage account name'''
        if not storage_account_name.isalnum():
            raise ValueError(
                'Invalid storage account name value provided. Use numbers and lower-case letters')
