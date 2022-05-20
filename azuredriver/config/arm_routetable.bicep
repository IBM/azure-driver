param route_table_name string = 'testrt'
param route_table_location string = 'centralindia'
param route_table_disable_bgp_route_propagation bool = false


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


