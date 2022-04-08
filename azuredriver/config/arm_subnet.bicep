param vnet_name string = 'vnet'
param subnet_name string = 'vnetsubnet'
param subnet_private_network_endpoint_policies string = 'Enabled'
param subnet_private_link_service_network_policies string = 'Enabled'
param subnet_cidr_block string = '10.0.2.0/24'
param route_table_name string = 'testrt'
param network_security_group_name string = 'mdnnsg'


resource vNet 'Microsoft.Network/virtualNetworks@2020-11-01' existing = {
  name: vnet_name
}

resource routeTables 'Microsoft.Network/routeTables@2020-11-01' existing = {
  name: route_table_name
}

resource networkSecurityGroups 'Microsoft.Network/networkSecurityGroups@2019-02-01' existing = {
  name: network_security_group_name
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2020-11-01' = {
  parent: vNet
  name: subnet_name
  properties: {
    addressPrefix: subnet_cidr_block
    networkSecurityGroup: {
      id: networkSecurityGroups.id
    }
    routeTable: {
      id: routeTables.id
    }
    serviceEndpoints: []
    delegations: []
    privateEndpointNetworkPolicies: subnet_private_network_endpoint_policies
    privateLinkServiceNetworkPolicies: subnet_private_link_service_network_policies
  }
}
