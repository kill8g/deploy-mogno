# deploy-mongo

部署一套完整的mongo分片服务器
Deploy a complete set of mongo shard servers
- 3 mongos
- 3 shardsvr, One master and two slaves
- 1 configsvr, One master and two slaves

sehema.py 
  > configsvr_define configsvr : Linux server address configuration information
  > shardsvr_define : 3 groups of shardsvr, each group is one master and two slaves
  > mongos_define : Deploy 3 mongos processes
  > servers linux : linux server ip, port, pwd
  > root : root path

Example:
start:
python deploy.py --start --project test
close:
python deploy.py --close --project test

test mongo:
```shell
mongo --host 192.168.0.100 --port 3201
```
```js
sh.enableSharding("testrs")
sh.shardCollection("testrs.datas", {shard_key: 1})
sh.enableBalancing("testrs.datas")
sh.startBalancer()
use config
db.settings.save( { _id:"chunksize", value: 1 } )
use testrs
for (var i = 10000; i < 50000; i++) {
    db.datas.insertOne({shard_key : Math.random().toString(36).substring(2, 15), value : "qwertyuiopasdfghjklzxcvbnm", id : i})
}
db.datas.getShardDistribution()
```
