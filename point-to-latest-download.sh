git checkout master &&
VERSION=`cat script.video.parentalcontrols/addon.xml |grep  'id="script.video.parentalcontrols"' |sed 's,.*version *= *"\([^"]*\)".*,\1,'` &&
echo version is $VERSION &&
git checkout gh-pages &&
sed -i "" 's,script.video.parentalcontrols-[^"]*\.zip,script.video.parentalcontrols-$VERSION.zip,' index.html &&
echo git commit index.html -m "pointing to latest download ($VERSION)" &&
echo git push 
