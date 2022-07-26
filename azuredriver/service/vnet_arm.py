'''Python script for VNET ARM'''
import logging
from ignition.model.lifecycle import LifecycleExecuteResponse
from ignition.service.resourcedriver import ResourceDriverError
from azuredriver.service.azureresourcemanager import AzureResourceManager
from azuredriver.service.common import CREATE_REQUEST_PREFIX, build_request_id
from azuredriver.service.topology import AZUREAssociatedTopology


logger = logging.getLogger(__name__)


class VNETResourceManager(AzureResourceManager):
    '''This class is used to manage VNET'''
    logger.info("Loading VNETResourceManager")
    # Will create a VPC using a Cloudformation template

    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(
            f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        return super().create(resource_id, lifecycle_name, driver_files,
        system_properties, resource_properties, request_properties,
        associated_topology, azure_location, 'arm_vnet.json', 'arm_vnet_parameters.json')

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        super().create_resource_name(system_properties,
                                     self.get_resource_name(system_properties), None)
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties,
        resource_properties, request_properties, associated_topology, azure_location)

    def __create_vnet_peering_name(self, system_properties, resource_name, initiator_vnet_name, operation_source_name):
        resource_name = resource_name.replace('VNetResource', initiator_vnet_name)
        if operation_source_name is not None:
            resource_name = resource_name + operation_source_name
        system_properties['resourceName'] = resource_name
        return system_properties['resourceName']

    def __create_vnet_peering_name(self, system_properties, resource_name, initiator_vnet_name, operation_source_name):
        resource_name = resource_name.replace('VNetResource', initiator_vnet_name)
        if operation_source_name is not None:
            resource_name = resource_name + operation_source_name
        system_properties['resourceName'] = resource_name
        return system_properties['resourceName']

    def __create_vnet_peering_name(self, system_properties, resource_name, initiator_vnet_name, operation_source_name):
        resource_name = resource_name.replace('VNetResource', initiator_vnet_name)
        if operation_source_name is not None:
            resource_name = resource_name + operation_source_name
        system_properties['resourceName'] = resource_name
        return system_properties['resourceName']

    def createvnetpeering(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        '''This method is used to create vnet peering'''
        logger.info(
            f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')

        stack_id = self.get_stack_id(resource_properties, azure_location)
        if stack_id is None:
            resourcemanager_driver = azure_location.resourcemanager_driver
            initiator_vnet_name = resource_properties.get('initiator_vnet_name')
            # Create resource name
            resource_name = self.__create_vnet_peering_name(system_properties, self.get_resource_name(system_properties), initiator_vnet_name, "peer")
            try:
                # create resource/deployment
                azure_location.set_resource_group_name(
                    resource_properties.get('initiator_vnet_rg_name'))
                stack_name = self.get_stack_name(resource_id, resource_name)
                arm_template, arm_parameters = self.prepare_deployment_artifacts(
                    system_properties, resource_properties, request_properties,
                     'arm_vnet_peering.json', 'arm_vnet_peering_parameters.json')
                stack_id = resourcemanager_driver.create_deployment(
                    stack_name, arm_template, arm_parameters)
                logger.info(
                    f'stack_name={stack_name} resource_name={resource_name} arm_template={arm_template} arm_parameters={arm_parameters}')
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
    def removevnetpeering(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        initiator_vnet_name = resource_properties.get('initiator_vnet_name')
        self.__create_vnet_peering_name(system_properties, self.get_resource_name(system_properties), initiator_vnet_name, None)
       # azure_location.resourcemanager_driver.delete_vnetpeering(resource_properties.get('initiator_vnet_name'), self.__get_vnet_peering_name(resource_properties.get('initiator_vnet_name'), resource_properties.get('acceptor_vnet_name')))
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, operation_source_name="peer")
  
    def get_vnet_peering_name(self, initiator_vnet_name, acceptor_vnet_name):
        return initiator_vnet_name+"-"+"to"+"-"+acceptor_vnet_name
    
