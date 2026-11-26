from enum import Enum


class AzureCredentialType(Enum):
    ClientSecretCredential = ClientSecretCredential
    ManagedIdentityCredential = ManagedIdentityCredential
    CertificateCredential = CertificateCredential
