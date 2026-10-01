import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Generate rsa key pair for authentication"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Replace existing keys. Invalidates every token in circulation.",
        )

    def handle(self, *args, **options):
        private_path = settings.JWT_KEY_DIR / "private_key.pem"
        public_path = settings.JWT_KEY_DIR / "public_key.pem"

        if private_path.exists() and not options["force"]:
            raise CommandError(
                f"{private_path} already exists. Re-run with --force to replace it, "
                "which will log out every user and invalidate all issued tokens."
            )

        settings.JWT_KEY_DIR.mkdir(parents=True, exist_ok=True)

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Open 0600 rather than chmod'd afterwards, so the private key is
        # never world-readable, not even briefly.
        fd = os.open(private_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(private_key_bytes)

        public_key = private_key.public_key()

        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        public_path.write_bytes(public_key_bytes)

        self.stdout.write(self.style.SUCCESS(f"Wrote {private_path} and {public_path}"))
