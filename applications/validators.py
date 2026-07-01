import os
import magic
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class SecureFileValidator:
    """
    Validates that the file has an allowed extension and its actual MIME type matches.
    Provides security against renamed malicious files.
    """

    def __init__(self, allowed_extensions=None, max_size_mb=5):
        self.allowed_extensions = [
            ext.lower() for ext in (
                allowed_extensions or [
                    'pdf',
                    'png',
                    'jpg',
                    'jpeg',
                    'doc',
                    'docx'])]
        self.max_size_mb = max_size_mb

        # Map extensions to their expected MIME types
        self.mime_types = {
            'pdf': [
                'application/pdf',
                'application/x-pdf',
                'application/acrobat',
                'applications/vnd.pdf',
                'text/pdf',
                'text/x-pdf'],
            'png': [
                'image/png',
                'application/png',
                'application/x-png'],
            'jpg': [
                'image/jpeg',
                'image/jpg',
                'image/jpe_',
                'image/pjpeg',
                'image/vnd.swiftview-jpeg',
                'image/x-citrix-jpeg'],
            'jpeg': [
                'image/jpeg',
                'image/jpg',
                'image/jpe_',
                'image/pjpeg',
                'image/vnd.swiftview-jpeg',
                'image/x-citrix-jpeg'],
            'doc': [
                'application/msword',
                'application/vnd.ms-office'],
            'docx': [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/zip'],
        }

    def __call__(self, file):
        # Check file size
        if file.size > self.max_size_mb * 1024 * 1024:
            raise ValidationError(f"File size must be under {self.max_size_mb}MB.")

        # Check file extension
        if not file.name or '.' not in file.name:
            raise ValidationError("File has no extension.")

        ext = os.path.splitext(file.name)[1][1:].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f"Unsupported file extension '{ext}'. Allowed extensions are: {
                    ', '.join(
                        self.allowed_extensions)}")

        # Check MIME type using python-magic
        # Read the first 2048 bytes for magic numbers
        file.seek(0)
        file_data = file.read(2048)
        file.seek(0)

        try:
            mime_type = magic.from_buffer(file_data, mime=True)
            # Some environments append charset, e.g. "text/plain; charset=utf-8"
            if mime_type and ';' in mime_type:
                mime_type = mime_type.split(';')[0].strip()
        except Exception:
            raise ValidationError(
                "Could not determine file type. The file might be corrupted.")

        expected_mimes = self.mime_types.get(ext, [])
        if mime_type not in expected_mimes:
            raise ValidationError(
                f"File content ({mime_type}) does not match the '{ext}' extension.")
