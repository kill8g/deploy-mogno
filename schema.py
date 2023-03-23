configsvr_define = {
	# Deploy 1 group of config servers with 1 primary and 2 secondaries.
	"type" : "configsvr", 
	"addrs" : ("192.168.0.100:3001", "192.168.0.101:3002","192.168.0.101:3003"), 
}

shardsvr_define = {
	# The deployment consists of three sets of shardsvr replica sets, 
	# with each set containing one primary and two secondary servers.
	"type" : "shardsvr", 
	"groups" : (
		("192.168.0.100:3101", "192.168.0.100:3102","192.168.0.101:3103"), 
		("192.168.0.100:3104", "192.168.0.100:3105","192.168.0.101:3106"), 
		("192.168.0.100:3107", "192.168.0.100:3108","192.168.0.101:3109"), 
	)
}

mongos_define =	{
	# Deploy 3 mongos.
	"type" : "mongos", 
	"addrs" : ("192.168.0.100:3201", "192.168.0.101:3202","192.168.0.100:3203"), 
}


servers = {
	"192.168.0.100" : {
		"port" : 22, 
		"user" : "root", 
		"password" : "xxxx", 
	}, 
	"192.168.0.101" : {
		"port" : 22, 
		"user" : "root", 
		"password" : "xxxx", 
	}, 	
}

project = "test"

root = "/data/mongoreplset/"
