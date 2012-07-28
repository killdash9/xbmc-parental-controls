FILENAME=script.video.parentalcontrols-`cat script.video.parentalcontrols/addon.xml |grep  'id="script.video.parentalcontrols"' |sed 's,.*version *= *"\([^"]*\)".*,\1,'`.zip
rm repo/script.video.parentalcontrols/$FILENAME
zip -r repo/script.video.parentalcontrols/$FILENAME script.video.parentalcontrols/
