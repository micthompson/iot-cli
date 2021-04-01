import pymysql
import configparser
from time import sleep

class Database(object):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.databaseServerIP = config['MYSQL']['host']
        self.databasePort = config['MYSQL']['port']
        self.databaseUserName = config['MYSQL']['user']
        self.databaseUserPassword = config['MYSQL']['password']
        self.newDatabaseName = config['MYSQL']['database']
        self.cusrorType = pymysql.cursors.SSCursor
        self.cusrorTypeJ=pymysql.cursors.DictCursor
        #self.init_db()
        self.dbObject=None
        self.conn=None
        self.dbObjectJ=None
        self.connJ=None
        self.created=False
        self.c_count=0
        while self.c_count<500 and self.created == False:
            try:
                self.createConnection()
                self.created=True
                print("DB Connected")
            except:
                print("Reconnecting")
                self.c_count+=1
                sleep(5)


    def init_db(self):
        db = pymysql.connect(host=self.databaseServerIP,port=int(self.databasePort), user=self.databaseUserName, password=self.databaseUserPassword,cursorclass=self.cusrorType,database=self.newDatabaseName)
        cursor=db.cursor()
        print("DB connected")
        print("Attempting to create Tables")
        with open("./default.sql") as dxx:
            data = dxx.readlines()
            for dd in range(2,len(data)):
                sql=data[dd]
                #print(sql)
                try:
                    cursor.execute(sql.replace(';','').replace('dbnamehere',self.newDatabaseName))
                except Exception as sss:
                    print(str(sss))
        print("Table Creation done")
        dxx.close()
        cursor.close()
        db.close()


    def createConnection(self):
        self.dbObject = pymysql.connect(host=self.databaseServerIP,port=int(self.databasePort), user=self.databaseUserName, password=self.databaseUserPassword,cursorclass=self.cusrorType,database=self.newDatabaseName)
        self.conn=self.dbObject.cursor()

        self.dbObjectJ = pymysql.connect(host=self.databaseServerIP,port=int(self.databasePort), user=self.databaseUserName, password=self.databaseUserPassword,cursorclass=self.cusrorTypeJ,database=self.newDatabaseName)
        self.connJ=self.dbObjectJ.cursor()

    def releaseConnection(self):
        try:
            self.conn.close()
            self.connJ.close()
            self.dbObject.close()
            self.dbObjectJ.close()
        except Exception as sss:
            print(str(sss))
        

    def get(self, sql,type='x'):
        #print(sql)
        try:
            if type == 'j':
                self.connJ.execute(sql)
                return(200,self.connJ.fetchall())
            else:
                self.conn.execute(sql)
                return(200,self.conn.fetchall())
            
        except Exception as aa:
            return (401,str(aa))
    
    def put(self, sql):
        #print(sql)
        try:
            self.conn.execute(sql)
            self.dbObject.commit()
            return(200,self.get("SELECT LAST_INSERT_ID()")[1][0][0])
            
        except Exception as ass:
            print(str(ass))
            self.releaseConnection()
            return (401,str(ass))
    
    def update(self,sql):
        #print(sql)
        try:
            self.conn.execute(sql)
            self.dbObject.commit()
            return(200,'OK')
        except Exception as aa:
            return (401,str(aa))

    def query(self,data={},columns=[],delimeter=' and ',type='general'):
        t=[]
        for x in data.keys():
            if x !='limit' and x in columns:
                if type == 'general':
                    t.append(str(x)+" = '"+pymysql.escape_string(data[x])+"'")
                else:
                    t.append(str(x)+" like '%"+pymysql.escape_string(data[x])+"%'")
        strx=delimeter.join(t)
        try:
            strx=strx+" Limit "+str(data['limit'])
        except:
            None
        print(strx)
        return strx

    def queryColumns(self,data=[]):
        return ' , '.join(data)

    def checkRequired(self,available=[],dbName=''):
        required , _ = self.columnDef(dbName)
        for c in required:
            if c not in available:
                return c
        return 'OK'

    def columnDef(self,tableName):
        if tableName =='serviceContainers':
            columns = ['containerId','containerName','containerIp','status','description']
            required = ['containerName','containerIp']

        elif tableName =='awsCredentials':
            columns=['accountId','accountName','regionAWS','accessKey','secretKey','status','containerId','description']
            required=['accountName','regionAWS','accessKey','secretKey','status','containerId']

        elif tableName =='serviceRequest':
            columns=['jobId','uid','task','operation','attrData','awsAccountId','scheduledAt','processedAt','processStatus','retryCount','processingTime','response','active']
            required=['task','operation','attrData','awsAccountId','scheduledAt','processedAt']

        elif tableName =='thingGroup':
            columns=['thingGroupId','thingGroupName','thingGroupDescription','parentGroupId','tags','thingGroupUID','thingGroupARN','awsAccountId','additionalData','version','status']
            required=['thingGroupName','awsAccountId']

        elif tableName =='things':
            columns=['thingId','thingName','thingDescription','thingTypeId','thingUID','awsAccountId','thingGroupId','version','status']
            required=['thingName''thingUID','awsAccountId']

        elif tableName =='thingType':
            columns=['thingTypeId','thingTypeName','thingTypeDescription','additionalData','awsAccountId','thingGroupId',"thingTypeArn",'status']
            required=['thingTypeId','thingTypeName','awsAccountId']

        return required,columns

    def dbOperation(self,table_name,operation='select',data={},fields=[],format='x'):
        self.releaseConnection()
        self.createConnection()
        _,columns=self.columnDef(table_name)

        if data == None:
            data={}
        id_col=columns[0]
        if operation.lower() == 'select' or operation.lower() == 'get':
            
            if len(data)==0:
                if len(fields) == 0:
                    return self.get("Select * from " + str(table_name) + "",'j')
                else:
                    return self.get("Select " + self.queryColumns(fields) + " from " + str(table_name) + "",'j')

            else:
                if len(fields) == 0:
                    return self.get("Select * from " + str(table_name) + " where " + self.query(data,columns),'j')
                else:
                    return self.get("Select " + self.queryColumns(fields) + " from " + str(table_name) + " where " + self.query(data,columns),'j')

        elif operation.lower() == 'insert' or operation.lower() == 'post':
            try:
                del data[id_col]
            except:
                None
            return self.put("Insert into " + str(table_name) + " set " + self.query(data,columns,' , '))
        
        elif operation.lower() == 'update' or operation.lower() == 'put':
            idx=data[id_col]
            del data[id_col]
            return self.update("Update " + str(table_name) + " set " + self.query(data,columns,' , ') + " Where " + str(id_col) + " ='" + str(idx) +"'")
        
        elif operation.lower() == 'delete' or operation.lower() == 'delete':
            return self.update("Delete from " + str(table_name) + " where " + str(id_col) + " = " + str(data[id_col]))

        elif operation.lower() == 'count':
            return self.get("Select count(*) from " + str(table_name) + "")[1][0][0]

    def escape(self,data):
        return pymysql.escape_string(str(data))

    
# if __name__ == '__main__':
#     database = Database()
#     print(database.get("Select * from serviceContainers"))
    
    