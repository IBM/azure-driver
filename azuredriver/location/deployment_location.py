import logging
import datetime
import json
import time
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
#from cfn_tools import load_yaml
from ignition.utils.propvaluemap import PropValueMap
from ignition.locations.exceptions import InvalidDeploymentLocationError
from ignition.locations.utils import get_property_or_default
from azure.core.exceptions import HttpResponseError
from azure.mgmt.resource.resources.models import DeploymentMode, Deployment,  DeploymentProperties, DeploymentWhatIf, DeploymentWhatIfProperties, ResourceGroup
from azuredriver.model.exceptions import StackNotFoundError
from azuredriver.service import *
from azuredriver.service.resourcedriver import InvalidRequestError


PUBLIC_KEY_SUFFIX = '_public'
PRIVATE_KEY_SUFFIX = '_private'

AZURE_DEPLOYMENT_STATUS_CREATING = 'Creating'
AZURE_DEPLOYMENT_STATUS_FAILED = 'Failed'
AZURE_DEPLOYMENT_STATUS_UPDATING = 'Updating'
AZURE_DEPLOYMENT_STATUS_CREATED = 'Created'
AZURE_DEPLOYMENT_STATUS_DELETING = 'Deleting'
AZURE_DEPLOYMENT_STATUS_DELETED = 'Deleted'

AZURE_DEPLOYMENT_STATUS_SUCCEEDED = 'Succeeded'

logger = logging.getLogger(__name__)

class AZUREDeploymentLocation:
    """
    AZURE based deployment location

    Attributes:
      name (str): name of the location
    """

    NAME = 'name'
    PROPERTIES = 'properties'
    AZURE_TENANT_ID = 'tenantId'
    AZURE_CLIENT_ID = 'clientId'
    AZURE_CLIENT_SECRET = 'clientSecret'
    AZURE_SUBSCRIPTION_ID = 'subscriptionId'
    RESOURCE_GROUP_NAME = 'resourceGroupNname'

    @staticmethod
    def from_dict(dl_data, resource_properties=None):
        """
        Creates an AZURE deployment location from dictionary format

        Args:
            dl_data (dict): the deployment location data. Should have a 'name' field and 'properties' for the location configuration
            resource_properties (dict): resource properties

        Returns:
            an AZUREDeploymentLocation instance
        """
        name = dl_data.get(AZUREDeploymentLocation.NAME)
        if name is None:
            raise InvalidDeploymentLocationError(f'Deployment location missing \'{AZUREDeploymentLocation.NAME}\' value')
        properties = dl_data.get(AZUREDeploymentLocation.PROPERTIES)
        if properties is None:
            raise InvalidDeploymentLocationError(
                f'Deployment location missing \'{AZUREDeploymentLocation.PROPERTIES}\' value')
        azure_tenant_id = get_property_or_default(
            properties, AZUREDeploymentLocation.AZURE_TENANT_ID, error_if_not_found=False)
        azure_client_id = get_property_or_default(
            properties, AZUREDeploymentLocation.AZURE_CLIENT_ID, error_if_not_found=False)
        azure_client_secret = get_property_or_default(
            properties, AZUREDeploymentLocation.AZURE_CLIENT_SECRET, error_if_not_found=False)
        azure_subscription_id = get_property_or_default(
            properties, AZUREDeploymentLocation.AZURE_SUBSCRIPTION_ID, error_if_not_found=False)
       # resource_group_name = get_property_or_default(
       #     properties, AZUREDeploymentLocation.RESOURCE_GROUP_NAME, error_if_not_found=False)
        kwargs = {}
        logging.debug('dl_data={dl_data}')
    #    if aws_default_region is not None:
    #        kwargs = {'aws_default_region': aws_default_region}

        if azure_client_id is None or azure_client_secret is None:
            raise InvalidDeploymentLocationError(f'AZURE credentials are missing')

        return AZUREDeploymentLocation(name, azure_tenant_id, azure_client_id, azure_client_secret, azure_subscription_id, **kwargs)

    def __init__(self, name, azure_tenant_id, azure_client_id, azure_client_secret, azure_subscription_id):
        self.name = name
        self.azure_tenant_id = azure_tenant_id
        self.azure_client_id = azure_client_id
        self.azure_client_secret = azure_client_secret
        self.azure_subscription_id =  azure_subscription_id
       # self.resource_group_name = resource_group_name
       # self.resource_group_name = None
     #   self.aws_default_region = aws_default_region
        self.__rm_driver = None
     #   self.vm = self.__vm()

    def to_dict(self):
        """
        Produces a dictionary copy of the deployment location

        Returns:
            the deployment location configuration as a dictionary. For example:

            {
                'name': 'Test',
                'properties': {
                    ...
                }
            }
        """
        return {
            AZUREDeploymentLocation.NAME: self.name,
            AZUREDeploymentLocation.PROPERTIES: {
                AZUREDeploymentLocation.AZURE_TENANT_ID: self.azure_tenant_id,
                AZUREDeploymentLocation.AZURE_CLIENT_ID: self.azure_client_id,
                AZUREDeploymentLocation.AZURE_CLIENT_SECRET: self.azure_client_secret,
                AZUREDeploymentLocation.AZURE_SUBSCRIPTION_ID: self.azure_subscription_id,
                AZUREDeploymentLocation.RESOURCE_GROUP_NAME: self.resource_group_name
            }
        }


    def set_resource_group_name(self, resource_group_name):
        self.resource_group_name = resource_group_name
        return self.resource_group_name


    @property
    def resourcemanager_driver(self):
        if self.__rm_driver is None:
            self.__rm_driver = ResourceManagerDriver(self)
          #  if self.aws_default_region:
          #      self.__rm_driver.default_region = self.azure_default_region
        return self.__rm_driver
   # TODO
   # def __vm(self):
   #     return ComputeManagementClient(self.__get__crdentials(), subscription_id)
        
    def get_arm_input_util(self):
        return ARMInputUtil()

    def close(self):
        pass

   
    

class ResourceManagerDriver():
    def __init__(self, azure_deployment_location):
        self.azure_deployment_location = azure_deployment_location
    #    self.default_region = default_region
        self.rclient = self.__create_resourcemanagement_client()
        self.nclient = self.__create_networkmanagement_client()
        
    def __create_networkmanagement_client(self):
        return NetworkManagementClient(
            self.__get__credentials(),
            self.azure_deployment_location.azure_subscription_id
        )

    def __create_resourcemanagement_client(self):
           
        return ResourceManagementClient(
            self.__get__credentials(),
            self.azure_deployment_location.azure_subscription_id
        )
        
    def __get__credentials(self):
        return ClientSecretCredential(
            client_id=self.azure_deployment_location.azure_client_id,
            client_secret=self.azure_deployment_location.azure_client_secret,
            tenant_id=self.azure_deployment_location.azure_tenant_id
        )
        

    def __to_parameter(self, param_name, param_value):
        return {
            'ParameterKey': param_name,
            'ParameterValue': param_value
        }

    def list_deployments(self): 
        deployment_list = []
        try: 
            deploymentpages = self.rclient.deployments.list_by_resource_group(resource_group_name=self.azure_deployment_location.resource_group_name).by_page()   
            for deploymentpage in deploymentpages:
                for deployment in deploymentpage:
                    if deployment.properties.provisioning_state != AZURE_DEPLOYMENT_STATUS_DELETED:
                        deployment_list.append(deployment)
            return deployment_list
        except HttpResponseError as ex:
            error_message = ex.message
            logging.error(f'Failed to get Azure Deployments, {error_message}')
            raise
        
    def get_deployment(self, deployment_id_or_name):
        deployment = None
        try:
            deployment_name = self.get_name_from_stackid(deployment_id_or_name)
            if  deployment_name  is None:                              
                deployment_name = deployment_id_or_name
            else:
                deployment =  self.rclient.deployments.get(resource_group_name=self.azure_deployment_location.resource_group_name, deployment_name=deployment_name)
        except HttpResponseError as ex:
            if ex.__class__.__name__ == "ResourceNotFoundError":
                raise StackNotFoundError(ex)
            error_message = ex.message
            logging.error(f'Failed to get Azure Deployment, {error_message}')
            raise 

        return deployment
    
    # TODO not using
    def get_deployment_matching_name(self, matcher):
        try:
            for deployment in  self.list_deployments():
                deployment_name = deployment.name
                if deployment_name is not None and matcher(deployment_name):
                   return deployment
        except HttpResponseError as ex:
            error_message = error_message = ex.message
            logging.error(f'Failed to get Azure deployment with name, {error_message}')
            raise 

        return None

    def list_deployment_operations(self,resource_group, deployment_name):
        try:
            deployment_operations_list = []
            deployment_operation_pages = self.rclient.deployment_operations.list(resource_group_name=self.azure_deployment_location.resource_group_name, deployment_name=deployment_name)
            for deployment_operations in deployment_operation_pages:
                for deployment_operation in deployment_operations:
                    deployment_operations_list.append(deployment_operation)
            return deployment_operations_list
        except HttpResponseError as ex:
            error_message = ex.message
            logging.error(f'Failed to get Azure Deployment operations, {error_message}')
            raise
        
    def get_deployment_failure(self, want_deployment_id):
        try:
            deployment = self.get_deployment(self, want_deployment_id)
            if deployment is not None:
                return deployment.properties.error.message
           # deployment_operations = self.list_deployment_operations(self.azure_deployment_location, self.get_deployment(want_deployment_id).name)
           # for deployment_operation in deployment_operations:
           #     if deployment_operation.properties.provisioning_operation == 'Create':
           #         return deployment_operation.properties.status_message
        except HttpResponseError as ex:
            error_message = ex.message
            logging.error(f'Failed to get Azure Deployment, {error_message}')
            return error_message

        return None

   # def get_stack_resources(self, want_stack_id):
   #     stack_name = None
   #     stack = self.get_stack(want_stack_id)
   #     if stack is not None:
   #         #stack_name = stack.name
   #         stack_name = stack.get('StackName', None)
   #     if stack_name is not None:
   #         response = self.rclient.describe_stack_resources(StackName=stack_name)
   #         return response.get('StackResources', [])
   
    def get_name_from_stackid(self, stack_id):
        azure_resource_name = None
        if stack_id.__contains__('/'):
            azure_resource_name = stack_id[stack_id.rindex("/")+1: len(stack_id)]
            logger.info(f'Azure resource name extracted from stack id: {azure_resource_name}')  
        else:
            azure_resource_name = stack_id
        return azure_resource_name
   
    def deployment_params_from_dict(self, parameters_dict):
        return [self.__to_parameter(param_name, param_value) for (param_name, param_value) in parameters_dict.items()]
    
    def validate_deployment(self, deployment_name, deployment):
        try:
            deploymenyment_begin_validate_async_response = self.rclient.deployments.begin_validate(self.azure_deployment_location.resource_group_name, deployment_name, deployment)
            deploymenyment_begin_validate_async_response.wait()
            return deploymenyment_begin_validate_async_response.result()
        except HttpResponseError as ex:
            error_message = ex.message
            logging.error(f'Failed to validate Azure Deployment, {error_message}')
            raise

    def prepare_deployment(self, template, parameters_dict):
        params = {
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters_dict,
        }
        deployment_properties = DeploymentProperties(**params)
        return Deployment(properties=deployment_properties)       

    def create_deployment(self, deployment_name, template, parameters_dict):
        stack_id = None
        try:
            logging.info(f'creating new deployment {deployment_name} with template {template}')
            deployment = self.prepare_deployment(template, parameters_dict)
            validation_results = self.validate_deployment(deployment_name, deployment)
            if validation_results.properties.provisioning_state == AZURE_DEPLOYMENT_STATUS_SUCCEEDED:
                retrycount = 0
                while True:
                    if retrycount > 5:
                        break
                    retrycount = retrycount+1
                    try:
                        deployment_result = self.rclient.deployments.begin_create_or_update(self.azure_deployment_location.resource_group_name, deployment_name, deployment)
                        stack_id = deployment_result.result().id
                        return stack_id
                    except Exception as ex:
                        error_message = ex.message
                        logging.error(f'Failed to create Azure Deployment in while loop, {error_message}')
                        if error_message.__contains__("AnotherOperationInProgress"):
                            continue
                        else:
                            raise
            else:
                raise InvalidRequestError(f'Deployment Template for {deployment_name} is not valid and canot continue with deployment, Error occured is : {validation_results.error.message}')
        except HttpResponseError as ex:
            error_message = ex.message
            logging.error(f'Failed to create Azure Deployment, {error_message}')
            raise

    def delete_deployment(self, delete_deployment_id):
        if delete_deployment_id is None:
            raise ValueError('delete_deployment_id argument not provided')

        deployment_name = None
        deployment = self.get_deployment(delete_deployment_id)
        if deployment is not None:
            deployment_name = deployment.name
        if deployment_name is None:
            raise ValueError('Invalid delete_deployment_id value provided')

        try:
            if not self._deployment_exists(deployment_name):
                return None

            logging.info(f'Deleting deployment {deployment_name}')
            del_response = self.rclient.deployments.begin_delete(self.azure_deployment_location.resource_group_name, deployment_name)
            return del_response
        except HttpResponseError as ex:
            error_message = ex.message
            if error_message.find('ResourceGroupBeingDeleted') != -1:
                raise StackNotFoundError('Resource Group is deleting')
            logging.error(f'Failed to delete Azure Deployment, {error_message}')
            raise
            
    def create_resourcegroup(self, resource_group_name, resource_group_location):
        try:
            resource_group = ResourceGroup(location=resource_group_location, properties=None, tags={'Creator': 'Cp4na'})
            resource_group = self.rclient.resource_groups.create_or_update(resource_group_name=resource_group_name, parameters= resource_group)
            stack_id = resource_group.id
            return stack_id
        except HttpResponseError as ex:
            error_message = ex.message
            logging.error(f'Failed to create Azure Resource group, {error_message}')
            raise
    
    def delete_resourcegroup(self, stackId, name=None):
        try: 
            if name is not None:
                resource_group_name = name
            else:
                resource_group_name = self.get_name_from_stackid(stackId)
            del_response = self.rclient.resource_groups.begin_delete(resource_group_name=resource_group_name)
            return del_response
        except HttpResponseError as ex:
            error_message = ex.message
            logging.error(f'Failed to delete Azure Resource group, {error_message}')
            raise
        
    def get_resourcegroup(self, stackId, name=None):
        try: 
            if name is not None:
                resource_group_name = name
            else:
                resource_group_name = self.get_name_from_stackid(stackId)
            resource_group = self.rclient.resource_groups.get(resource_group_name=resource_group_name)
            return resource_group
        except HttpResponseError as ex:
            if ex.__class__.__name__ == "ResourceNotFoundError":
                raise StackNotFoundError(ex)
            error_message = ex.message
            logging.error(f'Failed to get Azure Resource group, {error_message}')
            raise
        
    def get_vnetpeering(self, virtual_network_name, virtual_network_peering_name):
        try:
            resource_group_name = self.azure_deployment_location.resource_group_name
            vnetpeering = self.nclient.virtual_network_peerings.get(resource_group_name, virtual_network_name, virtual_network_peering_name)
            return vnetpeering
        except HttpResponseError as ex:
            if ex.__class__.__name__ == "ResourceNotFoundError":
                raise StackNotFoundError(ex)
            error_message = ex.message
            logging.error(f'Failed to get Azure Vnet Peering, {error_message}')
            raise    
    
    def delete_vnetpeering(self, resource_group_name, virtual_network_name, virtual_network_peering_name):
        try:
            self.nclient.virtual_network_peerings.begin_delete(resource_group_name, virtual_network_name, virtual_network_peering_name)
        except HttpResponseError as ex:
            error_message = ex.message
            if error_message.find('ResourceGroupBeingDeleted') != -1:
                raise StackNotFoundError('Resource Group is deleting')
            logging.error(f'Failed to delete Azure Vnet Peering, {error_message}')
            raise
        
    def get_route_table(self, route_table_name):
        resource_group_name = self.azure_deployment_location.resource_group_name
        route_table = self.nclient.routes.get(resource_group_name, route_table_name)
        return route_table
        
    def get_network_security_group(self, network_security_group_name):
        resource_group_name = self.azure_deployment_location.resource_group_name
        try:
            network_security_group = self.nclient.network_security_groups.get(resource_group_name, network_security_group_name)
            return network_security_group
        except HttpResponseError as ex:
            if ex.__class__.__name__ == "ResourceNotFoundError":
                raise StackNotFoundError(ex)
            error_message = ex.message
            logging.error(f'Failed to get Azure Network Security Group, {error_message}')
            raise
   
    def create_route_in_routetable(self, resource_properties):
        resource_group_name = self.azure_deployment_location.resource_group_name
        route_table_name = resource_properties.get('route_table_name')
        route_name = resource_properties.get('route_name')
        route_parameters = {
            'address_prefix': resource_properties.get('address_prefix'),
            'next_hop_type': resource_properties.get('next_hop_type'),
        }
        route_parameters['next_hop_ip_address'] = resource_properties.get('next_hop_ip_address') if len(resource_properties.get('next_hop_ip_address')) > 0 else None
        create_route_result = self.nclient.routes.begin_create_or_update(resource_group_name, route_table_name, route_name, route_parameters)
        stack_id = create_route_result.id
        return stack_id
    
    def delete_route_in_routetable(self, resource_properties):
        resource_group_name = self.azure_deployment_location.resource_group_name
        route_table_name = resource_properties.get('route_table_name')
        route_name = resource_properties.get('route_name')
        try:
            delete_route_result = self.nclient.routes.begin_delete(resource_group_name, route_table_name, route_name)
            return delete_route_result
        except HttpResponseError as ex:
            error_message = ex.message
            logging.error(f'Failed to delete Azure Route, {error_message}')
            raise
        
    def create_nsg_rule(self, resource_properties):
        resource_group_name = self.azure_deployment_location.resource_group_name
        network_security_group_name = resource_properties.get('network_security_group_name')
        nsg_rule_name = resource_properties.get('nsg_rule_name')
        priority = resource_properties.get('priority')
        security_rule_parameters =  {
            'access': resource_properties.get('access', None),
            'description': resource_properties.get('description', None),
            'destination_address_prefix': resource_properties.get('destination_address_prefix', None),
            'direction': resource_properties.get('direction', None) ,
            'protocol': resource_properties.get('protocol', None),
            'source_address_prefix': resource_properties.get('source_address_prefix', None),
            'source_port_range': resource_properties.get('source_port_range', None)
        }
       # security_rule_parameters = self.azure_deployment_location.get_arm_input_util().__set_empty_to_none_dict(security_rule_parameters)
        create_rule_result = self.nclient.security_rules.begin_create_or_update(resource_group_name, network_security_group_name, nsg_rule_name, priority, security_rule_parameters)
        stack_id = create_rule_result.id
        return stack_id
    
    def delete_nsg_rule(self, resource_properties):
        resource_group_name = self.azure_deployment_location.resource_group_name
        network_security_group_name = resource_properties.get('network_security_group_name')
        nsg_rule_name = resource_properties.get('nsg_rule_name')
        try:
            delete_response = self.nclient.security_rules.begin_delete(resource_group_name, network_security_group_name, nsg_rule_name)
            return delete_response
        except HttpResponseError as ex:
            error_message = ex.message
            logging.error(f'Failed to delete Azure Route, {error_message}')
            raise
        
   # def get_running_subnetid(self, resource_properties):
   #     virtualnetwork = self.nclient.virtual_networks.get(resource_properties.get('resourcegroup_name'), resource_properties.get('vnet_name'))
   #     for subnet in virtualnetwork.subnets:
   #         if not subnet.provisioning_state == AZURE_DEPLOYMENT_STATUS_SUCCEEDED:
   #             return subnet.id
        
        
    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
        raise TypeError("Type not serializable")

    def _deployment_exists(self, deployment_name):
        return self.rclient.deployments.check_existence(resource_group_name=self.azure_deployment_location.resource_group_name, deployment_name=deployment_name)
        

    def _get_deployment_status(self, deployment_name):
        return self.get_deployment(self.azure_deployment_location, deployment_name).properties.provisioning_state
       
# TODO
class ARMInputUtil:

    def filter_used_properties(self, arm_template_str, original_properties):
        arm_tpl = json.loads(arm_template_str)
        # cf_tpl = yaml.safe_load(cf_template_str)
        used_properties = {}
        if 'parameters' in arm_tpl:
            parameters = arm_tpl.get('parameters', {})
            if isinstance(original_properties, PropValueMap):
                return self.__filter_from_propvaluemap(parameters, original_properties)
            else:
                return self.__filter_from_dictionary(parameters, original_properties)
        return used_properties

    def __filter_from_dictionary(self, parameters, properties_dict):
        used_properties = {}
        for k, v in parameters.items():
            if k in properties_dict:
                used_properties[k] = properties_dict[k]
        return used_properties

    def __filter_from_propvaluemap(self, parameters, prop_value_map):
        used_properties = {}
        for param_name, param_def in parameters.items():
            if param_name in prop_value_map:
                used_properties[param_name] = self.__extract_property_from_value_map(prop_value_map, param_name)
            elif param_name.endswith(PUBLIC_KEY_SUFFIX):
                key_name = param_name[:len(param_name)-len(PUBLIC_KEY_SUFFIX)]
                if key_name in prop_value_map:
                    full_value = prop_value_map.get_value_and_type(key_name)
                    if full_value.get('type') == 'key' and 'publicKey' in full_value:
                        used_properties[param_name] = full_value.get('publicKey')
            elif param_name.endswith(PRIVATE_KEY_SUFFIX):
                key_name = param_name[:len(param_name)-len(PRIVATE_KEY_SUFFIX)]
                if key_name in prop_value_map:
                    full_value = prop_value_map.get_value_and_type(key_name)
                    if full_value.get('type') == 'key' and 'privateKey' in full_value:
                        used_properties[param_name] = full_value.get('privateKey')
        return used_properties

    def __extract_property_from_value_map(self, prop_value_map, property_name):
        full_value = prop_value_map.get_value_and_type(property_name)
        if full_value.get('type') == 'key':
            return full_value.get('keyName')
        else:
            return prop_value_map[property_name]
        
    def __set_empty_to_none_dict(self, properties):
        for key, value in properties.items():
            properties[key] = None if len(value) == 0 else value
        return properties
        
        
    
        