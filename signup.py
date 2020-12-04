import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json

USER_POOL_ID = 'us-east-1_4LyZzkFb9'
CLIENT_ID = '68ko3jles6b1e78c71pg56tl21'

client = boto3.client('cognito-idp')
sign = False
message = ''


def signup_user(username, password):
    try:
        sign = False
        resp = client.sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            Password=password
            )
        response = client.admin_confirm_sign_up(
        UserPoolId=USER_POOL_ID,
        Username=username
        )
        sign = True
        message = 'You have been successfully signed up'

    except:
    	message = 'Username or Email already exists'

    return message, sign