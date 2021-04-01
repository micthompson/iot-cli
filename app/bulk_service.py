import logging as log
import os
import threading
import time
import requests
import sys
import json
import socket
from datetime import datetime
import inspect

from aws_service import create_obj


class RefreshDB(object):
    def __init__(self,dbs):
        self._thread = threading.Thread(target=self.run)
        self._thread_stop = threading.Event()
        self._thread.daemon = False
        self.db=dbs
        self.counting=0
        log.getLogger().setLevel(log.INFO)
        
    def get_things(self,login, credentials,nextToken=''):
        log.info("Starting things download thread for account: %s " % (credentials['accountName']))
        self.db.createConnection()
        try:
            client , _ = login
            if nextToken=='':
                response=client.list_things(maxResults=10)
            else:
                response=client.list_things(maxResults=10, nextToken=nextToken)
            if len(response['things']) > 0:
                for thing in response['things']:
                    count = self.db.get("Select count(*) from things where thingName = '%s' and awsAccountId= '%s' and status='active'" %(thing['thingName'], credentials['accountId']),'x')[1][0][0]
                    if count == 0:
                        if 'thingTypeName' in thing.keys():
                            data=self.db.get("Select thingTypeId from thingType where ThingTypeName='%s' and awsAccountId='%s' and status in ('active','deprecated')" %(thing['thingTypeName'],str(credentials['accountId'])),'j')[1][0]

                            ins_id = self.db.put("Insert into things set thingName= '%s' , thingArn='%s' , thingDescription= '%s', version= '%s' ,awsAccountId = '%s', thingTypeId = '%s' , status='active'" %(thing['thingName'],thing['thingArn'],self.db.escape(thing['attributes']),thing['version'],str(credentials['accountId']),data['thingTypeId']))
                        else:
                            ins_id = self.db.put("Insert into things set thingName= '%s' , thingArn='%s' , thingDescription= '%s', version= '%s' ,awsAccountId = '%s' , status='active'" %(thing['thingName'],thing['thingArn'],self.db.escape(thing['attributes']),thing['version'],str(credentials['accountId'])))
                        log.info("Thing added to database on ID: %s" % (str(ins_id)))
                if 'nextToken' in response.keys():
                    self.get_things(credentials,response['nextToken'])
            else:
                log.info("No things to be added")
            self.db.releaseConnection()
        except Exception as ex:
            self.db.releaseConnection()
            log.exception('EXCEPTION: Downloading Things Failed: {}'.format(ex))
            pass
    
    def get_thing_types(self,login, credentials,nextToken=''):
        log.info("Starting thingTypes download thread for account: %s " % (credentials['accountName']))
        self.db.createConnection()
        try:
            client , _ = login
            if nextToken=='':
                response=client.list_thing_types(maxResults=10)
            else:
                response=client.list_thing_types(maxResults=10, nextToken=nextToken)
            if len(response['thingTypes']) > 0:
                for thing in response['thingTypes']:
                    if thing['thingTypeMetadata']['deprecated'] == True:
                            status='deprecated'
                    else:
                        status='active'
                    count = self.db.get("Select count(*) from thingType where thingTypeName = '%s' and awsAccountId= '%s' and status='%s'" %(thing['thingTypeName'], credentials['accountId'],status),'x')[1][0][0]
                    if count == 0:
                        ins_id = self.db.put("Insert into thingType set thingTypeName= '%s' , thingTypeArn='%s' , thingTypeDescription= '%s', status = '%s', awsAccountId='%s' " %(thing['thingTypeName'],thing['thingTypeArn'],self.db.escape(thing['thingTypeProperties']), status, str(credentials['accountId'])))
                        log.info("ThingType added to database on ID: %s" % (str(ins_id)))
                    else:
                        log.info("ThingType already exist")
                if 'nextToken' in response.keys():
                    self.get_thing_types(credentials,response['nextToken'])
            self.db.releaseConnection()
        except Exception as ex:
            self.db.releaseConnection()
            log.exception('EXCEPTION: Downloading ThingType Failed: {}'.format(ex))
            pass
    
    def list_thing_groups(self,login, credentials,nextToken=''):
        log.info("Starting thingGroups download thread for account: %s" % credentials['accountName'])
        self.db.createConnection()
        try:
            client , _ = create_obj(credentials['regionAWS'],credentials['accessKey'],credentials['secretKey'])
            if nextToken=='':
                response=client.list_thing_groups(maxResults=10)
            else:
                response=client.list_thing_groups(maxResults=10, nextToken=nextToken)
            
            if len(response['thingGroups']) > 0:
                for thing in response['thingGroups']:
                    count = self.db.get("Select count(*) from thingGroup where thingGroupName = '%s' and awsAccountId= '%s' and status='active'" %(thing['groupName'], credentials['accountId']),'x')[1][0][0]
                    if count == 0:
                        ins_id = self.db.put("Insert into thingGroup set thingGroupName= '%s' , thingGroupArn='%s' , status= 'active' , awsAccountId='%s'" %(thing['groupName'],thing['groupArn'], credentials['accountId']))
                        log.info("ThingGroup added to database on ID: %s" % (str(ins_id)))
                    else:
                        log.info("ThingGroup already exist")
                if 'nextToken' in response.keys():
                    self.list_thing_groups(credentials,response['nextToken'])
            self.db.releaseConnection()
        except Exception as ex:
            self.db.releaseConnection()
            log.exception('EXCEPTION: Downloading ThingGroup Failed: {}'.format(ex))
            pass

    def download(self):
        self.db.createConnection()
        sql= "Select accountId, accountName, regionAWS, accessKey, secretKey from awsCredentials where status='active'"
        data= self.db.get(sql,'j')[1]
        if len(data) > 0:
            for account in data:
                login=create_obj(account['regionAWS'],account['accessKey'],account['secretKey'])
                self.get_thing_types(login,account)
                self.get_things(login,account)
                self.list_thing_groups(login,account)


    def run_nonblock(self):
        log.info("Starting with count")
        self._thread.start()


    def run(self):
        t_ctr=600
        log.info("Starting Threaded Process")
        while(True):

            # This should only happen if ^C is hit.
            if self._thread_stop.is_set():
                log.warning('Exiting backend data refresh thread. ')
                break
            if t_ctr>=600:
                t_ctr=0
                log.info("Starting backend data refresh thread" )
                self.download()
                self.counting+=1
                log.info("Done backend data refresh thread")
            else:
                t_ctr=t_ctr+1
            time.sleep(1)


    def stop(self):
        self._thread_stop.set()

# if __name__ == '__main__':
#     statsUploader = RefreshDB()
#     #statsUploader.run()

