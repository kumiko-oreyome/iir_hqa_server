docker pull samejack/docker-elasticsearch-kibana:latest
docker run -p 5601:5601 -p 9200:9200 -it samejack/elasticsearch-kibana:latest

sysctl -w vm.max_map_count=262144 #不設定可能會報錯
HOST=
PORT=9200
CMDB_INDEX_NAME=
CMDB_LIB_DOC_NAME=
curl -X PUT http://${HOST}:${PORT}/${CMDB_INDEX_NAME}
curl -X PUT "http://${HOST}:${PORT}/${CMDB_INDEX_NAME}/${CMDB_LIB_DOC_NAME}/_mapping" -H 'Content-Type:application/json' -d '{
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
			"tags":{"type":"text", "analyzer": "ik_smart","search_analyzer": "ik_smart"},
			"paragraphs":{"type":"text", "analyzer": "ik_smart","search_analyzer": "ik_smart"}
        }
}'


