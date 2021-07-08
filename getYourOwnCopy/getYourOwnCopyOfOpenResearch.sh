#!/bin/bash
# WF 2021-09-26

#ansi colors
#http://www.csc.uvic.ca/~sae/seng265/fall04/tips/s265s047-tips/bash-using-colors.html
blue='\033[0;34m'
red='\033[0;31m'
green='\033[0;32m' # '\e[1;32m' is too bright for white bg.
endColor='\033[0m'

#
# a colored message
#   params:
#     1: l_color - the color of the message
#     2: l_msg - the message to display
#
color_msg() {
  local l_color="$1"
  local l_msg="$2"
  echo -e "${l_color}$l_msg${endColor}"
}

#
# error
#
# show the given error message on stderr and exit
#
#   params:
#     1: l_msg - the error message to display
#
error() {
  local l_msg="$1"
  # use ansi red for error
  color_msg $red "Error:" 1>&2
  color_msg $red "\t$l_msg" 1>&2
  exit 1
}


# show usage
#
usage() {
  echo "$0 [-h|--help]"
  echo ""
  echo "-h | --help: show this usage"
  echo "--since: get entities from the given date/iso date e.g. 2008"
  echo "--wikiId: retrieve data from the wiki with the given wikiId e.g. or/orclone"
  exit 1
}

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
# param
#   1: wikiId of the source wiki
#
setupWikiUser() {
  local wikiId="$1"
	wikicredpath=$HOME/.mediawiki-japi/
	orcredentials=$wikicredpath/${USER}_$wikiId.ini
	if [ ! -f $orcredentials ]
	then
		echo "creating $orcredentials"
		mkdir -p $wikicredpath
    url="https\://www.openresearch.org"
    case $wikiId in
      or)
        url="https\://www.openresearch.org"
        version="MediaWiki 1.31.15"
        scriptPath="/mediawiki"
        ;;
      orclone)
        url="https://confident.dbis.rwth-aachen.de"
        version="MediaWiki 1.31.15"
        scriptPath="/or"
        ;;
      *)
        error "unknown OpenResearch wikiId $wikiId"
    esac
	cat << EOF > $orcredentials
# Mediawiki JAPI credentials for OPENRESEARCH
# 2021-06-26
user=$USER
scriptPath=$scriptPath
version=$version
email=
url=$url
wikiId=$wikiId
EOF
	fi
}

#
# copy OPENRESEARCH Wiki
# params
#   1: source wiki
#   2: entries to be copied since when
#
copyWiki() {
  local l_source="$1"
  local l_since="$2"
  # get all pages that are semantified
  # wikipush -s or -t myor -q "[[Modification date::+]]" --progress -qd 10
  wikipush -s $l_source -t myor -q "[[Property:+]]"
  wikipush -s $l_source -t myor -q "[[Form:+]]"
  wikipush -s $l_source -t myor -q "[[Help:+]]"
  wikipush -s $l_source -t myor -q "[[Concept:+]]"
  wikipush -s $l_source -t myor -q "[[Template:+]]"
  wikipush -s $l_source -t myor -p "Template:Event" "Template:Event series" "Template:Tablelongrow" "Template:Tablerow" "Template:Tablesection"
  wikipush -s $l_source -t myor -q "[[isA::Event]][[Modification date::>$l_since]]" --progress -qd 10
  wikipush -s $l_source -t myor -q "[[Category:Event series]][[Modification date::>$l_since]]" --progress -qd 10
  wikipush -s $l_source -t myor -p "Template:Col-begin" "Template:Col-1-of-3" "Template:Col-2-of-3" "Template:Col-3-of-3" "Template:Col-end" "Template:Research_field_tpl" "Template:Yearly_calendar"
  wikipush -s $l_source -t myor -f -p "Main Page" "MediaWiki:Sidebar"
}

since=2006
wikiId=orclone
while [  "$1" != ""  ]
do
  option="$1"
  case $option in
    -h|--help) usage;;
    --since)
      since=$option
      ;;
    --wikiId)
      wikiId=$option
      ;;
  esac
  shift
done

installAndGetMediaWikiDocker
setupWikiUser $wikiId
copyWiki $wikiId $since
