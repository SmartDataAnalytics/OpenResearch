#!/bin/bash
# WF 2021-09-26


#
# get a pymediawiki docker copy
#
installAndGetMediaWikiDocker() {
  pip install -U pymediawikidocker
  mwcluster --forceRebuild --versionList 1.31.14 --smwVersion 3.2.3 \
     --basePort 9780 --sqlBasePort 9736 --wikiIdList myor \
     --extensionList "Admin Links"  "BreadCrumbs2" "Cargo" "CategoryTree" \
      "ConfirmAccount" "ConfirmEdit" "Data Transfer" "Header Tabs" \
      "ImageMap", "InputBox" "LanguageSelector" "MagicNoCache" "Maps7" "Nuke" "Page Forms" \
      "ParserFunctions" "PDFEmbed" "Renameuser" "Replace Text" "Semantic Result Formats" "SyntaxHighlight" \
      "TitleBlacklist"  "UrlGetParameters" "Variables" 
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
  local l_source="$1"
  # get all pages that are semantified
  # wikipush -s or -t myor -q "[[Modification date::+]]" --progress -qd 10
  wikipush -s $l_source -t myor -q "[[Property:+]]"
  wikipush -s $l_source -t myor -q "[[Form:+]]"
  wikipush -s $l_source -t myor -q "[[Help:+]]"
  wikipush -s $l_source -t myor -q "[[Concept:+]]"
  wikipush -s $l_source -t myor -q "[[Template:+]]"
  wikipush -s $l_source -t myor -p "Template:Event" "Template:Event series" "Template:Tablelongrow" "Template:Tablerow" "Template:Tablesection"
  wikipush -s $l_source -t myor -q "[[isA::Event]][[Modification date::>2021]]" --progress -qd 10
  wikipush -s $l_source -t myor -q "[[Category:Event series]][[Modification date::>2021]]" 
}


installAndGetMediaWikiDocker
setupWikiUser
copyWiki or
  