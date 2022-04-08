
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

class NSGResourceManager(AzureResourceManager):
    create_nsgrule_properties = ['nsg_rule_name', 'network_security_group_name', 'priority']
    logger.debug("Loading NSGResourceManager")
    # Will create a VPC using a Cloudformation template
    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        self.validate_name(resource_properties.get('network_security_group_name'))
        return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, 'arm_nsg.json', 'arm_nsg_parameters.json')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        self.__create_resource_name(system_properties, resource_properties, self.get_resource_name(system_properties))
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)

    def __create_resource_name(self, system_properties, resource_properties, resource_name):
        system_properties['resourceName'] = self.get_resource_name(system_properties)
        return system_properties['resourceName']
    
    # def addinternetrule(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
    #     logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
    #     self.validate_name(resource_properties.get('nsg_rule_name'))
    #     skip_create = self.__is_skip_internetrule_required(azure_location.resourcemanager_driver, resource_properties.get('network_security_group_name'), resource_properties.get('subnet_name'), resource_properties.get('private_or_public'))
    #     return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, 'arm_security_group_rules.json', 'arm_security_group_rules_parameters.json', properties_to_validate=NSGResourceManager.create_nsgrule_properties, operation_source_name='ir', skip_create=skip_create)

    # def removeinternetrule(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
    #     skip_delete = self.__is_skip_internetrule_required(azure_location.resourcemanager_driver, resource_properties.get('network_security_group_name'), resource_properties.get('subnet_name'), resource_properties.get('private_or_public'))
    #     return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, operation_source_name='ir', skip_delete=skip_delete)
    
    # def addnsgrule(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
    #     logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
    #     self.validate_name(resource_properties.get('nsg_rule_name'))
    #     skip_create = self.__is_skip_nsgrule_required(azure_location.resourcemanager_driver, resource_properties.get('network_security_group_name'), resource_properties.get('subnet_name'), resource_properties.get('local_or_global'))
    #     return super().create(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, 'arm_security_group_rules.json', 'arm_security_group_rules_parameters.json', properties_to_validate=NSGResourceManager.create_nsgrule_properties, operation_source_name=self.__get_nsgrule_label_name(resource_properties.get('direction')), skip_create=skip_create)

    # def removensgrule(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
    #     skip_delete = self.__is_skip_nsgrule_required(azure_location.resourcemanager_driver, resource_properties.get('network_security_group_name'), resource_properties.get('subnet_name'), resource_properties.get('local_or_global'))
    #     return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, operation_source_name=self.__get_nsgrule_label_name(resource_properties.get('direction')), skip_delete=skip_delete)
        
    
    # def __create_securityrule_resource_name(self, system_properties, nsg_rule_name, resource_name):
    #     system_properties['resourceName'] = self.sanitize_name(resource_name, '__', nsg_rule_name, 'securityrule')
    #     return system_properties['resourceName']

    def validate_name(self, nsg_name):
        nsg_name_len = len(nsg_name)
        if (nsg_name_len < 1 or nsg_name_len > 80) or (not bool(re.match('^[a-zA-Z0-9\-_.]*$', nsg_name))):
            raise ValueError('Invalid network security group name value provided. Network security group name must be between 1 and 80 characters in length and use numbers, letters and special characters like (-_.) only')
         
         
    # def __is_skip_internetrule_required(self, rmclient, network_security_group_name, subnet_name, private_or_public):
    #     subnet = self.getassociatedsubnet(rmclient, network_security_group_name, subnet_name)
    #     if subnet is not None and private_or_public.lower() == 'private':
    #         return False
    #     return True
        
    
    # def __is_skip_nsgrule_required(self, rmclient, network_security_group_name, subnet_name, local_or_global):
    #     subnet = self.getassociatedsubnet(rmclient, network_security_group_name, subnet_name)
    #     if subnet is not None and local_or_global.lower() == 'local':
    #        return False
    #     return True
         
    
    # def getassociatedsubnet(self, rmclient, network_security_group_name, subnet_name):
    #     try:
    #         network_security_group = rmclient.get_network_security_group(network_security_group_name)
    #         for subnet in network_security_group.subnets:
    #             subnet_name_from_id = rmclient.get_name_from_stackid(subnet.id)
    #             if subnet_name_from_id == subnet_name:
    #                 return subnet
    #         return None
    #     except StackNotFoundError as ex:
    #         raise InfrastructureNotFoundError(f'Cannot find NetworksecurityGroup {network_security_group_name}')
        
    #     except Exception as e:
    #         raise ResourceDriverError(str(e)) from e
        
        
    # def __get_nsgrule_label_name(self, direction):
    #     return "securityrule"+direction
        
        