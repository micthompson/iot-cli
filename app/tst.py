from mySQL import Database

db = Database()

def validate_account(account_id):
    data_cred=db.dbOperation("awsCredentials","select",fields=['accountName', 'regionAWS', 'accessKey', 'secretKey'],data={'accountId':str(account_id) ,'status' :'active'},format="j")
    print(len(data_cred[1]))
    db.releaseConnection()
    if len(data_cred[1])>0:
        return (data_cred[1])
    else:
        return ([])


print(validate_account(2))