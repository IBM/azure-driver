import os
import time
import unittest
import uuid
from unittest.mock import patch, MagicMock, ANY
from ignition.utils.file import DirectoryTree
from ignition.utils.propvaluemap import PropValueMap
from ignition.model.associated_topology import AssociatedTopology
from azuredriver.location.deployment_location import AZUREDeploymentLocation
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

    '''def __deployment_location(self):
        return {'name': 'mock_location'}

    def __system_properties(self):
        props = {}
        props['resourceId'] = '123'
        props['resourceName'] = 'TestResource'
        return PropValueMap(props)

    def __resource_properties(self):
        props = {}
        props['propA'] = {'type': 'string', 'value': 'valueA'}
        props['propB'] = {'type': 'string', 'value': 'valueB'}
        return PropValueMap(props)

    def test_driver_1(self):
        dl = {
            'name': "aws1",
            'properties': {
                AWSDeploymentLocation.AWS_ACCESS_KEY_ID: 'dummy',
                AWSDeploymentLocation.AWS_SECRET_ACCESS_KEY: 'dummy'
            }
        }
        driver_files = DirectoryTree('tests/unit/resources/cloudformation')
        driver = ResourceDriverHandler(self.location_translator, resource_driver_config=self.resource_driver_config)
        resource_properties = PropValueMap({
            'EnvironmentName': {
                'type': 'string',
                'value': 'sg1'
            }
        })
        # driver.execute_lifecycle('Create', driver_files, self.system_properties, self.resource_properties, {}, AssociatedTopology(), dl)
        resp = driver.execute_lifecycle('Create', driver_files, self.system_properties, resource_properties, {}, AssociatedTopology(), dl)
        print(f'resp={resp.request_id}')'''


    def __system_properties(self):
        props = {}
        props['resourceId'] = {'type': 'string', 'value': str(uuid.uuid4())}
        props['resourceName'] = {'type': 'string', 'value': 'test__Subnets__subnet2'}
        props['resourceManagerId'] = {'type': 'string', 'value': 'brent'}
        props['metricKey'] = {'type': 'string', 'value': 'c748dabe-2d0a-45ee-9725-93a546806ee8'}
        props['requestId'] = {'type': 'string', 'value': '8324ef5f-164c-4ee6-99c1-186ac5524bc4'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'dl-aws-vrantestcluste4'}
        props['resourceType'] = {'type': 'string', 'value': 'resource::AWSSubnet::1.0'}
        return PropValueMap(props)

    def __system_properties_rg(self):
        props = {}
        props['resourceId'] = {'type': 'string', 'value': str(uuid.uuid4())}
        props['resourceName'] = {'type': 'string', 'value': 'test__vpc__vpc'}
        props['resourceManagerId'] = {'type': 'string', 'value': 'brent'}
        props['metricKey'] = {'type': 'string', 'value': 'c748dabe-2d0a-45ee-9725-93a546806ee8'}
        props['requestId'] = {'type': 'string', 'value': '8324ef5f-164c-4ee6-99c1-186ac5524bc4'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'dl-aws-vrantestcluste4'}
        props['resourceType'] = {'type': 'string', 'value': 'resource::AzureResourceGroup::1.0'}
        return PropValueMap(props)

    def __system_properties_vnet(self):
        props = {}
        props['resourceId'] = {'type': 'string', 'value': str(uuid.uuid4())}
        props['resourceName'] = {'type': 'string', 'value': 'test__vpc__vpc'}
        props['resourceManagerId'] = {'type': 'string', 'value': 'brent'}
        props['metricKey'] = {'type': 'string', 'value': 'c748dabe-2d0a-45ee-9725-93a546806ee8'}
        props['requestId'] = {'type': 'string', 'value': '8324ef5f-164c-4ee6-99c1-186ac5524bc4'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'dl-aws-vrantestcluste4'}
        props['resourceType'] = {'type': 'string', 'value': 'resource::AzureVNet::1.0'}
        return PropValueMap(props)

    def __system_properties_rt(self):
        props = {}
        props['resourceId'] = {'type': 'string', 'value': str(uuid.uuid4())}
        props['resourceName'] = {'type': 'string', 'value': 'test__rt__rt'}
        props['resourceManagerId'] = {'type': 'string', 'value': 'brent'}
        props['metricKey'] = {'type': 'string', 'value': 'c748dabe-2d0a-45ee-9725-93a546806ee8'}
        props['requestId'] = {'type': 'string', 'value': '8324ef5f-164c-4ee6-99c1-186ac5524bc4'}
        props['deploymentLocation'] = {'type': 'string', 'value': 'dl-aws-vrantestcluste4'}
        props['resourceType'] = {'type': 'string', 'value': 'resource::AWSRoute::1.0'}
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
        props['ec2_access_key'] = {'type': 'string', 'value': 'AKIA2Z3UQKJ5L4HNZFUR'}
        props['ec2_secret_key'] = {'type': 'string', 'value': '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'}
        props['route_cidr'] = {'type': 'string', 'value': '0.0.0.0/0'}
        props['route_table_id'] = {'type': 'string', 'value': 'rb-07947ed3b22e0289a'}
        props['route_table_name'] = {'type': 'string', 'value': 'rtTest'}
        props['attachment_type'] = {'type': 'string', 'value': 'GatewayId'}
        props['attachment_id'] = {'type': 'string', 'value': 'igw-02d8eba9ee50f7001'}

        return PropValueMap(props)


    def __resource_properties_route(self):
        props = {}
        props['ec2_access_key'] = {'type': 'string', 'value': 'AKIAQZP7WXUWSL5VK4HV'}
        props['ec2_secret_key'] = {'type': 'string', 'value': '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'}
        props['aws_side_asn'] = {'type': 'string', 'value': '64512'}
        props['vpc_id'] = {'type': 'string', 'value': 'vpc-073c193a752a9ad3a'}
        props['transit_id'] = {'type': 'string', 'value': 'tgw-06502eb028c110066'}
        props['transit_route_table_id'] = {'type': 'string', 'value': 'tgw-rtb-0b5895e4a2f5be275'}
        props['transit_gateway_name'] = {'type': 'string', 'value': 'tgTest'}
        props['vpc073c193a752a9ad3aAttachment'] = {'type': 'string', 'value': 'tgw-attach-08bfecbd635408bde'}
        props['subnet_id'] = {'type': 'string', 'value': 'subnet-02e1adc78a85bfcbf'}
        props['cidr_block'] = {'type': 'string', 'value': '192.0.1.0/24'}
        props['access_domain_state'] = {'type': 'string', 'value': 'global'}
        props['propagation_default_route_tableId'] = {'type': 'string', 'value': 'disable'}
        props['auto_accept_shared_attachments'] = {'type': 'string', 'value': 'disable'}
        props['default_route_table_association'] = {'type': 'string', 'value': 'disable'}
        props['default_route_table_propagation'] = {'type': 'string', 'value': 'disable'}
        props['dns_support'] = {'type': 'string', 'value': 'disable'}
        props['multicast_support'] = {'type': 'string', 'value': 'disable'}
        props['vpn_ecmp_support'] = {'type': 'string', 'value': 'disable'}
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

    def test_driver_1(self):
        system_properties = self.__system_properties()
        system_properties_vnet = self.__system_properties_vnet()
        system_properties_rt = self.__system_properties_rt()
        resource_properties = self.__resource_properties()
        deployment_location = self.__deployment_location()
        request_properties = self.__request_properties()
        resource_properties_vnet = self.__resource_properties_vnet()
        request_properties_rt = self.__resource_properties_rt()
        resource_properties_route = self.__resource_properties_route()
        path = os.path.abspath(os.getcwd())
        print(path)
        driver_files = DirectoryTree('resources/cloudformation/')
        print(driver_files.get_path())
        driver = ResourceDriverHandler()
        associated_topology = AssociatedTopology()
        resp = driver.execute_lifecycle('Create', driver_files, system_properties_vnet, resource_properties_vnet, request_properties, associated_topology, deployment_location)
        print(f'resp={resp.request_id}')
        #resp = driver.execute_lifecycle('Create', driver_files, system_properties, resource_properties, request_properties, associated_topology, deployment_location)
        #print(f'resp={resp.request_id}')
        #resp = driver.execute_lifecycle('Create', driver_files, system_properties_rt, request_properties_rt, request_properties, associated_topology, deployment_location)
        #print(f'resp={resp}')
        #resp = driver.execute_lifecycle('Create', driver_files, system_properties_tg, request_properties_tg, request_properties, associated_topology, deployment_location)
        #print(f'resp={resp}')
        #resp = driver.execute_lifecycle('CreateTgwRouteTableAssociation', driver_files, system_properties_tga, request_properties_tga, request_properties, associated_topology, deployment_location)
        #print(f'resp={resp}')
        #resp = driver.execute_lifecycle('CreateTgwRouteTableAssociation', driver_files, system_properties_tga1, request_properties_tga1, request_properties, associated_topology, deployment_location)
        #print(f'resp={resp}')
        

        time.sleep(50)
        resp = driver.get_lifecycle_execution(resp.request_id, deployment_location)
        print(f'response {resp}')
