
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

class PublicIPResourceManager(AzureResourceManager):
    logger.debug("Loading PublicIPResourceManager")
    # Will create a VPC using a Cloudformation template
    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        logger.info(f'resource_id={resource_id} system_properties={system_properties} resource_properties={resource_properties} request_properties={request_properties}')
        stack_id = self.get_stack_id(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)
        if stack_id is None:
            resourcemanager_driver = azure_location.resourcemanager_driver
            self.resource_group_name(azure_location, resource_properties)
            resource_name = self.__create_resource_name(system_properties, resource_properties, self.get_resource_name(system_properties))
            stack_name = self.get_stack_name(resource_id, resource_name)
            logger.info(f'StackName: {stack_name}')
            arm_template = self.get_arm_template('arm_public_ip_group.json')
            arm_json_template = self.render_template(system_properties, resource_properties, request_properties, 'arm_public_ip_parameters.json')
            logging.info(f'Rendered template: {arm_json_template}')
            #arm_parameters = self.get_arm_parameters(resource_properties, system_properties, azure_location, arm_json_template)
            arm_parameters = json.loads(arm_json_template)
            arm_parameters = arm_parameters['parameters']
            logger.debug(f'stack_name={stack_name} cf_template={arm_template} arm_parameters={arm_parameters}')

            try:
                stack_id = resourcemanager_driver.create_deployment(stack_name, arm_template, arm_parameters)
                logger.info(f'Created Stack Id: {stack_id}')
            except Exception as e:
                raise ResourceDriverError(str(e)) from e

            if stack_id is None:
                raise ResourceDriverError('Failed to create deployment in azure')

        request_id = build_request_id(CREATE_REQUEST_PREFIX, stack_id)
        associated_topology = AZUREAssociatedTopology()
        associated_topology.add_stack_id(resource_name, stack_id)
        return LifecycleExecuteResponse(request_id, associated_topology=associated_topology)

    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        self.__create_resource_name(system_properties, resource_properties, self.get_resource_name(system_properties))
        return super().remove(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)

    def __create_resource_name(self, system_properties, resource_properties, resource_name):
        system_properties['resourceName'] = self.get_resource_name(system_properties)
        return system_properties['resourceName']
  
