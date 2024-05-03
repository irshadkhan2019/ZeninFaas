#!/bin/bash

# Define the file name
yaml_file_dep="mydelployHpa.yaml"
yaml_file_metric="components.yaml"

if [ -f "$yaml_file_dep" ]; then
    kubectl apply -f "$yaml_file_dep"
fi

if [ -f "$yaml_file_metric" ]; then
    kubectl apply -f "$yaml_file_metric"
fi



