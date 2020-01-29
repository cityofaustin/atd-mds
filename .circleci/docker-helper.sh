#!/usr/bin/env bash

export ATD_IMAGE="atddocker/atd-mds-etl";
#
# We need to assign the name of the branch as the tag to be deployed
#
export ATD_TAG="${CIRCLE_BRANCH}";

#
# Builds the docker image, tags it and publishes 
# the image to Docker Hub.
#
function build_container {
    # Let's make sure we are logged in
    echo "Logging in to Docker hub"
    docker login -u $ATD_DOCKER_USER -p $ATD_DOCKER_PASS

    # First build the image
    echo "docker build -f Dockerfile -t $ATD_IMAGE:$ATD_TAG .";
    docker build -f Dockerfile -t $ATD_IMAGE:$ATD_TAG .

    # Now we tag the image
    echo "docker tag $ATD_IMAGE:$ATD_TAG $ATD_IMAGE:$ATD_TAG;";
    docker tag $ATD_IMAGE:$ATD_TAG $ATD_IMAGE:$ATD_TAG;

    # We now publish the image
    echo "docker push $ATD_IMAGE:$ATD_TAG";
    docker push $ATD_IMAGE:$ATD_TAG;
}