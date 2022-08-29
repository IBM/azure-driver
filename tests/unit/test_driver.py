import os
import time
import unittest
from unittest import mock
import uuid
from unittest.mock import patch, MagicMock, ANY
from ignition.utils.file import DirectoryTree
from ignition.utils.propvaluemap import PropValueMap
from ignition.model.associated_topology import AssociatedTopology
from azuredriver.location.deployment_location import AZURE_DEPLOYMENT_STATUS_CREATED, AZUREDeploymentLocation
from azuredriver.service.resourcedriver import AdditionalResourceDriverProperties, ResourceDriverHandler

class TestDriver(unittest.TestCase):

    def setUp(self):
        self.resource_driver_config = AdditionalResourceDriverProperties()
        self.resource_driver_config.keep_files = True
        self.mock_cf_input_utils = MagicMock()
        self.mock_cf_input_utils.filter_used_properties.return_value = {'propA': 'valueA'}
        self.mock_os_location = MagicMock()
        self.mock_os_location.get_cf_input_util.return_value = self.mock_cf_input_utils
        self.mock_location_translator = MagicMock()
        self.mock_location_translator.from_deployment_location.return_value = self.mock_os_location


        self.deployment_location = self.__deployment_location()
        self.system_properties = self.__system_properties()
        self.resource_properties = self.__resource_properties()

    def __system_properties(self):
        props = {}
        props['resourceId'] = {'type': 'string', 'value': str(uuid.uuid4())}
        props['resourceName'] = {'type': 'string', 'value': 'test__Subnets__subnet2'}
        props['resourceManagerId'] = {'type': 'string', 'value': 'brent'}
        props['metricKey'] = {'type': 'string', 'value': 'c748dabe-2d0a-45ee-9725-93a546806ee8'}
        props['requestId'] = {'type': 'string', 'value': '8324ef5f-164c-4ee6-99c1-186ac5524bc4'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'dl-azure-vrantestcluste4'}
        props['resourceType'] = {'type': 'string', 'value': 'resource::azureSubnet::1.0'}
        return PropValueMap(props)

    def __system_properties_rg(self):
        props = {}
        props['resourceId'] = {'type': 'string', 'value': str(uuid.uuid4())}
        props['resourceName'] = {'type': 'string', 'value': 'test__vpc__vpc'}
        props['resourceManagerId'] = {'type': 'string', 'value': 'brent'}
        props['metricKey'] = {'type': 'string', 'value': 'c748dabe-2d0a-45ee-9725-93a546806ee8'}
        props['requestId'] = {'type': 'string', 'value': '8324ef5f-164c-4ee6-99c1-186ac5524bc4'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'dl-azure-vrantestcluste4'}
        props['resourceType'] = {'type': 'string', 'value': 'resource::AzureResourceGroup::1.0'}
        return PropValueMap(props)

    def __system_properties_vnet(self):
        props = {}
        props['resourceId'] = {'type': 'string', 'value': str(uuid.uuid4())}
        props['resourceName'] = {'type': 'string', 'value': 'test__vpc__vpc'}
        props['resourceManagerId'] = {'type': 'string', 'value': 'brent'}
        props['metricKey'] = {'type': 'string', 'value': 'c748dabe-2d0a-45ee-9725-93a546806ee8'}
        props['requestId'] = {'type': 'string', 'value': '8324ef5f-164c-4ee6-99c1-186ac5524bc4'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'dl-azure-vrantestcluste4'}
        props['resourceType'] = {'type': 'string', 'value': 'resource::AzureVNet::1.0'}
        return PropValueMap(props)

    def __system_properties_rt(self):
        props = {}
        props['resourceId'] = {'type': 'string', 'value': str(uuid.uuid4())}
        props['resourceName'] = {'type': 'string', 'value': 'test__rt__rt'}
        props['resourceManagerId'] = {'type': 'string', 'value': 'brent'}
        props['metricKey'] = {'type': 'string', 'value': 'c748dabe-2d0a-45ee-9725-93a546806ee8'}
        props['requestId'] = {'type': 'string', 'value': '8324ef5f-164c-4ee6-99c1-186ac5524bc4'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'dl-azure-vrantestcluste4'}
        props['resourceType'] = {'type': 'string', 'value': 'resource::AzureRouteTable::1.0'}
        return PropValueMap(props)

    


    def __resource_properties(self):
        props = {}
        props['vnet_name'] = {'type': 'string', 'value': 'Primary-test'}
        props['local_or_global'] = {'type': 'string', 'value': 'local'}
        props['private_or_public'] = {'type': 'string', 'value': 'Public'}
        props['subnet_private_link_service_network_policies'] = {'type': 'string', 'value': 'Enabled'}
        props['network_security_group_name'] = {'type': 'string', 'value': 'Primary-test-Public-local'}
        props['route_table_name'] = {'type': 'string', 'value': 'Primary-test-Public-local'}
        props['subnet_name'] = {'type': 'string', 'value': 'Primary-test_sub2'}
        props['subnet_private_network_endpoint_policies'] = {'type': 'string', 'value': 'Enabled'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'Test_Azure_new'}
        props['resourceManager'] = {'type': 'string', 'value': 'brent'}
        props['resourcegroup_name'] = {'type': 'string', 'value': 'Primary-test-rg'}
        props['subnet_cidr_block'] = {'type': 'string', 'value': '10.86.3.0/24'}


        return PropValueMap(props)

    def __resource_properties_vnet(self):
        props = {}
        props['vnet_name'] = {'type': 'string', 'value': 'Primary-test'}
        props['vnet_private_endpoint_network_policies'] = {'type': 'string', 'value': 'Enabled'}
        props['vnet_enable_ddos_protection'] = {'type': 'string', 'value': 'vnet_enable_ddos_protection'}
        props['vnet_address_space'] = {'type': 'string', 'value': '10.86.0.0/16'}
        props['vnet_location'] = {'type': 'string', 'value': 'North Europe'}
        props['vnet_private_link_service_network_policies'] = {'type': 'string', 'value': 'Enabled'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'Test_Azure_new'}
        props['resourceManager'] = {'type': 'string', 'value': 'brent'}
        props['resourcegroup_name'] = {'type': 'string', 'value': 'Primary-test-rg'}
        props['vnet_default_cidr_block'] = {'type': 'string', 'value': '10.86.1.0/24'}

        return PropValueMap(props)

    def __resource_properties_rt(self):
        props = {}
        props['branch_office_cidr'] = {'type': 'string', 'value': '0.0.0.0/0'}
        props['route_table_location'] = {'type': 'string', 'value': 'centralindia'}
        props['route_table_name'] = {'type': 'string', 'value': 'rtTest'}
        props['private_static_ip'] = {'type': 'string', 'value': '10.0.2.4/24'}
        props['private_or_public'] = {'type': 'string', 'value': 'private'}
        props['local_or_global'] = {'type': 'string', 'value': 'global'}
        props['route_table_disable_bgp_route_propagation'] = {'type': 'boolean', 'value': False}
        

        return PropValueMap(props)


    def __request_properties(self):
        props = {}

        return PropValueMap(props)

    def __deployment_location(self):
        NAME = 'name'
        PROPERTIES = 'properties'

        return {
            NAME: "dummy",
            PROPERTIES: {
                AZUREDeploymentLocation.AZURE_TENANT_ID: 'dummy',
                AZUREDeploymentLocation.AZURE_CLIENT_ID: 'dummy',
                AZUREDeploymentLocation.AZURE_CLIENT_SECRET: 'dummy',
                AZUREDeploymentLocation.AZURE_SUBSCRIPTION_ID: 'dummy'
            }
        }

    @patch('azuredriver.location.deployment_location.ResourceManagerDriver.create_resourcegroup')
    @patch('azuredriver.location.deployment_location.ResourceManagerDriver.get_resourcegroup')
    def test_Driver_rt(self,  mock_get_resourcegroup, mock_create_resourcegroup):
        system_properties_rg = self.__system_properties_rg()
        resource_properties = self.__resource_properties()
        request_properties = self.__request_properties()
        deployment_location = self.__deployment_location()
        path = os.path.abspath(os.getcwd())
        print(path)
        driver_files = DirectoryTree('/resources/resourcemanager/')
        print(driver_files.get_path())
        driver = ResourceDriverHandler()
        associated_topology = AssociatedTopology()
       # azure_location = AZUREDeploymentLocation.from_dict(deployment_location)
       # azure_location.resourcemanager_driver.get_resourcegroup = mock.Mock(return_value="Primary-test-rg")
        mock_create_resourcegroup.return_value = "/resourceGroups/Primary-test-rg"
        mock_get_resourcegroup.return_value = {'name': 'Primary-test-rg',  'id' : '/resourceGroups/Primary-test-rg','properties' : {'provisioning_state': AZURE_DEPLOYMENT_STATUS_CREATED}, 'output_resources': {}}
        create_resp = driver.execute_lifecycle('Create', driver_files, system_properties_rg, resource_properties, request_properties, associated_topology, deployment_location)
        get_resp = driver.get_lifecycle_execution(create_resp.request_id, deployment_location)
        self.assertEqual(create_resp.request_id, get_resp.request_id)

    
    @patch('azuredriver.location.deployment_location.ResourceManagerDriver.create_deployment')
    @patch('azuredriver.location.deployment_location.ResourceManagerDriver.get_deployment')
    @patch('azuredriver.location.deployment_location.ResourceManagerDriver.get_resourcegroup')
    def test_Driver_rt(self, mock_get_resourcegroup, mock_get_deployment, mock_create_deployment):
        system_properties_rt = self.__system_properties_rt()
        resource_properties_rt = self.__resource_properties_rt()
        request_properties = self.__request_properties()
        deployment_location = self.__deployment_location()
        path = os.path.abspath(os.getcwd())
        print(path)
        driver_files = DirectoryTree('/resources/resourcemanager/')
        print(driver_files.get_path())
        driver = ResourceDriverHandler()
        associated_topology = AssociatedTopology()
        mock_get_resourcegroup.return_value = "Primary-test-rg"
        mock_create_deployment.return_value = "/resourceGroups/Primary-test-rg/routeTables/rtTest"
        mock_get_deployment.return_value = {'name': 'dummy', 'id' : '/resourceGroups/Primary-test-rg/routeTables/rtTest','properties' : {'provisioning_state': AZURE_DEPLOYMENT_STATUS_CREATED}, 'output_resources': {}}
        create_resp = driver.execute_lifecycle('Create', driver_files, system_properties_rt, resource_properties_rt, request_properties, associated_topology, deployment_location)
        get_resp = driver.get_lifecycle_execution(create_resp.request_id, deployment_location)
        self.assertEqual(create_resp.request_id, get_resp.request_id)
    
    
    @patch('azuredriver.location.deployment_location.ResourceManagerDriver.create_deployment')
    @patch('azuredriver.location.deployment_location.ResourceManagerDriver.get_deployment')
    @patch('azuredriver.location.deployment_location.ResourceManagerDriver.get_resourcegroup')
    def test_driver_vnet(self, mock_get_resourcegroup, mock_get_deployment, mock_create_deployment):
        system_properties_vnet = self.__system_properties_vnet()
        deployment_location = self.__deployment_location()
        request_properties = self.__request_properties()
        resource_properties_vnet = self.__resource_properties_vnet()
        path = os.path.abspath(os.getcwd())
        print(path)
        driver_files = DirectoryTree('/resources/resourcemanager/')
        print(driver_files.get_path())
        driver = ResourceDriverHandler()
        associated_topology = AssociatedTopology()
        azure_location = AZUREDeploymentLocation.from_dict(deployment_location)
        mock_get_resourcegroup.return_value = "Primary-test-rg"
        mock_create_deployment.return_value = "/resourceGroups/Primary-test-rg/vpcs/Primary-test"
        mock_get_deployment.return_value = {'name': 'dummy', 'id' : '/resourceGroups/Primary-test-rg/vpcs/Primary-test', 'properties': {'provisioning_state': AZURE_DEPLOYMENT_STATUS_CREATED}, 'output_resources': {}}
        create_resp = driver.execute_lifecycle('Create', driver_files, system_properties_vnet, resource_properties_vnet, request_properties, associated_topology, deployment_location)
        get_resp = driver.get_lifecycle_execution(create_resp.request_id, deployment_location)
        self.assertEqual(create_resp.request_id, get_resp.request_id)
       
        
