#!/usr/bin/env bash

#
# Examples:
#
#   run build
#
#   runetl ~/etl.staging.env bash
#   runetl ~/etl.production.env app/process_test_run.py
#


#
# We also need to export the name of the docker image we are going to use
#
export ATD_DOCKER_IMAGE="atddocker/atd-mds-etl:local";

function runetl {

    # If the first argumentis build, then we build the container
    if [[ "$1" == "build" ]]; then
        docker build -f Dockerfile -t $ATD_DOCKER_IMAGE .;
        return;
    fi;

    # We are going to assume $1 is the file $2 is the command
    ATD_MDS_CONFIG=$1;
    RUN_COMMAND=$2;


    if [[ "${ATD_MDS_CONFIG}" =~ "production" ]];
    then
        RUN_ENVIRONMENT="production"
    else
        RUN_ENVIRONMENT="staging"
    fi

    # Makes sure the file exists
    if [[ -f "${ATD_MDS_CONFIG}" ]]; then
        echo "Using environment variables in '${ATD_MDS_CONFIG}'...";
    else
        echo "Error: The ATD_MDS_CONFIG variable is not set because it cannot find the file '${ATD_MDS_CONFIG}'";
        echo "Please refer to the documentation to create and env file.";
        return;
    fi;

    echo -e "\n\n----- ETL RUN ------";
    echo -e "Run Environment: \t${RUN_ENVIRONMENT}";
    echo -e "Run File: \t\t${RUN_COMMAND}";
    echo -e "ATD_MDS_CONFIG: \t${ATD_MDS_CONFIG}";
    echo -e "ATD_DOCKER_IMAGE: \t${ATD_DOCKER_IMAGE}";
    echo -e "--------------------\n";

    FINAL_COMMAND="docker run -it --rm --env-file ${ATD_MDS_CONFIG} ${ATD_DOCKER_IMAGE} ${RUN_COMMAND};"

    echo $FINAL_COMMAND;
    echo "--------------------------------------------------------------------";

    # Run Docker
    eval ${FINAL_COMMAND};

    # Exit
    return;
}