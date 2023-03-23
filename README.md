# deploy-mongo

部署一套完整的mongo分片服务器
包含
- 3个mongos
- 3组shardsvr, 一主二从
- 一组configsvr, 一主二从

sehema.py 配置信息
  > configsvr_define configsvr 部署地址
  > shardsvr_define 部署3组shardsvr, 每一组包含一主二从
  > mongos_define 部署3个mongos进程
  > servers linux 服务器的ip, user, pwd
  > root 项目根目录

示例:
启动分片服务器
python deploy.py --start --project test
关闭分片服务器
python deploy.py --close --project test

测试mongo:
```shell
mongo --host 192.168.0.155 --port 3201
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
