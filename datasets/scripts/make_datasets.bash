echo "=> Generating sanitized translations"
python sanitize.py context_curated context_curated_sanitized

echo "=> Synthesizing spider dataset"
echo "=> With english schema"
python synthesize.py spider pol_spider_en --schema-translation english --with-db
echo "=> With polish schema"
python synthesize.py spider pol_spider_pl --schema-translation context_curated_sanitized --with-db

echo "Synthesizing spider-syn dataset"
echo "=> With english schema"
python synthesize.py spider-syn pol_spidersyn_en --schema-translation english --with-db
echo "=> With polish schema"
python synthesize.py spider-syn pol_spidersyn_pl --schema-translation context_curated_sanitized --with-db

echo "Synthesizing spider-dk dataset"
echo "=> With english schema"
python synthesize.py spider-dk pol_spiderdk_en --schema-translation english --with-db
echo "=> With polish schema"
python synthesize.py spider-dk pol_spiderdk_pl --schema-translation context_curated_sanitized --with-db

echo "Synthesizing cosql-wc dataset"
echo "=> With english schema"
python synthesize.py cosql-wc pol_cosqlwc_en --schema-translation english --with-db
echo "=> With polish schema"
python synthesize.py cosql-wc pol_cosqlwc_pl --schema-translation context_curated_sanitized --with-db

echo "Synthesizing sparc-wc dataset"
echo "=> With english schema"
python synthesize.py sparc-wc pol_sparcwc_en --schema-translation english --with-db
echo "=> With polish schema"
python synthesize.py sparc-wc pol_sparcwc_pl --schema-translation context_curated_sanitized --with-db

echo "=> Joining pol_spider"
python join.py pol_spider pol_spider_en pol_spider_pl

echo "=> Joining pol_spidersyn"
python join.py pol_spidersyn pol_spidersyn_en pol_spidersyn_pl

echo "=> Joining pol_spiderdk"
python join.py pol_spiderdk pol_spiderdk_en pol_spiderdk_pl

echo "=> Joining pol_cosqlwc"
python join.py pol_cosqlwc pol_cosqlwc_en pol_cosqlwc_pl

echo "=> Joining pol_sparcwc"
python join.py pol_sparcwc pol_sparcwc_en pol_sparcwc_pl

echo "=> Joining pol_ultimate"
python join.py pol_ultimate pol_spider pol_spidersyn pol_spiderdk pol_cosqlwc pol_sparcwc
