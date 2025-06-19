# syntax=docker/dockerfile:1
ARG BASE_IMAGE=python:3.12-alpine

FROM $BASE_IMAGE AS buildimage
# Install required build dependencies
RUN apk add --no-cache python3 py3-wheel py3-pip python3-dev gcc musl-dev cargo
# wheel all required packages
COPY . /tmp/app_install
RUN cd /tmp/app_install && pip wheel --wheel-dir=/root/wheels .

FROM $BASE_IMAGE
# Install dependencies for entrypoint script
RUN apk add --no-cache shadow
COPY docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD [ "sml2mqtt", "--config", "/sml2mqtt/config.yml" ]
ARG USER_ID=9001
ENV SML2MQTT_FOLDER=/sml2mqtt \
    USER_ID=${USER_ID} \
    GROUP_ID=${USER_ID}
WORKDIR /sml2mqtt

# Install sml2mqtt
COPY --from=buildimage /root/wheels /root/wheels
RUN <<EOF
  set -eux
  pip install --no-index --find-links=/root/wheels sml2mqtt
  rm -rf /root/wheels /tmp/*
EOF
