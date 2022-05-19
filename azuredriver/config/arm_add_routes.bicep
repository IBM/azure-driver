param route_table_name string = 'testrtone'
param route_name string = 'testroute'
param route_next_hop_type string = 'VirtualAppliance'
param route_address_prefix string = '10.0.0.0/24'
param route_next_hop_ip_address string = ''
param route_has_bgp_override bool = false


resource routeTables 'Microsoft.Network/routeTables@2020-11-01' existing = {
  name: route_table_name
}


resource routes 'Microsoft.Network/routeTables/routes@2020-11-01' = {
  parent: routeTables
  name: route_name
  properties: {
    addressPrefix: route_address_prefix
    nextHopType: route_next_hop_type
    nextHopIpAddress: route_next_hop_ip_address
    hasBgpOverride: route_has_bgp_override
  }
}
