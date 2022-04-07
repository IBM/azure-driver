
param vm_network_security_group_name string = 'mdnnsg'
param vm_network_interface_name string = 'mdnnic'


var netinterfaceid = resourceId(resourceGroup().name, 'Microsoft.Network/networkInterfaces', vm_network_interface_name)
var nsgId = resourceId(resourceGroup().name, 'Microsoft.Network/networkSecurityGroups', vm_network_security_group_name)


param vm_name string = 'mdnvmnew'
param vm_location string = 'centralindia'
param vm_zone string = '1'
param vm_hardware_profile string = 'Standard_B1s'

param vm_image_publisher string = 'canonical'
param vm_image_flavor string = '0001-com-ubuntu-server-focal'
param vm_image_version string = '20_04-lts-gen2'

param vm_os_disk_type string = 'Linux'
param vm_os_disk_storage_type string = 'StandardSSD_LRS'
param vm_os_disk_size int = 30

param vm_data_disk_storage_type string = 'StandardSSD_LRS'
param vm_data_disk_size int = 8

param vm_computer_name string = 'mdnvmone'
param vm_admin_username string = 'mdnuser'
@secure()
param vm_admin_password string = 'mDN@123456789'


resource virtualMachines_resource 'Microsoft.Compute/virtualMachines@2021-11-01' = {
  name: vm_name
  location: vm_location
  tags: {
    Creator: 'Cp4na'
  }
  zones: [
    vm_zone
  ]
  properties: {
    hardwareProfile: {
      vmSize: vm_hardware_profile
    }
    storageProfile: {
      imageReference: {
        publisher: vm_image_publisher
        offer: vm_image_flavor
        sku: vm_image_version
        version: 'latest'
      }
      osDisk: {
        osType: 'Linux'
        name: '${vm_name}_osdisk'
        createOption: 'FromImage'
        caching: 'ReadWrite'
        managedDisk: {
          storageAccountType: vm_os_disk_storage_type
        }
        deleteOption: 'Delete'
        diskSizeGB: vm_os_disk_size
      }
      dataDisks: [
        {
          lun: 0
          name: '${vm_name}_data_disk'
          createOption: 'Empty'
          caching: 'None'
          writeAcceleratorEnabled: false
          managedDisk: {
            storageAccountType: vm_data_disk_storage_type
          }
          deleteOption: 'Delete'
          diskSizeGB: vm_data_disk_size
          toBeDetached: false
        }
      ]
    }
    osProfile: {
      computerName: vm_computer_name
      adminUsername: vm_admin_username
      adminPassword: vm_admin_password
      linuxConfiguration: {
        disablePasswordAuthentication: false
        provisionVMAgent: true
        patchSettings: {
          patchMode: 'ImageDefault'
          assessmentMode: 'ImageDefault'
        }
      }
      secrets: []
      allowExtensionOperations: true
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: netinterfaceid
          properties: {
            deleteOption: 'Delete'
          }
        }
      ]
    }
    diagnosticsProfile: {
      bootDiagnostics: {
        enabled: true
      }
    }
  }
}
