import os
import mimetypes
from email.mime.base import MIMEBase
from email import encoders

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.png', '.docx', '.xlsx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def is_valid_attachment(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return False

    _, ext = os.path.splitext(file_path)

    if ext.lower() not in ALLOWED_EXTENSIONS:
        print(f"Error: File type '{ext}' is not allowed.")
        return False

    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        print(f"Error: File '{file_path}' exceeds the size limit of 5MB.")
        return False

    return True


def attach_files(msg, file_paths):
    attached_files = 0

    for file_path in file_paths:
        if not is_valid_attachment(file_path):
            continue

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        main_type, sub_type = mime_type.split("/", 1)

        try:
            with open(file_path, "rb") as file:
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(file.read())

            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(file_path)}"
            )

            msg.attach(attachment)
            attached_files += 1
            print(f"Successfully attached: {file_path}")

        except Exception as e:
            print(f"Error attaching {file_path}: {e}")

    if attached_files == 0:
        print("No valid attachments were added.")
    else:
        print(f"{attached_files} file(s) successfully attached.")

    return msg
