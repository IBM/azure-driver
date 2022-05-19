@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_ZRS'
  'Premium_LRS'
])
param storage_account_type string = 'Standard_LRS'
param storage_account_name string = 'testsa'
param storage_location string = 'centralindia'

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storage_account_name
  location: storage_location
  tags: {
    Creator: 'Cp4na'
  }
  sku: {
    name: storage_account_type
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
  }

}

output storageEndpoint object = storageAccount.properties.primaryEndpoints
