FROM python:3.10-alpine

VOLUME /sml2mqtt

COPY . /tmp/sml2mqtt_src

RUN apk add --no-cache python3 py3-wheel py3-pip gcc musl-dev python3-dev && \
    # install sml2mqtt from local dir
    pip install --no-cache-dir /tmp/sml2mqtt_src && \
    # cleanup
    pip install --no-cache-dir pyclean && pyclean /usr && pip uninstall -y pyclean setuptools wheel pip && \
    apk del py3-wheel py3-pip gcc musl-dev python3-dev && \
    rm -fr /tmp/*

WORKDIR /sml2mqtt
CMD [ "sml2mqtt", "--config", "/sml2mqtt/config.yml"]
