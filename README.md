[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build Status](https://travis-ci.com/IBM/azure-driver.svg?branch=master)](https://travis-ci.com/IBM/azure-driver)

# Azure Driver
Lifecycle driver implementation that uses Azure templates to execute operations.

Please read the following guides to get started with the lifecycle Driver:

## Developer

- [Developer Docs](./developer_docs/index.md) - docs for developers to install the driver from source or run the unit tests

## User

- [User Guide](./docs/index.md)

# Build

Use the `build.py` script to build the Docker image and Helm chart.


# Deployment Location

The Azure driver expects an `Azure` deployment location with the following properties:

* AZURE_SUBSCRIPTION: the Azure subscription ID of your Azure account
* AZURE_CLIENTSECRET: the Azure client Secret Key of your Azure account
* AZURE_CLIENTID: the Azure client Id of your Azure account
* AZURE_TENANTID: the Azure tenant Id of your Azure account

