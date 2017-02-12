#!/usr/bin/env fish

# Very hacky.

echo "window.f = {'normal': {}, 'bold': {}};" > src/load.js

for file in ../renaissance/fonts/*
	echo -n "window.f['" >> src/load.js
	echo $file | grep bold > /dev/null; and echo -n "bold" >> src/load.js; or echo -n "normal" >> src/load.js
	echo -n "'][" >> src/load.js
	echo -n $file | tr -d -C '0123456789' | sed 's/^0*//' | tr -d '\n' >> src/load.js
	echo -n "] = new Font(new Loader(\"" >> src/load.js
	base64 $file | tr -d '\n' >> src/load.js
	echo "\"));" >> src/load.js
end

babili src/font.js src/load.js src/page.js --presets=babili --no-comments > combined.min.js
