#!/bin/bash
# WF 2021-09-26


#
# get a pymediawiki docker copy
# 
installAndGetMediaWikiDocker() {
  pip install -U pymediawikidocker
  mwcluster --forceRebuild --versionList 1.31.14 --smwVersion 3.2.3 --basePort 9780 --sqlBasePort 9736 --wikiIdList myor --extensionList "Admin Links"  "BreadCrumbs2" "Cargo" "CategoryTree" "ConfirmEdit" "ConfirmUserAccounts" "Data Transfer" "Header Tabs" "InputBox" "Semantic Result Formats" "SyntaxHighlight" "Variables"
  pip install -U py-3rdparty-mediawiki
}

#
# setup wikiuser
#
setupWikiUser() {
	wikicredpath=$HOME/.mediawiki-japi/
	orcredentials=$wikicredpath/${USER}_or.ini 
	if [ ! -f $orcredentials ]
	then
		echo "creating $orcredentials"
		mkdir -p $wikicredpath
	cat << EOF > $orcredentials
# Mediawiki JAPI credentials for OPENRESEARCH
# 2021-06-26 
user=$USER
scriptPath=/mediawiki/
version=MediaWiki 1.31.7
email=
url=https\://www.openresearch.org
wikiId=or
EOF
	fi
}

#
# copy OPENRESEARCH Wiki
#
copyWiki() {
	# get all pages that are semantified
	wikipush -s or -t myor -q "[[Modification date::+]]" --progress -qd 10
}


installAndGetMediaWikiDocker
setupWikiUser
copyWiki