#!/bin/bash

#building bicep files
python3 -m pip install virtualenv
python3 -m virtualenv env
source env/bin/activate
python3 -m pip install azure-cli==2.29.2
for FILE in azuredriver/config/*
do 
if [[ $FILE == *.bicep ]]
then
#echo $FILE
az bicep build --file $FILE --outdir $PWD/azuredriver/config/json/
fi
done 
deactivate
rm -rf env
#completed building bicep files

python3 setup.py bdist_wheel
mkdir -p docker/whls
cp dist/azuredriver-0.0.1-py3-none-any.whl docker/whls/


pushd docker
IMAGE_TAG="azure-driver:0.0.2-"$(date +%Y%m%d_%H%M%S)
docker build -t $IMAGE_TAG .
popd

pushd helm
mkdir -p repo
helm package -d repo azure-driver
popd




# Helm chart is in helm/repo/aws-driver-0.0.1.tgz
