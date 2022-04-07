import logging
from pathlib import Path
from pickle import TRUE
import random
from azuredriver.service.common import *
from ignition.model.lifecycle import LifecycleExecution, STATUS_IN_PROGRESS, STATUS_COMPLETE, STATUS_FAILED
import ignition.model.references as reference_model
from ignition.service.framework import Service, Capability
from ignition.service.resourcedriver import ResourceDriverHandlerCapability, InfrastructureNotFoundError, ResourceDriverError, InvalidRequestError
from ignition.model.failure import FailureDetails, FAILURE_CODE_INFRASTRUCTURE_ERROR
from ignition.service.config import ConfigurationPropertiesGroup
from azuredriver.location import *
from azuredriver.model.exceptions import *
from azuredriver.service.azureresourcemanager import *
from .vnet_arm import *
from .subnet_arm import *
from .vm_arm import *
from .nsg_arm import *
from .public_ip_arm import *
from .routetable_arm import *
from .storage_account_arm import *
from .resource_group import *
from azuredriver.service.topology import AZUREAssociatedTopology


driver_directory = here = Path(__file__).parent.parent

logger = logging.getLogger(__name__)

ARM_TEMPLATE_TYPE = 'AZURERESOURCEMANAGER'

VNET_RESOURCE_TYPE = 'VNET'

AZURE_DEPLOYMENT_STATUS_CREATING = ['Creating', 'Running']
AZURE_DEPLOYMENT_STATUS_FAILED = 'Failed'
AZURE_DEPLOYMENT_STATUS_UPDATING = 'Updating'
AZURE_DEPLOYMENT_STATUS_CREATED = ['Created', 'Succeeded']
AZURE_DEPLOYMENT_STATUS_DELETING = 'Deleting'
AZURE_DEPLOYMENT_STATUS_DELETED = 'Deleted'


class AdditionalResourceDriverProperties(ConfigurationPropertiesGroup, Service, Capability):

    def __init__(self):
        super().__init__('resource_driver')
        self.keep_files = False


# Note: this implementation is not fault-tolerant; a lifecycle request will be handled directly
# such that if the driver goes down the whole intent will probably fail. Also, it will make the
# lifecycle request handling synchronous, so we'll need to ensure that any Brent timeouts on driver
# calls are sufficiently high enough.
class ResourceDriverHandler(Service, ResourceDriverHandlerCapability):

    def __init__(self):
        self.stack_name_creator = StackNameCreator()
        self.props_merger = PropertiesMerger()
        self.handlers = {
            'resource::AzureVNet::1.0': VNETResourceManager(),
            'resource::AzureSubnet::1.0': SubnetResourceManager(),
            'resource::AzureNetworkSecurityGroup::1.0': NSGResourceManager(),
            'resource::AzurePublicIP::1.0': PublicIPResourceManager(),
            'resource::AzureRouteTable::1.0': RouteTableResourceManager(),
            'resource::AzureStorageAccount::1.0': StorageAccountResourceManager(),
            'resource::AzureVM::1.0': VMResourceManager(),
            'resource::AzureResourceGroup::1.0': ResourceGroupResourceManager()
        }

    def execute_lifecycle(self, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, deployment_location):
        logger.debug(f'lifecycle_name:{lifecycle_name},driver_files:{driver_files},system_properties:{system_properties}')
        logger.debug(f'resource_properties:{resource_properties},request_properties:{request_properties},associated_topology: {associated_topology}')

        azure_location = None
        try:
            azure_location = AZUREDeploymentLocation.from_dict(deployment_location)
            azure_location.set_resource_group_name(resource_properties.get('resourcegroup_name'))
            
            resource_type = system_properties.get('resourceType', None)
            if resource_type is None:
                raise InvalidRequestError(f'system_properties.resourceType must be provided')

            resource_id = system_properties.get('resourceId', None)
            if resource_id is None:
                raise InvalidRequestError(f'system_properties.resource_id must be provided')

            resource_name = system_properties.get('resourceName', None)
            if resource_name is None:
                raise InvalidRequestError(f'system_properties.resourceName must be provided')

            method_name = lifecycle_name.lower()

            handler = self.handlers.get(resource_type, None)
            if handler is None:
                raise InvalidRequestError(f'No handler for resourceType {resource_type}')

            if method_name == 'delete' or method_name == 'uninstall':
                method_name = 'remove'
            elif method_name == 'install':
                method_name = 'create'
            method = getattr(handler, method_name)
            if method is not None:
                return method(resource_id, lifecycle_name, driver_files, system_properties, resource_properties, request_properties, associated_topology, azure_location)
            else:
                raise InvalidRequestError(f'Handler does not support lifecycle {lifecycle_name}')
        finally:
            if azure_location is not None:
                azure_location.close()
            logger.debug("exit execute")


    def get_lifecycle_execution(self, request_id, deployment_location):
        logger.info(f'request_id: {request_id},  deployment_location: {deployment_location}')
        deployment = None
        azure_location = AZUREDeploymentLocation.from_dict(deployment_location)
        resourcemanager_driver = azure_location.resourcemanager_driver
        request_type, stack_id, operation_id = self.__split_request_id(request_id)
        logger.info(f'Started checking lifecycle execution status')
        if stack_id == 'SKIP':
            return LifecycleExecution(request_id, STATUS_COMPLETE, failure_details=None, outputs={})
        azure_location.set_resource_group_name(get_resource_name_from_stackid(stack_id, "resourceGroups"))
        
        try:
            # limit calls to rate-limited AZURE describe stack API
            if random.randint(1, 20)%2 == 0:
                return LifecycleExecution(request_id, STATUS_IN_PROGRESS)
            logger.info(f'Stack Id to get deployment: {stack_id}')
            isResourceGroup = self.is_resourcetype_resourcegroup(stack_id)
            isVnetPeering = self.is_vnet_peering(stack_id)
            if isResourceGroup: 
                deployment = resourcemanager_driver.get_resourcegroup(stack_id)
            else:
                deployment = resourcemanager_driver.get_deployment(stack_id)
                logger.info('Request Type: %s', request_type)
                logger.info(deployment.properties.output_resources)
                if isVnetPeering and request_type == DELETE_REQUEST_PREFIX:
                    logger.info('Inside Vnet Peering')
                    try:
                        vnetpeering = resourcemanager_driver.get_vnetpeering(get_resource_name_from_stackid(stack_id, "resourceGroups"), get_resource_name_from_stackid(stack_id, "virtualNetworks"), get_resource_name_from_stackid(stack_id, "virtualNetworkPeerings"))
                    except StackNotFoundError as e:
                        if deployment is None:
                            raise

            logger.debug('Stack found: %s', deployment)
        except StackNotFoundError as e:
            logger.error('Stack not found: %s', stack_id)
            if request_type == DELETE_REQUEST_PREFIX:
                logger.info('Stack not found on delete request, returning task as successful: %s', stack_id)
                return LifecycleExecution(request_id, STATUS_COMPLETE)
            else:
                raise InfrastructureNotFoundError(str(e)) from e

        if deployment is None:
            logger.debug('Deployment not found: %s', stack_id)
            if request_type == DELETE_REQUEST_PREFIX:
                logger.debug('Deployment not found on delete request, returning task as successful: %s', stack_id)
                return LifecycleExecution(request_id, STATUS_COMPLETE)
            else:
                raise InfrastructureNotFoundError(f'Cannot find stack {stack_id}')
        logger.debug(f'Retrieved Deployment: {deployment}')
        return self.__build_execution_response(deployment, request_id, resourcemanager_driver)

    def is_resourcetype_resourcegroup(self, stack_id):
        return True if stack_id.find('/providers/') == -1 else False
            
    
    def is_vnet_peering(self, stack_id):
        return True if stack_id.__contains__("vnet_peering") else False
    
    def __split_request_id(self, request_id):
        return tuple(request_id.split(REQUEST_ID_SEPARATOR))

    def __build_execution_response(self, deployment, request_id, resourcemanager_driver):
        logger.info(f'Building execution response')
        request_type, stack_id, operation_id = self.__split_request_id(request_id)
        if deployment is None:
            stack_status = AZURE_DEPLOYMENT_STATUS_DELETED
        else:
            stack_status = deployment.properties.provisioning_state
        failure_details = None
        if request_type == CREATE_REQUEST_PREFIX:
            status = self.__determine_create_status(request_id, stack_id, stack_status)
        else:
            status = self.__determine_delete_status(request_id, stack_id, stack_status)
        if not self.is_resourcetype_resourcegroup(stack_id) and status == STATUS_FAILED:
            description = resourcemanager_driver.get_deployment_failure(stack_id)
            failure_details = FailureDetails(FAILURE_CODE_INFRASTRUCTURE_ERROR, description)

        outputs = None
        if not self.is_resourcetype_resourcegroup(stack_id) and request_type == CREATE_REQUEST_PREFIX:
            outputs = deployment.properties.outputs

        logger.debug(f'request_id {request_id} deployment: {deployment} outputs: {outputs}')
        return LifecycleExecution(request_id, status, failure_details=failure_details, outputs=outputs)
    
    # TODO
    def __change_outputs_key(self, key):
        if key == 'VNETID':
            key = 'vnet_id'
        elif key == 'SUBNETID':
            key = 'subnet_id'
        elif key == 'IGWID':
            key = 'igw_id'
        elif key == 'ROUTETABLEID':
            key = 'route_table_id'
        elif key == 'TGWID':
            key = 'transit_gateway_id'
        elif key == 'TGWRTID':
            key = 'transit_route_table_id'
        return key

    def __translate_outputs_to_values_dict(self, stack_outputs):
        if stack_outputs is None:
            return None
        if len(stack_outputs) == 0:
            return None
        outputs = {}
        for stack_output in stack_outputs:
            key = stack_output.get('OutputKey')
            value = stack_output.get('OutputValue')
            outputs[self.__change_outputs_key(key)] = value

        logger.info(f'stack outputs: {stack_outputs} to outputs: {outputs}')

        return outputs

    def __determine_create_status(self, request_id, stack_id, stack_status):
        logger.info(f'stack status: {stack_status}')
        if stack_status in AZURE_DEPLOYMENT_STATUS_CREATING:
            create_status = STATUS_IN_PROGRESS
        elif stack_status in AZURE_DEPLOYMENT_STATUS_CREATED:
            create_status = STATUS_COMPLETE
        elif stack_status in [AZURE_DEPLOYMENT_STATUS_FAILED]:
            create_status = STATUS_FAILED
        # TODO
        #elif stack_status in AWS_STACK_STATUS_ROLLBACK_COMPLETE:
        #    create_status = STATUS_FAILED
        else:
            raise ResourceDriverError(f'Cannot determine status for request \'{request_id}\' as the current Stack status is \'{stack_status}\' which is not a valid value for the expected transition')
        logger.debug('Stack %s has stack_status %s, setting status in response to %s', stack_id, stack_status, create_status)
        return create_status

    def __determine_delete_status(self, request_id, stack_id, stack_status):
        if stack_status in [AZURE_DEPLOYMENT_STATUS_DELETING]:
            delete_status = STATUS_IN_PROGRESS
        elif stack_status in [AZURE_DEPLOYMENT_STATUS_DELETED]:
            delete_status = STATUS_COMPLETE
        # TODO
        elif stack_status in [AZURE_DEPLOYMENT_STATUS_FAILED]:
            delete_status = STATUS_FAILED
        else:
            raise ResourceDriverError(f'Cannot determine status for request \'{request_id}\' as the current Stack status is \'{stack_status}\' which is not a valid value for the expected transition')
        logger.info('Stack %s has stack_status %s, setting status in response to %s', stack_id, stack_status, delete_status)
        return delete_status

    def find_reference(self, instance_name, driver_files, deployment_location):
        """
        Find a Resource, returning the necessary property output values and internal resources from those instances

        :param str instance_name: name used to filter the Resource to find
        :param ignition.utils.file.DirectoryTree driver_files: object for navigating the directory intended for this driver from the Resource package. The user should call 'remove_all' when the files are no longer needed
        :param dict deployment_location: the deployment location to find the instance in
        :return: an ignition.model.references.FindReferenceResponse

        :raises:
            ignition.service.resourcedriver.InvalidDriverFilesError: if the scripts are not valid
            ignition.service.resourcedriver.InvalidRequestError: if the request is invalid e.g. if no script can be found to execute the transition/operation given by lifecycle_name
            ignition.service.resourcedriver.TemporaryResourceDriverError: there is an issue handling this request at this time
            ignition.service.resourcedriver.ResourceDriverError: there was an error handling this request
        """
        return reference_model.FindReferenceResponse()


