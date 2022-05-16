import logging
from pathlib import Path
import re
import os
import uuid
import json
import fnmatch
from azuredriver.service.common import DELETE_REQUEST_PREFIX
from azuredriver.service.common import CREATE_REQUEST_PREFIX, build_request_id
from ignition.model.lifecycle import LifecycleExecuteResponse
from ignition.service.templating import ResourceTemplateContextService, Jinja2TemplatingService
from ignition.service.resourcedriver import InfrastructureNotFoundError, ResourceDriverError, InvalidRequestError
from ignition.service.framework import interface
from azuredriver.service.topology import AZUREAssociatedTopology
from azure.core.exceptions import *
from azuredriver.model.exceptions import *
from .common import *


driver_directory = here = Path(__file__).parent.parent

logger = logging.getLogger(__name__)

class StackNameCreator:

    def create(self, resource_id, resource_name):
        potential_name = '{0}-{1}'.format(resource_name, resource_id)
        needs_starting_letter = not potential_name[0].isalpha()
        potential_name = re.sub('[^A-Za-z0-9-._]+', '-', potential_name)
        max_size = 64
        if needs_starting_letter:
            potential_name = 's{0}'.format(potential_name)
        if len(potential_name)>max_size:
            potential_name = potential_name[:64]
        return potential_name


class AzureResourceManager():
    def __init__(self):
        self.stack_name_creator = StackNameCreator()
        self.props_merger = PropertiesMerger()
        # Jinja2TemplatingService
        self.templating_service = Jinja2TemplatingService()
        # ResourceTemplateContextService
        self.resource_context_service = ResourceTemplateContextService()

    def sanitize_name(self, *names):
        full_name = ''
        for name in names:
            full_name = full_name + name
        return full_name.replace('-', '')

    def get_stack_name(self, resource_id, resource_name):
        if resource_id is not None and resource_name is not None:
            stack_name = self.stack_name_creator.create(resource_id, resource_name)
        else:
            stack_name = 's' + str(uuid.uuid4())
        return stack_name

    def get_resource_name(self, system_properties):
        resource_name = system_properties.get('resourceName', None)
        if resource_name is None:
            raise InvalidRequestError(f'system_properties.resourceName must be provided')
        return self.sanitize_name(resource_name)
    
    
    def get_stack_id(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location):
        resourcemanager_driver = azure_location.resourcemanager_driver
        stack_id = None
        logger.info(f'resource_id:{resource_id},lifecycle_name:{lifecycle_name},driver_files:{driver_files},system_properties:{system_properties}')
        logger.debug(f'resource_properties:{resource_properties},request_properties:{request_properties},associated_topology: {associated_topology}, azure_location: {azure_location}')

        if 'stack_id' in resource_properties:
            input_stack_id = resource_properties.get('stack_id', None)
            logger.debug(f"stack available {input_stack_id}")
            if input_stack_id != None and len(input_stack_id.strip())!=0 and input_stack_id.strip() != "0":
                try:
                    ##Check for valid stack
                    resourcemanager_driver.get_deployment(input_stack_id.strip())
                except StackNotFoundError as e:
                    raise InfrastructureNotFoundError(str(e)) from e
                else:
                    stack_id = input_stack_id

        return stack_id

    def is_parameter_json(self, arm_template_name):
        return fnmatch.fnmatch(arm_template_name,"*_parameters.json")

    def get_arm_template(self, arm_template_name):
        template_path = os.path.join(driver_directory, 'config', 'json', arm_template_name)
        logger.debug(f'ARM template file path for {arm_template_name} is {template_path}')
        with open(template_path, 'r') as template_path_file:
            if not self.is_parameter_json(arm_template_name):
                template = json.load(template_path_file)
            else:
                template = template_path_file.read()
        return template
    
    
    def render_template(self, system_properties, resource_properties, request_properties, arm_template_name):
        template = self.get_arm_template(arm_template_name)
        return self.templating_service.render(template,
            self.resource_context_service.build(system_properties, resource_properties, request_properties, {}))

    def get_arm_parameters(self, resource_properties, system_properties, azure_location, arm_template):
        input_props = self.props_merger.merge(resource_properties, system_properties)
        return azure_location.get_arm_input_util().filter_used_properties(arm_template, input_props)
    
    def prepare_deployment_artifacts(self, system_properties, resource_properties, request_properties, template_file_name, params_file_name):
        arm_template = self.get_arm_template(template_file_name)
        arm_json_template = self.render_template(system_properties, resource_properties, request_properties, params_file_name)
        logging.info(f'Rendered template: {arm_json_template}')
        arm_parameters = json.loads(arm_json_template)
        arm_parameters = arm_parameters['parameters']
        return arm_template, arm_parameters
    
    
    def validate_deployment_properties(self, resource_name, resource_properties, properties_to_validate):
        if properties_to_validate is not None:
            for property in properties_to_validate:
                value = resource_properties.get(property, None)
                if value is None:
                    raise ResourceDriverError(f'Missing {property} for resource {resource_name}')
                
        
    # Will create a CP4NA resource using a ARM template
    def create(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, template_file_name, params_file_name, **kwargs):
        if 'skip_create' in kwargs and kwargs['skip_create']:
            return LifecycleExecuteResponse(build_request_id(CREATE_REQUEST_PREFIX, 'SKIP'))
        
        stack_id = self.get_stack_id(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)
        if stack_id is None:
            resourcemanager_driver = azure_location.resourcemanager_driver
            # Create resource name
            operation_source_name = kwargs['operation_source_name'] if 'operation_source_name' in kwargs else None
            resource_name = self.__create_resource_name(system_properties, resource_properties, self.get_resource_name(system_properties), operation_source_name)
            try:
                # validate properties before creation of resource
                if 'properties_to_validate' in kwargs:
                    self.validate_deployment_properties(resource_name, resource_properties, kwargs['properties_to_validate'])
                
                # create resource/deployment
                stack_name = self.get_stack_name(resource_id, resource_name)
                arm_template, arm_parameters = self.prepare_deployment_artifacts(system_properties, resource_properties, request_properties, template_file_name, params_file_name)
                stack_id = resourcemanager_driver.create_deployment(stack_name, arm_template, arm_parameters)
                logger.info(f'stack_name={stack_name} resource_name={resource_name} arm_template={arm_template} arm_parameters={arm_parameters}')
                
                logger.info(f'Created Stack Id: {stack_id}')
            except Exception as e:
                raise ResourceDriverError(str(e)) from e

            if stack_id is None:
                raise ResourceDriverError('Failed to create deployment in azure')

        request_id = build_request_id(CREATE_REQUEST_PREFIX, stack_id)
        associated_topology = AZUREAssociatedTopology()
        associated_topology.add_stack_id(resource_name, stack_id)
        return LifecycleExecuteResponse(request_id, associated_topology=associated_topology)

    # Remove a ARM deployment in AZURE
    def remove(self, resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location, **kwargs):
        if 'skip_delete' in kwargs and kwargs['skip_delete']:
            return LifecycleExecuteResponse(build_request_id(CREATE_REQUEST_PREFIX, 'SKIP'))
        resource_id = system_properties.get('resourceId', None)
        if resource_id is None:
            raise InvalidRequestError(f'system_properties.resource_id must be provided')

        operation_source_name = kwargs['operation_source_name'] if 'operation_source_name' in kwargs else None
        resource_name = self.__create_resource_name(system_properties, resource_properties, self.get_resource_name(system_properties), operation_source_name)

        associated_topology.__class__ = AZUREAssociatedTopology
        stack_id = associated_topology.get_stack_id(resource_name)

        if stack_id is not None:
            logger.info(f'Removing stack {stack_id} for resource_id: {resource_id}, lifecycle_name: {lifecycle_name}, system_properties: {system_properties} resource_properties: {resource_properties} request_properties: {request_properties} associated_topology: {associated_topology} aws_location: {azure_location}')
            azure_location.set_resource_group_name(resource_properties.get('resourcegroup_name'))
            request_id = build_request_id(DELETE_REQUEST_PREFIX, stack_id)
            try:
                if 'properties_to_validate' in kwargs:
                    self.validate_deployment_properties(resource_name, resource_properties, kwargs['properties_to_validate'])
                if system_properties.get('resourceType', None) == 'resource::AzureResourceGroup::1.0':
                    delete_response = azure_location.resourcemanager_driver.delete_resourcegroup(stackId=stack_id)
                else:
                    if resource_name.__contains__("peer"):
                        deployment = azure_location.resourcemanager_driver.get_deployment(stack_id)
                        vnet_peering_id = deployment.properties.output_resources[0].id if deployment is not None else None
                        if vnet_peering_id is not None:
                            azure_location.set_resource_group_name(resource_properties.get('initiator_vnet_rg_name'))
                            azure_location.resourcemanager_driver.delete_vnetpeering(resource_properties.get('initiator_vnet_rg_name'), resource_properties.get('initiator_vnet_name'), self.get_vnet_peering_name(resource_properties.get('initiator_vnet_name'), resource_properties.get('acceptor_vnet_name')))
                    delete_response = azure_location.resourcemanager_driver.delete_deployment(stack_id)
                    
                if delete_response is None:
                    raise InfrastructureNotFoundError(f'Stack {stack_id} not found')
                logger.info(f'Stack {stack_id} deletion response: {delete_response}')
                
            except StackNotFoundError as e:
                return LifecycleExecuteResponse(build_request_id(DELETE_REQUEST_PREFIX, 'SKIP'))
            except Exception as e:
                raise ResourceDriverError(str(e)) from e
        else:
            # nothing to do
            logger.info(f'No stack_id in associated topology for resource with id: {resource_id} name: {resource_name} lifecycle_name: {lifecycle_name}')
            request_id = build_request_id(CREATE_REQUEST_PREFIX, 'SKIP')

        return LifecycleExecuteResponse(request_id)
    
    def __create_resource_name(self, system_properties, resource_properties, resource_name, operation_source_name):
        resource_name = self.get_resource_name(system_properties)
        if operation_source_name is not None:
            resource_name = resource_name + operation_source_name
        system_properties['resourceName'] = resource_name
        return system_properties['resourceName']