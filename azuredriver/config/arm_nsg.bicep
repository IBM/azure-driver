param network_security_group_name string = 'nsgwithrules'
param network_security_group_location string = 'centralindia'
param private_or_public string = 'public'
param local_or_global string = 'local'
param vnet_address_space string = ''

resource networkSecurityGroup 'Microsoft.Network/networkSecurityGroups@2019-02-01' = {
  name: network_security_group_name
  location: network_security_group_location
  tags: {
    Creator: 'Cp4na'
  }
}


resource outbound_internet_rule 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (private_or_public == 'private') {
  parent: networkSecurityGroup
  name: 'DenyInternetOutbound'
  properties: {
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: '*'
    destinationAddressPrefix: 'Internet'
    access: 'Deny'
    priority: 100
    direction: 'Outbound'
  }
}

resource outbound_vnet_rule_1 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (local_or_global == 'local')  {
  parent: networkSecurityGroup
  name: 'DenyVnetOutbound'
  properties: {
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: 'VirtualNetwork'
    destinationAddressPrefix: 'VirtualNetwork'
    access: 'Deny'
    priority: 102
    direction: 'Outbound'
  }
}

resource outbound_vnet_rule_2 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (local_or_global == 'local')  {
  parent: networkSecurityGroup
  name: 'AllowVnetCIDROutbound'
  properties: {
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: vnet_address_space
    destinationAddressPrefix: vnet_address_space
    access: 'Allow'
    priority: 101
    direction: 'Outbound'
  }
}

resource inbound_internet_rule 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (private_or_public == 'public')  {
  parent: networkSecurityGroup
  name: 'AllowInternetInbound'
  properties: {
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: 'Internet'
    destinationAddressPrefix: vnet_address_space
    access: 'Allow'
    priority: 105
    direction: 'Inbound'
  }
}

resource inbound_loadbalancer_rule 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (private_or_public == 'private')  {
  parent: networkSecurityGroup
  name: 'DenyLoadbalancerInbound'
  properties: {
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: 'AzureLoadBalancer'
    destinationAddressPrefix: '*'
    access: 'Deny'
    priority: 106
    direction: 'Inbound'
  }
}

resource inbound_vnet_rule_1 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (local_or_global == 'local')  {
  parent: networkSecurityGroup
  name: 'AllowVnetCIDRInbound'
  properties: {
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: vnet_address_space
    destinationAddressPrefix: vnet_address_space
    access: 'Allow'
    priority: 102
    direction: 'Inbound'
  }
}

resource inbound_vnet_rule_2 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (local_or_global == 'local')  {
  parent: networkSecurityGroup
  name: 'DenyVnetInbound'
  properties: {
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: 'VirtualNetwork'
    destinationAddressPrefix: 'VirtualNetwork'
    access: 'Deny'
    priority: 103
    direction: 'Inbound'
  }
}

