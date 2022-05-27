# Azure python driver

## Introduction

   Azure Driver is a python based driver developed from Ignition framework which is a python flask application. This will manage azure resource lifecyle using Azure python SDK. Each azure resources can be created/deleted using Azure bicep templates

## Install Steps

   Install azure-driver helm chart 

   ```
     helm install azure-driver azure-driver-0.0.1.tgz  -n <namespace>
   ``` 

   To install helm chart with a specific image, image could be pushed to a Docker registry and installed as follows:

   ```
   helm install azure-driver aws-driver-0.0.1.tgz --set docker.image=[registry]/azure-driver
   ``` 

## Configuration

    Steps to configure azure-driver to lmctl enviornment. This is to register azure driver to resource manager

    1. save the certificate from the secret

    ```
       oc get secret azure-driver-tls -o 'go-template={{index .data "tls.crt"}}' | base64 -d > azuredriver-tls.pem
    ```
    
    2. configure and activate the lmctl environment for the required OCP cluster

    3. Add/configure the azure-driver to the resource manager

    ```
       lmctl resourcedriver add --type azure --url https://azure-driver:7275 --certificate azuredriver-tls.pem -e <lmctl-env-name>
    ```

## Deployment Location

The AZURE driver expects an `AZURE` deployment location with the following properties:

* tenantId: Azure tenant ID
* clientId: Azure Client ID for the registered application
* clientSecret: Azure Client Secret for the registered application
* subscriptionId: Azure Subscription ID


## Scalability

  There are two ways to scale the azure-driver to address  production grade traffic

   ### 1. By increasing no of processes and threads

      With Gunicorn support, aws-driver can handle huge traffic by configuring no of processes and threads to the helm install command as below

      ```
         helm install azure-driver azure-driver-0.0.1.tgz --set docker.image=azure-driver--set docker.version=0.0.2 --set app.config.env.NUM_PROCESSES=<processes> --set --set app.config.env.NUM_THREADS=<threads> --set resources.requests.cpu=2*<processes>+1  --set resources.limits.cpu=2<processes>+1 -n <namespace>
      ```
      Note: Default no of processes are 9 and no of threads are 8 which are typically sufficient for production grade applications. Whenever you are increasing the no of processes, the cpu resources also should be increased accordingly as mentioned in the above command. There may be a need to increase the memory if required.

   ### 2. By scaling out the pod instances
     
    The easiest way to handle huge traffic if the default values are not sufficient is to increase the pod replicas

      ```
        oc scale deploy azure-driver --replicas <required-pod-replicas>
      ```
     

