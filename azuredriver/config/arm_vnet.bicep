param vnet_name string = 'vnet'
param vnet_location string = 'centralindia'
param vnet_enable_ddos_protection bool = false
param vnet_private_endpoint_network_policies string = 'Enabled'
param vnet_private_link_service_network_policies string ='Enabled'
param vnet_default_cidr_block string = '10.0.1.0/24'
param vnet_address_space array = [
  '10.0.1.0/24'
  '10.0.2.0/24'
]

resource vNet 'Microsoft.Network/virtualNetworks@2020-11-01' = {
  name: vnet_name
  location: vnet_location
  tags: {
    Creator: 'Cp4na'
  }
  properties: {
        addressSpace: {
          addressPrefixes: vnet_address_space
        }
    subnets: [
      {
        name: 'default'
        properties: {
          addressPrefix: vnet_default_cidr_block
          delegations: []
          privateEndpointNetworkPolicies: vnet_private_endpoint_network_policies
          privateLinkServiceNetworkPolicies: vnet_private_link_service_network_policies
        }
      }
    ]
    virtualNetworkPeerings: []
    enableDdosProtection: vnet_enable_ddos_protection
  }
}
