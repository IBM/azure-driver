'''Python script for Route Table'''
import logging
from azuredriver.service.azureresourcemanager import AzureResourceManager

logger = logging.getLogger(__name__)


class RouteTableResourceManager(AzureResourceManager):
    '''This class is used to manage route tables'''
    create_subnetroute_properties = [
        'route_name', 'route_table_name', 'route_next_hop_type', 'route_address_prefix']
    remove_subnetroute_properties = ['route_name', 'route_table_name']
    logger.debug("Loading RouteTableResourceManager")
    # Will create a VPC using a Cloudformation template

    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(
            f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties} lifecycle_name={lifecycle_name}')
        return super().create(resource_id, lifecycle_name, driver_files,
        system_properties, resource_properties, request_properties, associated_topology,
        azure_location, 'arm_routetable.json', 'arm_routetable_parameters.json')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        super().create_resource_name(system_properties,
                                     self.get_resource_name(system_properties), None)
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties,
        resource_properties, request_properties, associated_topology, azure_location)
