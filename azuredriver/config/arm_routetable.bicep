param route_table_name string = 'testrt'
param route_table_location string = 'centralindia'
param route_table_disable_bgp_route_propagation bool = false
param branch_offices array = []
param route_next_hop_ip_address string = ''


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

resource routes 'Microsoft.Network/routeTables/routes@2020-11-01' = [for bo in branch_offices: {
  parent: routeTables
  name: bo.name
  properties: {
    addressPrefix: bo.cidr
    nextHopType: 'VirtualAppliance'
    nextHopIpAddress: route_next_hop_ip_address
    hasBgpOverride: route_table_disable_bgp_route_propagation
  } 
}]

