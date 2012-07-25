rm dist/script.video.parentalcontrols-*
zip -r dist/script.video.parentalcontrols-`cat script.video.parentalcontrols/addon.xml |grep  'id="script.video.parentalcontrols"' |sed 's,.*version *= *"\([^"]*\)".*,\1,'`.zip script.video.parentalcontrols/
