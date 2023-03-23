import schema
import paramiko
import json
import argparse

configsvr_define = schema.configsvr_define
shardsvr_define = schema.shardsvr_define
mongos_define = schema.mongos_define

servers = schema.servers
root = schema.root

# init ssh
ssh = paramiko.SSHClient()
policy = paramiko.AutoAddPolicy()
ssh.set_missing_host_key_policy(policy)

def exec_command(hostname, port, username, password, cmd):
    print(hostname, cmd)
    ssh.connect(
        hostname = hostname,
        port = port,
        username = username,
        password = password,
    )
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())
    print(stderr.read().decode())

def _dumps_(data):
    for k, v in data.items():
        pass

def init_configsvr(addrs):
    conf = {
        "_id" : "%s-configsvr" % (project), 
        "configsvr" : True, 
        "members" : [], 
    }
    index = 0
    for addr in addrs:
        conf["members"].append({"_id" : index, "host" : addr})
        index = index + 1

    s = json.dumps(conf).replace("\"", "'")
    addr = addrs[0]
    host, port = addr.split(':')
    server = servers[host]
    assert(server)
    cmd = "cd %s && mongo --port %s --eval \"rs.initiate(%s)\"" % (root, port, s)
    exec_command(host, server["port"], server["user"], server["password"], cmd)

def init_shardsvr(addrs, group):
    conf = {
        "_id" : "%s-shardsvr-%d" % (project, group), 
        "members" : [], 
    }
    index = 0
    for addr in addrs:
        conf["members"].append({"_id" : index, "host" : addr})
        index = index + 1
    s = json.dumps(conf).replace("\"", "'")
    addr = addrs[0]
    host, port = addr.split(':')
    server = servers[host]
    assert(server)
    cmd = "cd %s && mongo --port %s --eval \"rs.initiate(%s)\"" % (root, port, s)
    exec_command(host, server["port"], server["user"], server["password"], cmd)

def init_mongos(addrs, shardsvrs):
    group = 1
    for addr in addrs:
        host, port = addr.split(':')
        replSet = "%s-shardsvr-%d" % (project, group)
        array = shardsvrs[group - 1]
        cmd = "cd %s && mongo --port %s --eval \"sh.addShard('%s/%s')\"" % (root, port, replSet, ",".join(array))
        server = servers[host]
        assert(server)
        exec_command(host, server["port"], server["user"], server["password"], cmd)
        group = group + 1

def start_configsvr(hostname, sshport, username, password, index, mongoport):
    dbpath = "%s-configsvr-%d" % (project, index)
    replSet = "%s-configsvr" % (project)
    logpath = "%s-configsvr-%d.log" % (project, index)
    checkdir = "cd %s && mkdir -p %s " % (root, dbpath)
    cmd = "%s && mongod --configsvr --replSet %s --bind_ip 0.0.0.0 --port %d --dbpath %s --logpath %s --fork" % \
            (checkdir, replSet, mongoport, dbpath, logpath)
    exec_command(hostname, sshport, username, password, cmd)

def start_all_configsvr(addrs):
    index = 1
    for addr in addrs:
        host, port = addr.split(':')
        server = servers[host]
        assert(server)
        start_configsvr(host, server["port"], server["user"], server["password"], index, int(port))
        index = index + 1

    init_configsvr(addrs)

def start_shardsvr(hostname, sshport, username, password, group, index, mongoport):
    dbpath = "%s-shardsvr-%d-rs-%d" % (project, group, index)
    replSet = "%s-shardsvr-%d" % (project, group)
    logpath = "%s-shardsvr-%d-rs-%d.log" % (project, group, index)
    checkdir = "cd %s && mkdir -p %s " % (root, dbpath)
    cmd = "%s && mongod --shardsvr --replSet %s --bind_ip 0.0.0.0 --port %d --dbpath %s --logpath %s --fork" % \
            (checkdir, replSet, mongoport, dbpath, logpath)
    exec_command(hostname, sshport, username, password, cmd)

def start_all_shardsvr(groups):
    group = 1
    for addrs in groups:
        index = 1
        for addr in addrs:
            host, port = addr.split(':')
            server = servers[host]
            assert(server)
            start_shardsvr(host, server["port"], server["user"], server["password"], group, index, int(port))
            index = index + 1
        init_shardsvr(addrs, group)
        group = group + 1

def start_mongos(hostname, sshport, username, password, index, mongoport, configsvrs):
    replSet = "%s-configsvr" % (project)
    logpath = "%s-mongos-%d.log" % (project, index)
    cddir = "cd %s" % (root)
    cmd = "%s && mongos --configdb %s/%s --logpath .%s --logappend --verbose --fork --port %d" % \
            (cddir, replSet, ",".join(configsvrs), logpath, mongoport)
    exec_command(hostname, sshport, username, password, cmd)

def start_all_mongos(addrs, groups, configsvrs):
    index = 1
    for addr in addrs:
        host, port = addr.split(':')
        server = servers[host]
        assert(server)
        start_mongos(host, server["port"], server["user"], server["password"], index, int(port), configsvrs)
        index = index + 1

    init_mongos(addrs, groups)

def start_all():
    start_all_configsvr(configsvr_define["addrs"])
    start_all_shardsvr(shardsvr_define["groups"])
    start_all_mongos(mongos_define["addrs"], shardsvr_define["groups"], configsvr_define["addrs"])

def shutdown(addr):
    host, port = addr.split(':')
    server = servers[host]
    assert(server)
    cmd = "mongo admin --port %s --host 127.0.0.1 --eval \"%s\"" % (port, "db.shutdownServer()")
    exec_command(host, server["port"], server["user"], server["password"], cmd)

def close_all():
    for addr in mongos_define["addrs"]:
        shutdown(addr)
    for addrs in shardsvr_define["groups"]:
        for addr in addrs:
            shutdown(addr)
    for addr in configsvr_define["addrs"]:
        shutdown(addr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'deploy of argparse')
    parser.add_argument('--start', action = "store_true")
    parser.add_argument('--close', action = "store_true")
    parser.add_argument('--project', type = str, required = True)
    args = parser.parse_args()
    assert(args.project)
    project = args.project
    if args.start:
        start_all()
    if args.close:
        close_all()
