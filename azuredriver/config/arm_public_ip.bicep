param public_ip_address_name string = 'mdnpubipnew'
param public_ip_location string = 'centralindia'
param public_ip_address_version string = 'IPv4'
param public_ip_allocation_method string = 'Static'
param public_ip_sku_type_name string = 'Standard'
param public_ip_sku_tier_name string = 'Regional'
param public_ip_zones string = '1'

resource publicIPAddresses 'Microsoft.Network/publicIPAddresses@2020-11-01' = {
  name: public_ip_address_name
  location: public_ip_location
  tags: {
    Creator: 'Cp4na'
  }
  sku: {
    name: public_ip_sku_type_name
    tier: public_ip_sku_tier_name
  }
  zones: [
    public_ip_zones
  ]
  properties: {
    publicIPAddressVersion: public_ip_address_version
    publicIPAllocationMethod: public_ip_allocation_method
    idleTimeoutInMinutes: 4
    ipTags: []
  }
}
