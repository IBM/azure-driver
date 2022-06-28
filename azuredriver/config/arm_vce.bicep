@description('Virtual machine size')
param virtualMachineSize string = 'Standard_DS3_v2'

@description('The version of the Edge to deploy from Marketplace')
@allowed([
  'Virtual Edge 2.5'
  'Virtual Edge 3.x'
])
param EdgeVersion string = 'Virtual Edge 3.x'

@description('FQDN or IP address of VCO')
param VCO string = 'TargetVCO'

@description('Determines whether or not to ignore certificate errors')
@allowed([
  'true'
  'false'
])
param IgnoreCertErrors string = 'false'

@description('Activation Key')
param ActivationKey string = 'XXXX-XXXX-XXXX-XXXX'

@description('Name of the Virtual Edge')
param EdgeName string = 'velocloudVCE'

@description('The Public Key for Virtual Edge Instance paired with local private key')
param SslPublicKey string

@description('Determines whether or not a new virtual network should be provisioned.')
@allowed([
  'new'
  'existing'
])
param virtualNetworkNewOrExisting string = 'new'

@description('Virtual Network Name')
param vNetName string = 'AzureVNET'

@description('Azure location name')
param vceLocation string

@description('Virtual Network IP Address Space')
param vNetPrefix string = '10.0.0.0/16'

@description('Public Subnet Name for Edge WAN Interface within vNET')
param PublicSubnetName string = 'Public_SN'

@description('Public Subnet IP Range for Edge WAN Interface')
param PublicSubnet string = '10.0.0.0/24'

@description('Private Subnet Name for Edge LAN Interface witin vNET')
param PrivateSubnetName string = 'Private_SN'

@description('Private Subnet for Edge LAN Interface')
param PrivateSubnet string = '10.0.3.0/24'

@description('IP Address used for Edge LAN Interface GE3')
param EdgeGE3LANIP string = '10.0.3.4'

var virtualMachineName_var = EdgeName
var nic1_var = '${EdgeName}1-nic'
var nic2_var = '${EdgeName}2-nic'
var nic3_var = '${EdgeName}3-nic'
var ipGE1 = '${EdgeName}-1-ipconfig'
var ipGE2 = '${EdgeName}-2-ipconfig'
var ipGE3 = '${EdgeName}-3-ipconfig'
var publicIP_var = '${EdgeName}-publicIP'
var virtualNetworkName_var = vNetName
var subnet1Name = PublicSubnetName
var subnet2Name = PrivateSubnetName
var vNetPrefixSpace = vNetPrefix
var PublicSubnetSpace = PublicSubnet
var PrivateSubnetSpace = PrivateSubnet
var PrivateSubnetStartAddress = EdgeGE3LANIP
var routeTablePublic_var = '${vNetName}-PUB-RT'
var routeTablePrivate_var = '${vNetName}-PRI-RT'
var subnet1Ref = resourceId('Microsoft.Network/virtualNetworks/subnets', virtualNetworkName_var, subnet1Name)
var subnet2Ref = resourceId('Microsoft.Network/virtualNetworks/subnets', virtualNetworkName_var, subnet2Name)
var networkSecurityGroupName_var = 'VELO_vVCE_SG'
var sshKeyPath = '/home/vcadmin/.ssh/authorized_keys'
var sshPubKey = 'parameters(\'SslPublicKey\')'
var cloudinit = '#cloud-config\nvelocloud:\n vce:\n  vco: ${VCO}\n  activation_code: ${ActivationKey}\n  vco_ignore_cert_errors: ${IgnoreCertErrors}\n'
var images = {
  'Virtual Edge 2.5': {
    publisher: 'velocloud'
    offer: 'velocloud-virtual-edge'
    sku: 'velocloud-virtual-edge'
    version: '2.5.0'
  }
  'Virtual Edge 3.x': {
    publisher: 'velocloud'
    offer: 'velocloud-virtual-edge-3x'
    sku: 'velocloud-virtual-edge-3x'
    version: '3.0.0'
  }
}
var imageSku = images[EdgeVersion].sku
var imagePublisher = images[EdgeVersion].publisher
var imageOffer = images[EdgeVersion].offer
var imageVersion = images[EdgeVersion].version

resource virtualMachineName 'Microsoft.Compute/virtualMachines@2017-03-30' = {
  name: virtualMachineName_var
  location: vceLocation
  plan: {
    publisher: imagePublisher
    product: imageOffer
    name: imageOffer
  }
  properties: {
    hardwareProfile: {
      vmSize: virtualMachineSize
    }
    osProfile: {
      computerName: virtualMachineName_var
      adminUsername: 'vcadmin'
      customData: base64(cloudinit)
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: sshKeyPath
              keyData: SslPublicKey
            }
          ]
        }
      }
    }
    storageProfile: {
      imageReference: {
        publisher: imagePublisher
        offer: imageOffer
        sku: imageSku
        version: imageVersion
      }
      osDisk: {
        createOption: 'FromImage'
      }
      dataDisks: []
    }
    networkProfile: {
      networkInterfaces: [
        {
          properties: {
            primary: true
          }
          id: nic1.id
        }
        {
          properties: {
            primary: false
          }
          id: nic2.id
        }
        {
          properties: {
            primary: false
          }
          id: nic3.id
        }
      ]
    }
  }
}

resource virtualNetworkName 'Microsoft.Network/virtualNetworks@2017-06-01' = if (virtualNetworkNewOrExisting == 'new') {
  name: virtualNetworkName_var
  location: vceLocation
  properties: {
    addressSpace: {
      addressPrefixes: [
        vNetPrefixSpace
      ]
    }
    subnets: [
      {
        name: subnet1Name
        properties: {
          addressPrefix: PublicSubnetSpace
          routeTable: {
            id: routeTablePublic.id
          }
        }
      }
      {
        name: subnet2Name
        properties: {
          addressPrefix: PrivateSubnetSpace
          routeTable: {
            id: routeTablePrivate.id
          }
        }
      }
    ]
  }
}

resource nic1 'Microsoft.Network/networkInterfaces@2017-06-01' = {
  name: nic1_var
  location: vceLocation
  properties: {
    enableIPForwarding: true
    ipConfigurations: [
      {
        name: ipGE1
        properties: {
          subnet: {
            id: subnet1Ref
          }
          privateIPAllocationMethod: 'Dynamic'
        }
      }
    ]
    networkSecurityGroup: {
      id: networkSecurityGroupName.id
    }
  }
  dependsOn: [
    virtualNetworkName
  ]
}

resource nic2 'Microsoft.Network/networkInterfaces@2017-06-01' = {
  name: nic2_var
  location: vceLocation
  properties: {
    enableIPForwarding: true
    ipConfigurations: [
      {
        name: ipGE2
        properties: {
          subnet: {
            id: subnet1Ref
          }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: publicIP.id
          }
        }
      }
    ]
    networkSecurityGroup: {
      id: networkSecurityGroupName.id
    }
  }
  dependsOn: [
    virtualNetworkName
  ]
}

resource nic3 'Microsoft.Network/networkInterfaces@2017-06-01' = {
  name: nic3_var
  location: vceLocation
  properties: {
    enableIPForwarding: true
    ipConfigurations: [
      {
        name: ipGE3
        properties: {
          subnet: {
            id: subnet2Ref
          }
          privateIPAllocationMethod: 'Static'
          privateIPAddress: PrivateSubnetStartAddress
        }
      }
    ]
    networkSecurityGroup: {
      id: networkSecurityGroupName.id
    }
  }
  dependsOn: [
    virtualNetworkName
  ]
}

resource publicIP 'Microsoft.Network/publicIPAddresses@2017-06-01' = {
  name: publicIP_var
  location: vceLocation
  properties: {
    publicIPAllocationMethod: 'Dynamic'
  }
}

resource routeTablePublic 'Microsoft.Network/routeTables@2015-06-15' = if (virtualNetworkNewOrExisting == 'new') {
  name: routeTablePublic_var
  location: vceLocation
  properties: {
    routes: [
      {
        name: 'DefaultRouteToInternet'
        properties: {
          addressPrefix: '0.0.0.0/0'
          nextHopType: 'Internet'
        }
      }
    ]
  }
}

resource routeTablePrivate 'Microsoft.Network/routeTables@2015-06-15' = if (virtualNetworkNewOrExisting == 'new') {
  name: routeTablePrivate_var
  location: vceLocation
  properties: {
    routes: [
      {
        name: 'DefaultRouteToGE3'
        properties: {
          addressPrefix: '0.0.0.0/0'
          nextHopType: 'VirtualAppliance'
          nextHopIpAddress: PrivateSubnetStartAddress
        }
      }
    ]
  }
}

resource networkSecurityGroupName 'Microsoft.Network/networkSecurityGroups@2016-09-01' = {
  name: networkSecurityGroupName_var
  location: vceLocation
  properties: {
    securityRules: [
      {
        name: 'VCMP'
        properties: {
          priority: 1000
          sourceAddressPrefix: '*'
          protocol: '*'
          destinationPortRange: '*'
          access: 'Allow'
          direction: 'Inbound'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'SSH'
        properties: {
          priority: 1001
          sourceAddressPrefix: '*'
          protocol: '*'
          destinationPortRange: '*'
          access: 'Allow'
          direction: 'Inbound'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'SNMP'
        properties: {
          priority: 1002
          sourceAddressPrefix: '*'
          protocol: '*'
          destinationPortRange: '*'
          access: 'Allow'
          direction: 'Inbound'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}
