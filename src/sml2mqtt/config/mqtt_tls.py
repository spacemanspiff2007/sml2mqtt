import ssl
from logging import Logger
from pathlib import Path
from typing import Any, Literal

from aiomqtt import TLSParameters
from easyconfig import BaseModel
from pydantic import Field, field_validator


def _get_ssl_consts(prefix: str) -> dict[str, int]:
    return {name.removeprefix(prefix): getattr(ssl, name) for name in dir(ssl) if name.startswith(prefix)}


def get_ssl_verify_values() -> dict[str, int]:
    return _get_ssl_consts('CERT_')


def get_ssl_version_values() -> dict[str, int]:
    return _get_ssl_consts('PROTOCOL_')


class MqttTlsOptions(BaseModel):
    insecure: bool | None = Field(
        None, description='Enable/disable server hostname verification when using SSL/TLS.'
    )

    ca_certs: str | None = Field(
        None, alias='ca certificates',
        description='Path to Certificate Authority (CA) certificate file in PEM or DER format'
    )

    cert_file: str | None = Field(
        None, alias='cert file', description='Path to PEM encoded client certificate file'
    )
    key_file: str | None = Field(
        None, alias='key file', description='Path to PEM encoded private keys file'
    )
    file_password: str | None = Field(
        None, alias='file password', description='Password to encrypt the cert file or the key file if needed'
    )

    cert_reqs: Literal[tuple(get_ssl_verify_values())] | None = Field(
        None, alias='certificate requirement',
        description='Certificate requirement that the client imposes on the broker.'
    )
    tls_version: Literal[tuple(get_ssl_version_values())] | None = Field(
        None, alias='tls version', description='The version of the SSL/TLS protocol to be used.'
    )
    ciphers: str | None = Field(
        None, description='Which encryption ciphers are allowable for the connection'
    )

    @field_validator('ca_certs', 'cert_file', 'key_file')
    @classmethod
    def _ensure_file_exists(cls, v: str | None):
        if v is None:
            return None

        if not isinstance(v, str):
            raise TypeError()

        if not Path(v).is_file():
            raise FileNotFoundError(v)

        return v

    def get_client_kwargs(self, log: Logger) -> dict[str, Any]:
        cert_reqs = get_ssl_verify_values()[self.cert_reqs] if self.cert_reqs is not None else None
        tls_version = get_ssl_version_values()[self.tls_version] if self.tls_version is not None else None

        if self.insecure:
            log.warning('Verification of server hostname in server certificate disabled! '
                        'Use this only for testing, not for a real system!')

        return {
            'tls_insecure': self.insecure,
            'tls_params': TLSParameters(
                ca_certs=self.ca_certs,
                certfile=self.cert_file,
                keyfile=self.key_file,
                cert_reqs=cert_reqs,
                tls_version=tls_version,
                ciphers=self.ciphers,
                keyfile_password=self.file_password
            )
        }
