FROM python:3.12-alpine as buildimage

COPY . /tmp/app_install

RUN set -eux; \
# Install required build dependencies
    apk add --no-cache python3 py3-wheel py3-pip python3-dev gcc musl-dev cargo; \
# wheel all required packages
    cd /tmp/app_install; \
    pip wheel --wheel-dir=/root/wheels .

FROM python:3.12-alpine

COPY --from=buildimage /root/wheels /root/wheels
COPY docker/entrypoint.sh /entrypoint.sh

ENV SML2MQTT_FOLDER=/sml2mqtt \
    USER_ID=9001 \
    GROUP_ID=${USER_ID}

RUN set -eux; \
# Install required build dependencies
    apk add --no-cache su-exec tini; \
# install sml2mqtt
    pip install \
        --no-index \
        --find-links=/root/wheels \
        sml2mqtt; \
# clean up
	rm -rf /root/wheels; \
	rm -fr /tmp/*; \
# mkdir
    mkdir -p ${SML2MQTT_FOLDER}; \
# prepare entrypoint script
	chmod +x /entrypoint.sh;

WORKDIR /sml2mqtt
VOLUME ["${SML2MQTT_FOLDER}"]
ENTRYPOINT ["/entrypoint.sh"]

CMD ["su-exec", "sml2mqtt", "tini", "--", "python", "-m", "sml2mqtt", "--config", "/sml2mqtt/config.yml"]
