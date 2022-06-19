"""All methods that check message signatures."""
import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_der_public_key

from rain_server.configuration.logger import get_logger


def check_signature(message: str, pubkey: str, signature: str) -> bool:
    """
    Checks if the message signature is valid.

    :param message: The message to check signature
    :param pubkey: The public key
    :param signature: The signature to check
    :return: True if the signature is valid
    """
    message_bytes = message.encode('utf-8')

    pubkey_key = load_der_public_key(base64.b64decode(pubkey), default_backend())
    signature_bytes = base64.b64decode(signature)
    try:
        pubkey_key.verify(
            signature_bytes,
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except InvalidSignature as err:
        get_logger().error(err)
        return False
    else:
        return True
