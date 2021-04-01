import boto3
import json
import logging
import http.client
import requests
import os
import sys

def create_obj(region_name, aws_access_key_id, aws_secret_access_key):
    client = boto3.client('iot', region_name=region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    resource = boto3.client('resource-groups', region_name=region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    return client, resource



def createthingtype(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.create_thing_type(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}


def deprecatethingtype(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.deprecate_thing_type(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}


def deletethingtype(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.delete_thing_type(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}


def creatething(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.create_thing(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}


def updatething(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.update_thing(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}


def deletething(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.delete_thing(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}


def createthinggroup(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.create_thing_group(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}


def updatethinggroup(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.update_thing_group(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}


def deletethinggroup(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.delete_thing_group(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    
def creategroup(user_id, **kwargs):
    client , _ = user_id
    try:
        response = client.create_thing_group(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}

def deletegroup(user_id, **kwargs):
    _ , resource = user_id
    try:
        response = resource.delete_group(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    
def updategroup(user_id, **kwargs):
    _ , resource = user_id
    try:
        response = resource.update_group(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}

def createjob(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.create_job(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}

def deletejob(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.delete_job(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
        
def canceljob(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.cancel_job(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}

def listthings(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.list_things(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}

def listthingtypes(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.list_thing_types(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}

def listthinggroups(user_id, **kwargs):
    client, _ = user_id
    try:
        response = client.list_thing_groups(**kwargs)
        return response
    except Exception as err:
        logging.error(err)
        print("#err", err)
        return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}

def f_data(data,key,exc="",db=None):
    try:
        if exc == "es":
            return "'"+db.escape(str(data[key]))+"'"
        return "'"+str(data[key])+"'"
    except:
        return 'NULL'

def validate_account(db,acc_id):
    data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(acc_id) ,'status' :'active'},format="j")
    len_D=len(data_cred[1])
    db.releaseConnection()
    if len(data_cred[1])>0:
        return (len_D,data_cred[1])
    else:
        return (len_D,[])