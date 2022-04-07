
from azuredriver.location import *
from azuredriver.model.exceptions import *
from azuredriver.service.azureresourcemanager import *
import logging
import json


logger = logging.getLogger(__name__)

class VNETResourceManager(AzureResourceManager):
    logger.info("Loading VNETResourceManager")
    # Will create a VPC using a Cloudformation template
    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, 'arm_vnet.json', 'arm_vnet_parameters.json')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        self.__create_resource_name(system_properties, resource_properties, self.get_resource_name(system_properties))
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)

    def __create_resource_name(self, system_properties, resource_properties, resource_name):
        system_properties['resourceName'] = self.get_resource_name(system_properties)
        return system_properties['resourceName']
    
    def createvnetpeering(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, 'arm_vnet_peering.json', 'arm_vnet_peering_parameters.json', operation_source_name="vnet_peering")
    
    def removevnetpeering(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        self.__create_resource_name(system_properties, resource_properties, self.get_resource_name(system_properties))
       # azure_location.resourcemanager_driver.delete_vnetpeering(resource_properties.get('initiator_vnet_name'), self.__get_vnet_peering_name(resource_properties.get('initiator_vnet_name'), resource_properties.get('acceptor_vnet_name')))
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, operation_source_name="vnet_peering")
  
    def get_vnet_peering_name(self, initiator_vnet_name, acceptor_vnet_name):
        return initiator_vnet_name+"-"+"to"+"-"+acceptor_vnet_name
    
