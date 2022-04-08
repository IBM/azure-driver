param initiator_vnet_name string = 'svnet'
param acceptor_vnet_name string = 'pvnet'
param peering_state string = 'Connected'
param allow_virtual_network_access bool = true
param allow_forwarded_traffic bool = true
param allow_gateway_transit bool = false
param use_remote_gateways bool = false
param acceptor_vnet_rg_name string = 'mdnrg'
param acceptor_vnet_subscription_id string = 'fe42dccb-7208-4832-9ae1-694b971a67a0'

var acceptor_vnet_id = '/subscriptions/${acceptor_vnet_subscription_id}/resourceGroups/${acceptor_vnet_rg_name}/providers/Microsoft.Network/virtualNetworks/${acceptor_vnet_name}'

resource vnet_peering 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2020-11-01' = {
  name: '${initiator_vnet_name}/${initiator_vnet_name}-to-${acceptor_vnet_name}'
  properties: {
    peeringState: peering_state
    remoteVirtualNetwork: {
      id: acceptor_vnet_id
    }
    allowVirtualNetworkAccess: allow_virtual_network_access
    allowForwardedTraffic: allow_forwarded_traffic
    allowGatewayTransit: allow_gateway_transit
    useRemoteGateways: use_remote_gateways
  }
}
