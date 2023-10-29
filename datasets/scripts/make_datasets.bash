echo "=> Generating sanitized translations"
python sanitize.py context_curated context_curated_sanitized

echo "=> Synthesizing spider dataset"
echo "==> In english"
python synthesize.py spider spider --schema-translation english -s en -q en --with-db
echo "==> With english schema"
python synthesize.py spider pol_spider_en --schema-translation english --with-db
echo "==> With polish schema"
python synthesize.py spider pol_spider_pl --schema-translation context_curated_sanitized --with-db
echo "==> Joining pol_spider"
python join.py pol_spider pol_spider_en pol_spider_pl
echo "==> Joining pol_spider_mix"
python join.py pol_spider_mix pol_spider spider

echo "=> Synthesizing spider-syn dataset"
echo "==> In english"
python synthesize.py spider-syn spidersyn --schema-translation english -s en -q en --with-db
echo "==> With english schema"
python synthesize.py spider-syn pol_spidersyn_en --schema-translation english --with-db
echo "==> With polish schema"
python synthesize.py spider-syn pol_spidersyn_pl --schema-translation context_curated_sanitized --with-db
echo "==> Joining pol_spidersyn"
python join.py pol_spidersyn pol_spidersyn_en pol_spidersyn_pl
echo "==> Joining pol_spidersyn_mix"
python join.py pol_spidersyn_mix pol_spidersyn spidersyn

echo "=> Synthesizing spider-dk dataset"
echo "==> In english"
python synthesize.py spider-dk spiderdk --schema-translation english -s en -q en --with-db
echo "==> With english schema"
python synthesize.py spider-dk pol_spiderdk_en --schema-translation english --with-db
echo "==> With polish schema"
python synthesize.py spider-dk pol_spiderdk_pl --schema-translation context_curated_sanitized --with-db
echo "==> Joining pol_spiderdk"
python join.py pol_spiderdk pol_spiderdk_en pol_spiderdk_pl
echo "==> Joining pol_spiderdk_mix"
python join.py pol_spiderdk_mix pol_spiderdk spiderdk

echo "=> Synthesizing cosql-wc dataset"
echo "==> In english"
python synthesize.py cosql-wc cosqlwc --schema-translation english -s en -q en --with-db
echo "==> With english schema"
python synthesize.py cosql-wc pol_cosqlwc_en --schema-translation english --with-db
echo "==> With polish schema"
python synthesize.py cosql-wc pol_cosqlwc_pl --schema-translation context_curated_sanitized --with-db
echo "==> Joining pol_cosqlwc"
python join.py pol_cosqlwc pol_cosqlwc_en pol_cosqlwc_pl
echo "==> Joining pol_cosqlwc_mix"
python join.py pol_cosqlwc_mix pol_cosqlwc cosqlwc

echo "=> Synthesizing sparc-wc dataset"
echo "==> In english"
python synthesize.py sparc-wc sparcwc --schema-translation english -s en -q en --with-db
echo "==> With english schema"
python synthesize.py sparc-wc pol_sparcwc_en --schema-translation english --with-db
echo "==> With polish schema"
python synthesize.py sparc-wc pol_sparcwc_pl --schema-translation context_curated_sanitized --with-db
echo "==> Joining pol_sparcwc"
python join.py pol_sparcwc pol_sparcwc_en pol_sparcwc_pl
echo "==> Joining pol_sparcwc_mix"
python join.py pol_sparcwc_mix pol_sparcwc sparcwc

echo "=> Joining ultimate"
python join.py ultimate spider spidersyn spiderdk cosqlwc sparcwc
echo "=> Joining pol_ultimate"
python join.py pol_ultimate pol_spider pol_spidersyn pol_spiderdk pol_cosqlwc pol_sparcwc
echo "=> Joining pol_ultimate_mix"
python join.py pol_ultimate_mix pol_spider_mix pol_spidersyn_mix pol_spiderdk_mix pol_cosqlwc_mix pol_sparcwc_mix
echo "=> Joining pol_ultimate_en"
python join.py pol_ultimate_en pol_spider_en pol_spidersyn_en pol_spiderdk_en pol_cosqlwc_en pol_sparcwc_en
echo "=> Joining pol_ultimate_pl"
python join.py pol_ultimate_pl pol_spider_pl pol_spidersyn_pl pol_spiderdk_pl pol_cosqlwc_pl pol_sparcwc_pl
