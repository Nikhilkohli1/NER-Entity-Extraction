import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json

USER_POOL_ID = 'us-east-1_4LyZzkFb9'
CLIENT_ID = '68ko3jles6b1e78c71pg56tl21'
CLIENT_SECRET = ''

client = boto3.client('cognito-idp')
sign = False
    

def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'), 
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2


def signup_user(username, email, name, password):
    try:
        sign = False
        resp = client.sign_up(
            ClientId=CLIENT_ID,
            SecretHash=get_secret_hash(username),
            Username=username,
            Password=password, 
            UserAttributes=[
            {
                'Name': "name",
                'Value': name
            },
            {
                'Name': "email",
                'Value': email
            }
            ],
            ValidationData=[
                {
                'Name': "email",
                'Value': email
            },
            {
                'Name': "custom:username",
                'Value': username
            }
			])
        message = 'Please confirm your signup, check Email for validation code'
        sign = True

    except:
    	message = 'Username or Email already exists'

    return message, sign