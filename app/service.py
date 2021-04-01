import configparser
from mySQL import Database
from flask import flash, request, redirect, render_template, url_for
import flask
import datetime, json
from aws_service import *
import configparser
import bulk_service

db=Database()

config = configparser.ConfigParser()
config.read('config.ini')

service_port = config['SYSTEM']['service_port']

app = flask.Flask(__name__)
app.config["DEBUG"] = False

@app.route('/data/<string:dbinst>', methods=['GET','POST','PUT','DELETE','VIEW'])
def tables(dbinst):
    x=dbinst.split('-')
    try:
        databaseReq=x[0]+x[1].title()
    except:
        databaseReq=dbinst
    try:
        if request.method == 'VIEW':
            a,b = db.columnDef(databaseReq)
            return {"requiredFields": a , "availableFields": b}
    except:
        None

    try:
        payload = request.get_json()
    except:
        payload = {}
    try:
        filedList = payload['fields']
    except:
        filedList = []

    try:
        if request.method == 'POST' or request.method == 'PUT':
            condition = payload['data']
        else:
            condition = payload['where']
    except:
        condition={}
    
    if request.method == 'POST':
        statusDb=db.checkRequired(available=payload['data'].keys() , dbName=databaseReq)

        if statusDb != 'OK':
            return {'status':"401",'result':"KEY : " + str(statusDb) + " Not Present"}
    data=db.dbOperation(databaseReq,request.method,fields=filedList,data=condition,format='j')
    return {'status':data[0],'result':data[1]}

@app.route('/service/CreateThing', methods=['POST','GET'])
def f1():
    

    if request.method=="POST":

        acc_id=str(request.get_json()["accountId"])

        data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(acc_id) ,'status' :'active'},format="j")[1][0]
        if len(data_cred) == 0:
            return {'HTTPStatusCode': 401,"ResponseMetadata": "Account Disabled or Doesnot Exist"}

        payload = request.get_json()
        del payload['accountId']
        
        data=db.dbOperation("things","select",fields=['count(*)'],data={'thingName':str(payload["thingName"]) ,'awsAccountId' :str(acc_id),'status':'active'})[1][0]['count(*)']

        if data > 0:
            return {'HTTPStatusCode': 401,"ResponseMetadata": "Thing Already Exist"}    
        if "thingTypeName" in payload.keys():
            data_ty=db.dbOperation("thingType","select",fields=['thingTypeId'],data={'thingTypeName':payload["thingTypeName"] ,'awsAccountId' :str(acc_id), 'status' : 'active'})[1]

            if len(data_ty) == 0:
                return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingType Dosenot Exist"}
        else:
            data_ty=[{}]
        data_ty=data_ty[0]
        l_id=db.put("Insert into things set thingName= '"+payload["thingName"]+"', thingDescription="+f_data(payload,'attributePayload',"es",db)+", thingTypeId="+f_data(data_ty,'thingTypeId')+", awsAccountId='"+str(acc_id)+"', status='inactive'")
        print(l_id[1])
        client, _  = create_obj(data_cred['regionAWS'], data_cred['accessKey'], data_cred['secretKey'])
        
        try:
            response = client.create_thing(**payload)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                db.update("Update things set thingArn='"+response["thingArn"]+"' , thingUID='"+response["thingId"]+"', status ='active' where thingId='"+str(l_id[1])+"'")
            return response
        except Exception as err:
            logging.error(err)
            print("#err", err)
            return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    else:
        return {'HTTPStatusCode': 200, 'HelpUrl': "https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/iot.html#IoT.Client.create_thing"}

@app.route('/service/UpdateThing', methods=['GET','POST'])
def f2():
    
    if request.method=="POST":

        acc_id=acc_id=str(request.get_json()["accountId"])
        data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(acc_id) ,'status' :'active'},format="j")[1][0]

        payload= request.get_json()
        del payload['accountId']
        data=db.dbOperation("things","select",fields=['count(*)'],data={'thingName':str(payload["thingName"]) ,'awsAccountId' :str(acc_id),'status':'active'})[1][0]['count(*)']
        if data == 0:
            return {'HTTPStatusCode': 401,"ResponseMetadata": "Thing Disabled or Doesnot Exist"}
        version=db.dbOperation("things","select",fields=['version'],data={'thingName':str(payload["thingName"]) ,'awsAccountId' :str(acc_id)})[1][0]['version']
        
        if "thingTypeName" in payload.keys():
            data_ty=db.dbOperation("thingType","select",fields=['thingTypeId'],data={'thingTypeName':payload["thingTypeName"] ,'awsAccountId' :str(acc_id), 'status' : 'active'})[1]

            if len(data_ty) == 0:
                return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingType Dosenot Exist"}
        else:
            data_ty=[{}]
        data_ty=data_ty[0]
                
        client, _  = create_obj(data_cred['regionAWS'], data_cred['accessKey'], data_cred['secretKey'])
        try:
            payload.update({'expectedVersion':int(version)})
            payload.update({'removeThingType':False})
            response = client.update_thing(**payload)
            db.update("Update things set thingDescription="+f_data(payload,'attributePayload',"es",db)+", thingTypeId="+f_data(data_ty,'thingTypeId')+", version = version+1 where awsAccountId='"+str(acc_id)+"' and status='active' and thingName= '"+payload["thingName"]+"'")
            return response
        except Exception as err:
            logging.error(err)
            print("#err", err)
            return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    else:
        return {'HTTPStatusCode': 200, 'HelpUrl': "https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/iot.html#IoT.Client.update_thing"}

@app.route('/service/DeleteThing', methods=['GET','POST'])
def f3():

    if request.method=="POST":
        acc_id=acc_id=str(request.get_json()["accountId"])
        data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(acc_id) ,'status' :'active'},format="j")[1][0]
        payload= request.get_json()
        del payload['accountId']

        data=db.dbOperation("things","select",fields=['count(*)'],data={'thingName':str(payload["thingName"]) ,'awsAccountId' :str(acc_id),'status':'active'})[1][0]['count(*)']
        if data == 0:
            return {'HTTPStatusCode': 401,"ResponseMetadata": "Thing Disabled or Doesnot Exist"}
        version=db.dbOperation("things","select",fields=['version'],data={'thingName':str(payload["thingName"]) ,'awsAccountId' :str(acc_id)})[1][0]['version']

        client, _  = create_obj(data_cred['regionAWS'], data_cred['accessKey'], data_cred['secretKey'])

        try:
            payload.update({'expectedVersion':int(version)})
            response = client.delete_thing(**payload)
            db.update("Update things set status='inactive' where awsAccountId='"+str(acc_id)+"' and status='active' and thingName= '"+payload["thingName"]+"'")
            return response
        except Exception as err:
            logging.error(err)
            return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    else:
        return {'HTTPStatusCode': 200, 'HelpUrl': "https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/iot.html#IoT.Client.delete_thing"}

@app.route('/service/CreateThingGroup', methods=['GET','POST'])
def f4():
    
    if request.method=="POST":
        acc_id=acc_id=str(request.get_json()["accountId"])
        data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(acc_id) ,'status' :'active'},format="j")[1][0]
        payload= request.get_json()
        del payload['accountId']
        data_ty=db.dbOperation("thingGroup","select",fields=['count(*)'],data={'thingGroupName':str(payload["thingGroupName"]) ,'awsAccountId' :str(acc_id),'status':'active'})[1][0]['count(*)']
        if data_ty != 0:
                return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingGroup Already Exist"}
        if 'parentGroupName' in payload.keys():
            data_ty=db.dbOperation("thingGroup","select",fields=['thingGroupId'],data={'thingGroupName':payload["parentGroupName"] ,'awsAccountId' :str(acc_id), 'status' : 'active'})[1]

            if len(data_ty) == 0:
                return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingGroup Dosenot Exist"}
        else:
            data_ty=[{}]
        data_ty=data_ty[0]

        client, _  = create_obj(data_cred['regionAWS'], data_cred['accessKey'], data_cred['secretKey'])
        l_id=db.put("Insert into thingGroup set thingGroupName= '"+payload["thingGroupName"]+"', thingGroupDescription="+f_data(payload,'thingGroupProperties',"es",db)+", parentGroupId="+f_data(data_ty,'thingGroupId')+", awsAccountId='"+str(acc_id)+"', status='inactive', tags="+f_data(payload,'tags',"es",db))

        try:
            response = client.create_thing_group(**payload)
            if str(response['ResponseMetadata']['HTTPStatusCode']) == "200":
                db.update("Update thingGroup set thingGroupArn='"+response["thingGroupArn"]+"' , thingGroupUID='"+response["thingGroupId"]+"', status ='active' where thingGroupId='"+str(l_id[1])+"'")
            return response
        except Exception as err:
            logging.error(err)
            return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    else:
        return {'HTTPStatusCode': 200, 'HelpUrl': "https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/iot.html#IoT.Client.create_thing_group"}

@app.route('/service/UpdateThingGroup', methods=['GET','POST'])
def f5():
    
    if request.method=="POST":
        acc_id=acc_id=str(request.get_json()["accountId"])
        data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(acc_id) ,'status' :'active'},format="j")[1][0]

        payload= request.get_json()
        del payload['accountId']
        data=db.dbOperation("thingGroup","select",fields=['count(*)'],data={'thingGroupName':str(payload["thingGroupName"]) ,'awsAccountId' :str(acc_id),'status':'active'})[1][0]['count(*)']
        if data == 0:
            return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingGroup Disabled or Doesnot Exist"}
        version=db.dbOperation("thingGroup","select",fields=['version'],data={'thingGroupName':str(payload["thingGroupName"]) ,'awsAccountId' :str(acc_id)})[1][0]['version']
        
        if "parentGroupName" in payload.keys():
            data_ty=db.dbOperation("thingGroup","select",fields=['thingGroupId'],data={'thingGroupName':payload["parentGroupName"] ,'awsAccountId' :str(acc_id), 'status' : 'active'})[1]

            if len(data_ty) == 0:
                return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingType Dosenot Exist"}
        else:
            data_ty=[{}]
        data_ty=data_ty[0]
                
        client, _  = create_obj(data_cred['regionAWS'], data_cred['accessKey'], data_cred['secretKey'])
        try:
            payload.update({'expectedVersion':int(version)})
            response = client.update_thing_group(**payload)
            if str(response['ResponseMetadata']['HTTPStatusCode']) == "200":
                db.update("Update thingGroup set thingGroupDescription="+f_data(payload,'thingGroupProperties',"es",db)+", version = version+1 where awsAccountId='"+str(acc_id)+"' and status='active' and thingGroupName= '"+payload["thingGroupName"]+"'")
            return response
        except Exception as err:
            logging.error(err)
            return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    else:
        return {'HTTPStatusCode': 200, 'HelpUrl': "https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/iot.html#IoT.Client.update_thing_group"}

@app.route('/service/DeleteThingGroup', methods=['GET','POST'])
def f6():
    
    if request.method=="POST":
        acc_id=acc_id=str(request.get_json()["accountId"])
        data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(acc_id) ,'status' :'active'},format="j")[1][0]

        payload= request.get_json()
        del payload['accountId']
        data=db.dbOperation("thingGroup","select",fields=['count(*)'],data={'thingGroupName':str(payload["thingGroupName"]) ,'awsAccountId' :str(acc_id),'status':'active'})[1][0]['count(*)']
        if data == 0:
            return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingGroup Disabled or Doesnot Exist"}
        version=db.dbOperation("thingGroup","select",fields=['version'],data={'thingGroupName':str(payload["thingGroupName"]) ,'awsAccountId' :str(acc_id)})[1][0]['version']

        if data == 0:
            return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingGroup Disabled or Doesnot Exist"}

        client, _  = create_obj(data_cred['regionAWS'], data_cred['accessKey'], data_cred['secretKey'])    
        try:
            payload.update({'expectedVersion':int(version)})
            response = client.delete_thing_group(**payload)
            db.update("Update thingGroup set status='inactive' where awsAccountId='"+str(acc_id)+"' and status='active' and thingGroupName= '"+payload["thingGroupName"]+"'")
            return response
        except Exception as err:
            logging.error(err)
            return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    else:
        return {'HTTPStatusCode': 200, 'HelpUrl': "https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/iot.html#IoT.Client.delete_thing_group"}

@app.route('/service/CreateThingType', methods=['GET','POST'])
def f7():
    
    if request.method=="POST":

        acc_id=str(request.get_json()["accountId"])
        data_cred=validate_account(db,acc_id)
        if data_cred[0]>0:
            data_cred=data_cred[1][0]
        else:
            return {'HTTPStatusCode': 401,"ResponseMetadata": "Account Doesnot Exist"}
        print(data_cred)
        payload= request.get_json()
        del payload['accountId']
    
        data_ty=db.dbOperation("thingType","select",fields=['count(*)'],data={'thingTypeName':str(payload["thingTypeName"]) ,'awsAccountId' :str(acc_id),'status':'active'})[1][0]['count(*)']
        if data_ty != 0:
                return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingType Already Exist"}

        client, _  = create_obj(data_cred['regionAWS'], data_cred['accessKey'], data_cred['secretKey'])
        l_id=db.put("Insert into thingType set thingTypeName= '"+payload["thingTypeName"]+"', thingTypeDescription="+f_data(payload,'thingTypeProperties',"es",db)+", awsAccountId='"+str(acc_id)+"', status='inactive'")

        try:
            response = client.create_thing_type(**payload)
            if str(response['ResponseMetadata']['HTTPStatusCode']) == "200":
                db.update("Update thingType set thingTypeArn='"+response["thingTypeArn"]+"' , thingTypeUID='"+response["thingTypeId"]+"', status ='active' where thingTypeId='"+str(l_id[1])+"'")
            return response
        except Exception as err:
            logging.error(err)
            return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    else:
        return {'HTTPStatusCode': 200, 'HelpUrl': "https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/iot.html#IoT.Client.create_thing_type"}

@app.route('/service/DeprecateThingType', methods=['GET','POST'])
def f8():
    
    if request.method=="POST":

        acc_id=acc_id=str(request.get_json()["accountId"])
        data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(acc_id) ,'status' :'active'},format="j")[1][0]
        payload= request.get_json()
        del payload['accountId']
        
        data_ty=db.dbOperation("thingType","select",fields=['count(*)'],data={'thingTypeName':str(payload["thingTypeName"]) ,'awsAccountId' :str(acc_id),'status':'active'})[1][0]['count(*)']
        if data_ty == 0:
                return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingType Deprecated or Dosen't Exist"}

        client, _  = create_obj(data_cred['regionAWS'], data_cred['accessKey'], data_cred['secretKey'])
        try:
            response = client.deprecate_thing_type(**payload)
            if str(response['ResponseMetadata']['HTTPStatusCode']) == "200":
                db.update("Update thingType set status='deprecated' where awsAccountId='"+str(acc_id)+"' and status='active' and thingTypeName= '"+payload["thingTypeName"]+"'")
            return response
        except Exception as err:
            logging.error(err)
            return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    else:
        return {'HTTPStatusCode': 200, 'HelpUrl': "https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/iot.html#IoT.Client.deprecate_thing_type"}

@app.route('/service/DeleteThingType', methods=['GET','POST'])
def f9():
    
    if request.method=="POST":
        acc_id=acc_id=str(request.get_json()["accountId"])
        data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(acc_id) ,'status' :'active'},format="j")[1][0]
        payload= request.get_json()
        del payload['accountId']
        
        data_ty=db.dbOperation("thingType","select",fields=['count(*)'],data={'thingTypeName':str(payload["thingTypeName"]) ,'awsAccountId' :str(acc_id),'status':'deprecated'})[1][0]['count(*)']
        if data_ty == 0:
                return {'HTTPStatusCode': 401,"ResponseMetadata": "ThingType Deprecated or Dosen't Exist"}

        client, _  = create_obj(data_cred['regionAWS'], data_cred['accessKey'], data_cred['secretKey'])

        try:
            response = client.delete_thing_type(**payload)
            if str(response['ResponseMetadata']['HTTPStatusCode']) == "200":
                db.update("Update thingType set status='inactive' where awsAccountId='"+str(acc_id)+"' and status='deprecated' and thingTypeName= '"+payload["thingTypeName"]+"'")
            return response
        except Exception as err:
            logging.error(err)
            return {'HTTPStatusCode': 401, 'ResponseMetadata': str(err)}
    else:
        return {'HTTPStatusCode': 200, 'HelpUrl': "https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/iot.html#IoT.Client.delete_thing_type"}


try:
    db.init_db()
    bs=bulk_service.RefreshDB(db)
    bs.run_nonblock()
    app.run(host='0.0.0.0', port = service_port)
    bs.stop()
except:
    bs.stop()
    None