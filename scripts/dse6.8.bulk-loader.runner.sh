dsbulk load --schema.graph who_likes_whom --schema.vertex person \
-url /home/ryan/projects/dse-graph-supernode-benchmarking/tmp/data/vertices.csv \
-delim '|' \
--schema.allowMissingFields true

dsbulk load -g who_likes_whom -e likes \
-url /home/ryan/projects/dse-graph-supernode-benchmarking/tmp/data/vertices.csv \
-m '0=person_id, 1=book_id' \
-delim '|' \
--schema.allowMissingFields true
