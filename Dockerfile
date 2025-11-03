# syntax=docker/dockerfile:1
ARG BASE_IMAGE=python:3.13-alpine

FROM $BASE_IMAGE AS buildimage
RUN apk add --no-cache py3-pip build-base
COPY . /tmp/sml2mqtt/source
RUN pip install --prefix /tmp/sml2mqtt/target /tmp/sml2mqtt/source

FROM $BASE_IMAGE
ENTRYPOINT [ "sml2mqtt" ]
CMD [ "--config", "/sml2mqtt/config.yml" ]
WORKDIR /sml2mqtt
COPY --from=buildimage /tmp/sml2mqtt/target/ /usr/local/
