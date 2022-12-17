#!/usr/bin/env bash

set -euo pipefail

# Need to use -L to follow the 302 https://stackoverflow.com/questions/18474690/is-there-a-way-to-follow-redirects-with-command-line-curl

if [[ -f /tmp/testEpubAeroplanesAndDirigiblesOfWar.epub ]]; then
	echo "Book exists"
else
curl -L "https://www.gutenberg.org/ebooks/793.epub3.images" > /tmp/testEpubAeroplanesAndDirigiblesOfWar.epub
fi

#curl -v -X POST "$1" -H "Content-Type:multipart/form-data" -F "payload_json={\"content\":\"Have a nice day\"};type=application/json"
     
# https://discord.com/developers/docs/resources/webhook
# https://discord.com/developers/docs/reference#uploading-files

curl -X POST "$1" \
	 -H "Content-Type:multipart/form-data" \
	 -F 'payload_json={"content":"Here is a normal message", "attachments":[{"id":0, "description": "Aeroplanes and Dirigibles of War by Frederick Arthur Ambrose Talbot", "filename": "AeroplanesAndDirigiblesOfWar.epub"}]};type=application/json' \
	 -F "files[0]=@/tmp/testEpubAeroplanesAndDirigiblesOfWar.epub;filename='AeroplanesAndDirigiblesOfWar.epub';type=application/epub+zip;"
#rm /tmp/testEpubAeroplanesAndDirigiblesOfWar.epub