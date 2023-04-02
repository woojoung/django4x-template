# import logging
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework import permissions, views, status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from .utils import md5_hex_digest, now_int


# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
def create_pre_signed_url(s3_command, bucket_name, object_name, expiration=3600):
    if s3_command not in ['get_object', 'put_object']:
        return ClientError('Invalid s3 command', 'create_pre_signed_url')

    # Generate a pre_signed URL for the S3 object
    s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    try:
        result = s3_client.generate_presigned_url(
            s3_command, Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=expiration)
    except ClientError as client_error:
        # logging.error(e)
        # return None
        result = client_error

    # The response contains the pre_signed URL
    return result


# https://docs.aws.amazon.com/ko_kr/ses/latest/dg/send-an-email-using-sdk-programmatically.html
def send_email(recipient, subject, body_html):
    client = boto3.client('ses', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name=settings.AWS_REGION)

    try:
        # Provide the contents of the email.
        result = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject,
                },
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': body_html,
                    },
                },
            },
            Source=settings.AWS_SES_SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as client_error:
        result = client_error
    # else:
    #     print(result['MessageId'])

    return result


@permission_classes([permissions.IsAuthenticated])
class S3View(views.APIView):
    @classmethod
    def post(cls, request):
        file_path = request.data.get('file_path', '')
        if file_path == '':
            return Response(None, status.HTTP_400_BAD_REQUEST)

        file_name = file_path.split('\\').pop()
        file_extension = file_name.split('.').pop().lower()

        s3_command = 'put_object'
        object_name = '.'.join([md5_hex_digest(file_name), str(now_int()), str(request.user.id), file_extension])

        pre_signed_url = create_pre_signed_url(s3_command, settings.AWS_S3_BUCKET_PUBLIC, object_name)
        if isinstance(pre_signed_url, ClientError):
            return Response({'detail': str(pre_signed_url)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Access to XMLHttpRequest at 'https://pre_signed_url'
        # from origin 'https://origin' has been blocked by CORS policy:
        # Response to preflight request doesn't pass access control check:
        # No 'Access-Control-Allow-Origin' header is present on the requested resource.

        return Response({'pre_signed_url': pre_signed_url}, status.HTTP_200_OK)
