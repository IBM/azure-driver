param route_table_name string = 'testrt'
param route_table_location string = 'centralindia'
param route_table_disable_bgp_route_propagation bool = false
param private_or_public string = 'public'
param local_or_global string = 'local'
param branch_office_cidr string
param private_static_ip string


resource routeTables 'Microsoft.Network/routeTables@2020-11-01' = {
  name: route_table_name
  location: route_table_location
  tags: {
    Creator: 'Cp4na'
  }
  properties: {
    disableBgpRoutePropagation: route_table_disable_bgp_route_propagation
    routes: []
  }
}


resource branchofficeroute 'Microsoft.Network/routeTables/routes@2020-11-01' = if ((private_or_public == 'private') && (local_or_global == 'global')) {
  name: 'BranchOfficeRoute'
  parent: routeTables
  properties: {
    addressPrefix: branch_office_cidr
    hasBgpOverride: route_table_disable_bgp_route_propagation
    nextHopIpAddress: private_static_ip
    nextHopType: 'VirtualAppliance'
  }
}
