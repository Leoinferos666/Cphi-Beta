import uuid

from utils.database import (
    supabase
)


def upload_file(
    uploaded_file,
    folder="attachments"
):

    filename = (

        f"{uuid.uuid4()}_"

        f"{uploaded_file.name}"

    )

    file_bytes = (
        uploaded_file.getvalue()
    )

    supabase.storage.from_(
        "attachments"
    ).upload(
        filename,
        file_bytes
    )

    
    public_url = (
    supabase.storage
    .from_("attachments")
    .get_public_url(filename)
    )

    signed = (
        supabase.storage
        .from_("attachments")
        .create_signed_url(
            filename,
            60 * 60 * 24 * 365
        )
    )

    print(signed)

    return signed