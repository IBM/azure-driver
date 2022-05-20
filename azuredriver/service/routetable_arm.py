
from ignition.model.lifecycle import LifecycleExecuteResponse
from ignition.service.resourcedriver import ResourceDriverError
from azuredriver.service.common import CREATE_REQUEST_PREFIX, build_request_id
from azuredriver.location import *
from azuredriver.model.exceptions import *
from azuredriver.service.azureresourcemanager import *
from azuredriver.service.topology import AZUREAssociatedTopology
from azuredriver.service.common import CREATE_REQUEST_PREFIX, build_request_id
import logging
import json


logger = logging.getLogger(__name__)

        

class RouteTableResourceManager(AzureResourceManager):
    create_subnetroute_properties = ['route_name', 'route_table_name', 'route_next_hop_type', 'route_address_prefix']
    remove_subnetroute_properties = ['route_name', 'route_table_name']
    logger.debug("Loading RouteTableResourceManager")
    # Will create a VPC using a Cloudformation template
    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties} lifecycle_name={lifecycle_name}')
        return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, 'arm_routetable.json', 'arm_routetable_parameters.json')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        self.__create_resource_name(system_properties, resource_properties, self.get_resource_name(system_properties))
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)

    def __create_resource_name(self, system_properties, resource_properties, resource_name):
        system_properties['resourceName'] = self.get_resource_name(system_properties)
        return system_properties['resourceName']
    
    
    def addroute(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info("Adding route started")
      #  skip_create = self.__is_skip_addsubnetroute_required(azure_location.resourcemanager_driver, resource_properties.get('route_name'), resource_properties.get('subnet_name'), resource_properties.get('local_or_global'))
        return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, 'arm_add_routes.json', 'arm_add_routes_parameters.json', properties_to_validate=RouteTableResourceManager.create_subnetroute_properties, operation_source_name="{}{}".format(resource_properties.get('route_name'),"route"))
       

    def removeroute(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info("Deleting route started")
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, properties_to_validate=RouteTableResourceManager.remove_subnetroute_properties, operation_source_name="{}{}".format(resource_properties.get('route_name'),"route"))
    
    # def addinternetroute(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
    #     logger.info("Adding route started")
    #     skip_create = self.__is_skip_addinternetroute_required(azure_location.resourcemanager_driver, resource_properties.get('route_name'), resource_properties.get('subnet_name'), resource_properties.get('private_or_public'))
    #     return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, 'arm_add_routes.json', 'arm_add_routes_parameters.json', properties_to_validate=RouteTableResourceManager.create_subnetroute_properties, operation_source_name="subnet_route", skip_create=skip_create)
       

    # def removeinternetroute(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
    #     logger.info("Deleting route started")
    #     return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, properties_to_validate=RouteTableResourceManager.remove_subnetroute_properties, operation_source_name="subnet_route") 
        
    # def __create_subnetroute_resource_name(self, route_name, system_properties, resource_name):
    #     system_properties['resourceName'] = self.sanitize_name(resource_name, '__', route_name, 'subnetroute')
    #     return system_properties['resourceName']
    
    # def __is_skip_addinternetroute_required(self, rmclient, route_table_name, subnet_name, private_or_public):
        
    #     route_table = rmclient.get_route_table(route_table_name)
    #     for subnet in route_table.subnets:
    #         subnet_name_from_id = rmclient.get_name_from_stackid(subnet.id)
    #         if subnet_name_from_id == subnet_name:
    #             if private_or_public == 'private':
    #                return False
    #     return True
    
    # def __is_skip_addsubnetroute_required(self, rmclient, route_table_name, subnet_name, local_or_global):
    #     is_skip_required = False
    #     if local_or_global == 'local':
    #        return False
    #     return True
    #    # route_table = rmclient.get_route_table(route_table_name)
    #    # for subnet in route_table.subnets:
    #    #     subnet_name_from_id = rmclient.get_name_from_stackid(subnet.id)
    #    #     if subnet_name_from_id == subnet_name:
    #    #         is_skip_required = True
    #    #         break
    #    # return is_skip_required
    
    
        
