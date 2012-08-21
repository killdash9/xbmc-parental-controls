FILENAME=repo/script.video.parentalcontrols/script.video.parentalcontrols-`cat script.video.parentalcontrols/addon.xml |grep  'id="script.video.parentalcontrols"' |sed 's,.*version *= *"\([^"]*\)".*,\1,'`.zip
rm $FILENAME
zip -r $FILENAME script.video.parentalcontrols/
git add $FILENAME
python addons_xml_generator.py
git status
echo "Don't forget to add, commit and push"
