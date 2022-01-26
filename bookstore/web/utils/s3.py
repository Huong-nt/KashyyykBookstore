import boto3
from botocore.exceptions import ClientError
import logging

# AWS_ACCESS_KEY_ID = 'AKIAI7BO5AHOKPO7AQ6A'
# AWS_SECRET_ACCESS_KEY = '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'

FILE_CONTENT_TYPES = {  # these will be used to set the content type of S3 object. It is binary by default.
    'aac': 'audio/aac',
    'wav': 'audio/wav',
    'wmv': 'text/plain',
    'mp3': 'audio/mpeg',
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'doc': 'application/msword',

    'bin': 'application/octet-stream',
    'hex': 'application/octet-stream',
}


class S3:
    def __init__(self, client):
        """
        Arguments:
            client -- boto3 client 
        """
        self.client = client
    


    def upload_public(self,  bucket_name, key_name, file, file_extension):
        """Uploads a given StringIO object to S3. Closes the file after upload.
        Returns the URL for the object uploaded.
        Note: The acl for the file is set as 'public-acl' for the file uploaded.
        Arguments:
            bucket_name -- name of the bucket where file needs to be uploaded.
            key_name -- key name to be kept in S3.
            file -- StringIO object which needs to be uploaded.
            extension -- content type that needs to be set for the S3 object.
        """
        try:
            content_type = FILE_CONTENT_TYPES[file_extension]
            response = self.client.put_object(
                ACL='public-read',
                Body=file.getvalue(),
                Bucket=bucket_name,
                ContentType=content_type,
                Key=key_name,
            )
            print(response)
            if 'ResponseMetadata' not in response:
                raise Exception('upload false')
            if 'HTTPStatusCode' not in response['ResponseMetadata']:
                raise Exception('upload false')
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception('upload false')
        except Exception as e:
            print('upload_s3_false:')
            print(e)
            return None
        # close stringio object
        file.close()
        # object_url = f"https://s3.amazonaws.com/{bucket_name}/{key_name}"
        object_url = f"http://{bucket_name}.s3.amazonaws.com/{key_name}"
        return object_url
