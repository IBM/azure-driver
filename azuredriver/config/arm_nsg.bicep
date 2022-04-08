param network_security_group_name string = 'nsgwithrules'
param network_security_group_location string = 'centralindia'
param private_or_public string = 'public'
param local_or_global string = 'local'

resource networkSecurityGroup 'Microsoft.Network/networkSecurityGroups@2019-02-01' = {
  name: network_security_group_name
  location: network_security_group_location
  tags: {
    Creator: 'Cp4na'
  }
}

resource outbound_internet_rule 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (private_or_public == 'private') {
  parent: networkSecurityGroup
  name: 'outbound_internet_rule'
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

resource outbound_vnet_rule 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (local_or_global == 'local')  {
  parent: networkSecurityGroup
  name: 'outbound_vnet_rule_access'
  properties: {
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: 'VirtualNetwork'
    destinationAddressPrefix: 'VirtualNetwork'
    access: 'Deny'
    priority: 101
    direction: 'Outbound'
  }
}

resource inbound_vnet_rule 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = if (local_or_global == 'local')  {
  parent: networkSecurityGroup
  name: 'inbound_vnet_rule_access'
  properties: {
    protocol: '*'
    sourcePortRange: '*'
    destinationPortRange: '*'
    sourceAddressPrefix: 'VirtualNetwork'
    destinationAddressPrefix: 'VirtualNetwork'
    access: 'Deny'
    priority: 102
    direction: 'Inbound'
  }
}

