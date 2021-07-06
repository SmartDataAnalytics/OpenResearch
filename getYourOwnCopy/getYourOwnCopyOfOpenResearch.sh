#!/bin/bash
# WF 2021-09-26
#
# get a pymediawiki docker copy
#
installAndGetMediaWikiDocker() {
  pip install -U pymediawikidocker
  # 1.31.15 does not work with diagrams and Mermaid
  # 1.35.3 is needed if diagrams should be displayed
  mwcluster --forceRebuild --versionList 1.35.3 --smwVersion 3.2.3 \
     --basePort 9780 --sqlBasePort 9736 --wikiIdList myor \
     --extensionList "Admin Links"  "BreadCrumbs2" "Cargo" "CategoryTree" \
      "ConfirmAccount" "ConfirmEdit" "Data Transfer" "Diagrams" "Header Tabs" \
      "ImageMap", "InputBox" "LanguageSelector" "MagicNoCache" "Maps7" "Mermaid" "Nuke" "Page Forms" \
      "ParserFunctions" "PDFEmbed" "Renameuser" "Replace Text" "Semantic Result Formats" "SyntaxHighlight" \
      "TitleBlacklist"   "Variables" \
      --logo https://confident.dbis.rwth-aachen.de/or/images/f/f2/OpenResearch-Logo-Copy.png
  #"UrlGetParameters"
  #
  pip install -U py-3rdparty-mediawiki
  pip install -U OpenResearchMigration
  pip install -U wikirender
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
version=MediaWiki 1.31.15
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
  wikipush -s $l_source -t myor -p "Template:Col-begin" "Template:Col-1-of-3" "Template:Col-2-of-3" "Template:Col-3-of-3" "Template:Col-end" "Template:Research_field_tpl" "Template:Yearly_calendar"
  wikipush -s $l_source -t myor -f -p "Main Page" "MediaWiki:Sidebar"
}


installAndGetMediaWikiDocker
setupWikiUser
copyWiki or
