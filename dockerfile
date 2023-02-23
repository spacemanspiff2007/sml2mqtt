FROM python:3.10-apline

VOLUME /sml2mqtt

RUN apk add --no-cache python3 py3-wheel py3-pip gcc musl-dev python3-dev git && \
    pip install --no-cache-dir --no-clean sml2mqtt && \
    apk del py3-wheel py3-pip gcc musl-dev python3-dev git && \
    rm -fr /tmp/* \
    cd  /sml2mqtt && \
CMD [ "sml2mqtt" ]
