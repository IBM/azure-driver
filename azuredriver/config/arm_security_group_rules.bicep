param network_security_group_name string = 'Test'
param nsg_rule_name string = 'ruleone'
param priority int = 1000
param access string = 'Allow'
param destination_address_prefixes string = '*'
param destination_port_range string = '2426'
param source_port_range string = '*'
param source_address_prefixes string = '*'
param direction string = 'Inbound'
param protocol string = 'Tcp'



resource networkSecurityGroup 'Microsoft.Network/networkSecurityGroups@2020-11-01'  existing = {
  name: network_security_group_name
}

resource networkSecurityGroupRule 'Microsoft.Network/networkSecurityGroups/securityRules@2020-11-01' = {
  parent: networkSecurityGroup
  name: nsg_rule_name
  properties: {
    protocol: protocol
    sourcePortRange: source_port_range
    destinationPortRange: destination_port_range
    sourceAddressPrefix: source_address_prefixes
    destinationAddressPrefix: destination_address_prefixes
    access: access
    priority: priority
    direction:direction
  }
}
