from flask import Flask, request, jsonify, json

from pymongo import MongoClient
import netmiko

app = Flask(__name__)


def mongoconnect():
    mongo_client = MongoClient('mongodb://mongo-db-data:27017')
    # mongo_client = MongoClient('mongodb://127.0.0.1:27017')
    db = mongo_client.ip
    col = db['interfaceStatus']
    t = col.count_documents({})
    print(t)


def testNetworkConnection(host):
    try:
        connection = netmiko.ConnectHandler(ip=host, device_type="cisco_ios", username="DevOpsNMS", password="ti4da0TA")
        if connection:
            print("Connection Successful")
            return True
    except UnicodeError:
        print(host + " Problem timeout")
        return False
    except netmiko.ReadTimeout:
        return False
    except netmiko.NetmikoBaseException:
        return False
    except netmiko.NetmikoTimeoutException:
        return False


def testDocExists(host, data):
    mongo_client = MongoClient('mongodb://mongo-db-data:27017')
    # mongo_client = MongoClient()  # 'mongodb://127.0.0.1:27017'
    db = mongo_client.ip
    col = db['interfaceStatus']
    result = col.count_documents({"nodeIP": host})
    if result > 0:
        UUPdate(host, data)
    else:
        ADDOne(host, data)


def UUPdate(host, data):
    mongo_client = MongoClient('mongodb://mongo-db-data:27017')
    # mongo_client = MongoClient('mongodb://127.0.0.1:27017')
    db = mongo_client.ip
    col = db['interfaceStatus']
    myquery = {"nodeIP": host}
    newValues = {"$set": data}
    col.update_one(myquery, newValues)
    print(host, " Updated")


def ADDOne(host, data):
    mongo_client = MongoClient('mongodb://mongo-db-data:27017')
    # mongo_client = MongoClient('mongodb://127.0.0.1:27017')
    db = mongo_client.ip
    col = db['interfaceStatus']
    # col.insertOne({"mgmtIPaddress" : host}, {data})
    col.insert_one({"nodeIP": host}, data)
    print(host, " Added to db")
    UUPdate(host, data)


def XRcode(host):
    connection = netmiko.ConnectHandler(ip=host, device_type="cisco_ios", username="DevOpsNMS", password="ti4da0TA")

    # 1. hostname  : this code extract the hostname in XR IOS
    a = connection.send_command("terminal length 0")
    a = connection.send_command("terminal pager 0")
    a = connection.send_command("show configuration running  | include hostname", read_timeout=300)
    aa = a.splitlines()

    for i in range(0, len(aa)):
        if "hostname" in aa[i]:
            aaa = aa[i].split()
            hostn = aaa[1]

    # 2. IOS :  this code extracts the IOS and version
    b = connection.send_command("terminal length 0")
    b = connection.send_command("terminal pager 0")
    b = connection.send_command("show version | include Software, Version", read_timeout=300)
    bb = b.splitlines()
    for i in range(0, len(bb)):
        if "IOS" in bb[i]:
            bbb = bb[i].split()
            cIOS = bbb[2]
            IOSversion = bbb[5]

    # 3. Updates the hostname, IOS and version in the mongo db
    hinfo = {"hostName": hostn, "ios": cIOS, "iosVersion": IOSversion}
    testDocExists(host, hinfo)

    # 4. Platform
    c = connection.send_command("terminal length 0")
    c = connection.send_command("terminal pager 0")
    c = connection.send_command("show platform", read_timeout=300)
    cc = c.splitlines()
    # df = pd.DataFrame(cc)

    # for x in cc.iloc[:, 3]:
    #     if x == 'ASR-9904' and x == 'ASR-9010' and x == 'ASR-9006' and x == 'ASR-9001' and x == 'ASR-9903' and x == 'ASR-9906':
    #         pinfo = {"platform": [cc[3:len(cc)]]}
    #     else:
    #         #print("node type not found")
    #         break

    pinfo = {"platform": [cc[3:len(cc)]]}
    testDocExists(host, pinfo)

    # 5. Extract all interfaces physical and logical from device
    d = connection.send_command("terminal length 0")
    d = connection.send_command("terminal pager 0")
    d = connection.send_command("show inter descr | inclu up | i Te", read_timeout=300)
    dd = d.splitlines()
    dd = dd[4:len(dd)]
    upList = []
    for i in dd:
        if "Te" in i:
            upList.append(i)

    uinfo = {"tenGEifUp": [upList]}
    testDocExists(host, uinfo)

    # 6. Interfaces Down
    e = connection.send_command("terminal length 0")
    e = connection.send_command("terminal pager 0")
    e = connection.send_command("show interf descr | i down | i Te", read_timeout=300)
    ee = e.splitlines()
    ee = ee[4:len(ee)]
    downList = []
    for i in ee:
        if "Te" in i:
            downList.append(i)

    dinfo = {"tenGEifDown": [downList]}
    testDocExists(host, dinfo)


def XEcode(host):
    connection = netmiko.ConnectHandler(ip=host, device_type="cisco_ios", username="DevOpsNMS", password="ti4da0TA")

    # 1. hostname  : this code extract the hostname in XR IOS
    a = connection.send_command("terminal length 0")
    a = connection.send_command("show configuration  | include hostname", read_timeout=200)
    aa = a.splitlines()

    for i in range(0, len(aa)):
        if "hostname" in aa[i]:
            aaa = aa[i].split()
            hostn = aaa[1]

    # 2. IOS :  this code extracts the IOS and version
    b = connection.send_command("terminal length 0")
    b = connection.send_command("show version | include Software, Version", read_timeout=100)
    bb = b.splitlines()
    for i in range(0, len(bb)):
        if "IOS" in bb[i]:
            bbb = bb[i].split()
            cIOS = bbb[2]
            IOSversion = bbb[5]

    # 3. Updates the hostname, IOS and version in the mongo db
    hinfo = {"hostName": hostn, "ios": cIOS, "iosVersion": IOSversion}
    testDocExists(host, hinfo)

    # 4. Platform
    c = connection.send_command("terminal length 0")
    c = connection.send_command("show platform", read_timeout=100)
    cc = c.splitlines()
    # df = pd.DataFrame(cc)
    # for x in cc.iloc[:, 2]:
    #     if x == 'ASR-9904' and x == 'ASR-9010' and x == 'ASR-9006' and x == 'ASR-9001' and x == 'ASR-9903' and x == 'ASR-9906':
    #         pinfo = {"platform": [cc[3:len(cc)]]}
    #     else:
    #         break
    # print("node type not found")
    pinfo = {"platform": [cc[3:len(cc)]]}
    testDocExists(host, pinfo)

    # 5. Extract all interfaces physical and logical from device
    d = connection.send_command("terminal length 0")
    d = connection.send_command("show inter descr | inclu up | i Te", read_timeout=200)
    dd = d.splitlines()
    dd = dd[4:len(dd)]
    upList = []
    for i in dd:
        if "Te" in i:
            upList.append(i)

    uinfo = {"tenGEifUp": [upList]}
    testDocExists(host, uinfo)

    # 6. Interfaces Down
    e = connection.send_command("terminal length 0")
    e = connection.send_command("show interf descr | i down | i Te", read_timeout=200)
    ee = e.splitlines()
    ee = ee[4:len(ee)]
    downList = []
    for i in ee:
        if "Te" in i:
            downList.append(i)

    dinfo = {"tenGEifDown": [downList]}
    testDocExists(host, dinfo)


# This function communicates with the network device using the IP address, retreives the ios to determine if it is XE or XR
# Then invoke XE or XR functions
def start(ipList):
    for host in ipList:
        print("Start with ", host)
        if testNetworkConnection(host):
            connection = netmiko.ConnectHandler(ip=host, device_type="cisco_ios", username="DevOpsNMS",
                                                password="ti4da0TA")
            a = connection.send_command("terminal length 0")
            a = connection.send_command("show version | include Software, Version", read_timeout=150)

            # print (a)

            if "XE" in a:
                print("This is XE")
                XEcode(host)
            elif "XR" in a:
                print("This is XR")
                XRcode(host)
            else:
                print("this is nothing")

        else:
            print(host, " did not connect")
            continue
    print("End start")


# This function retrieves the IP address, Province and Site Name of the device and updates the networkStatus DB
# It then compiles a list of the IP addresses and passes it to start()

# @app.route(('/apestatus'), methods=['GET'])
# @app.route(('/apeinfo'), methods=['POST'])
def getnetworkservice():
    # ipList = []
    mongo_client = MongoClient('mongodb://mongo-db-data:27017')
    # mongo_client = MongoClient()  # 'mongodb://127.0.0.1:27017'
    db = mongo_client.ip
    col2 = db["service-statistics"]
    print(col2.count_documents({}))
    nodeIP9k = []

    for x in col2.find({}, {"_id": 0, "nodeIP": 1, "siteName": 1, "province": 1, "nodeType": 1}):
        host = x["nodeIP"]
        province = x["province"]
        siteN = x["siteName"]
        nodeType = x["nodeType"]

        if ('ASR-9900' in x["nodeType"]) or ('ASR-9010' in x["nodeType"]) or ('ASR-9006' in x["nodeType"]) or (
                'ASR-9903' in x["nodeType"]):
            Ddata = {"province": province, "siteName": siteN, "nodeTYpe": nodeType}
            # testDocExists(host, Ddata)
            nodeIP9k.append(host)
        # ipList.append(host)
        # a={'data': ipList}

    start(nodeIP9k)
    print("Completed updating database")
    return ({'nodeIP': nodeIP9k})
    # return a


# initiates the program - This is the start of the program
# start(getnetworkservice())


# getIPfromQueue()

@app.route(('/serviceinformationget'), methods=['GET'])
def justget():
    x = 'Got'
    return x


@app.route(('/serviceinformation'), methods=['POST'])
def liveservice():
    item = request.get_json()
    ip_input = item['nodeIP']
    nodeiplist = [ip_input]
    mongo_client = MongoClient('mongodb://mongo-db-data:27017')
    # mongo_client = MongoClient()  # 'mongodb://127.0.0.1:27017'
    db = mongo_client.ip
    col1 = db['interfaceStatus']
    col2 = db['service-statistics']
    for x in col2.find({}, {'nodeIP': 1, '_id': 0}):
        nodeip = x['nodeIP']
        if ip_input == nodeip:
            start(nodeiplist)

    myquery = {'nodeIP': ip_input}
    findall = {'_id': 0, 'nodeIP': 1, 'ios': 1, 'siteName': 1, 'province': 1, 'hostName': 1, 'iosVersion': 1,
               'platform': 1, 'tenGEifUp': 1, 'tenGEifDown': 1}
    


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='0.0.0.0')
