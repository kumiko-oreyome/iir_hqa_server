HOST=
PORT=9200
CMDB_INDEX_NAME=
CMDB_LIB_DOC_NAME=
curl -X PUT http://${HOST}:${PORT}/${CMDB_INDEX_NAME}
sysctl -w vm.max_map_count=262144 #不設定可能會報錯
curl -X PUT "http://${HOST}:${PORT}/${CMDB_INDEX_NAME}/${CMDB_LIB_DOC_NAME}/_mapping" -H 'Content-Type:application/json' -d '{
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_max_word"
            },
			"tags":{"type":"text", "analyzer": "ik_smart","search_analyzer": "ik_smart"},
			"paragraphs":{"type":"text", "analyzer": "ik_max_word","search_analyzer": "ik_max_word"}
        }
}'


