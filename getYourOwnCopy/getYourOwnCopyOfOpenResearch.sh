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
  echo "--fix: use migration/fix mode when creating the copy"
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
# get the IsoTime
#
getIsoTime() {
  date "+%Y-%m-%d %H:%M:%S"
}

#
# get a backup of the given wiki
#
# params:
#    #1: l_wikiId - the id of the wiki to backup
#
getBackup() {
  local l_wikiId="$1"
  wikibackupdir=$HOME/wikibackup
  timestamp=$(getIsoTime)

  # check the backup directory
  if [ ! -d $wikibackupdir/$l_wikiId ]
  then
    color_msg $blue "starting initial wiki backup for $l_wikiId at $timestamp... "
    wikibackup --source $l_wikiId --progress --query "[[Modification date::+]]" -qd 10 --git
    timestamp=$(getIsoTime)
    color_msg $green "initial wiki backup for $l_wikiId done at $timestamp"
  else
    color_msg $blue "starting incremental backup for $l_wikiId at $timestamp ..."
    timestamp=$(getIsoTime)
    # https://stackoverflow.com/questions/4561895/how-to-recursively-find-the-latest-modified-file-in-a-director
pythonCode=/tmp/getLastModified.py
cat << EOF > $pythonCode
import glob
import os
import datetime
import sys
root=sys.argv[1]
list_of_files = glob.glob(f'{root}/*.wiki') # * means all if need specific format then *.csv
if len(list_of_files)>0:
    latest_file = max(list_of_files, key=os.path.getctime)
    lastModified=os.stat(latest_file).st_mtime
    print(datetime.datetime.fromtimestamp(lastModified))
EOF
    latestModificationDate=$(python $pythonCode $wikibackupdir/$l_wikiId)
    echo "latest backup file: $latestModificationDate"
    wikibackup --source $l_wikiId --progress --query "[[Modification date::>$latestModificationDate]]" -qd 10 --git
    color_msg $green "incremental wiki backup for $l_wikiId done at $timestamp"
  fi
}

#
# copy OPENRESEARCH Wiki
# params
#   1: source wiki
#   2: entries to be copied since when
#   3: mode
#
copyWiki() {
  local l_source="$1"
  local l_since="$2"
  local l_mode="$3"
  # get all pages that are semantified
  # wikipush -s or -t myor -q "[[Modification date::+]]" --progress -qd 10
  wikipush -s $l_source -t myor -q "[[Property:+]]"
  wikipush -s $l_source -t myor -q "[[Form:+]]"
  wikipush -s $l_source -t myor -q "[[Help:+]]"
  wikipush -s $l_source -t myor -q "[[Concept:+]]"
  wikipush -s $l_source -t myor -q "[[Template:+]]"
  wikipush -s $l_source -t myor -q "[[Category:Template]]"
  wikipush -s $l_source -t myor -p "Template:Event" "Template:Event series" "Template:Tablelongrow" "Template:TableRow" "Template:Tablesection"
  wikipush -s $l_source -t myor -p "List of Events"
  wikipush -s $l_source -t myor -p "Template:Col-begin" "Template:Col-1-of-3" "Template:Col-2-of-3" "Template:Col-3-of-3" "Template:Col-end" "Template:Research_field_tpl" "Template:Yearly_calendar"
  wikipush -s $l_source -t myor -f -p "Main Page" "MediaWiki:Sidebar" --withImages
  case $l_mode in
    copy)
      wikipush -s $l_source -t myor -q "[[isA::Event]][[Modification date::>$l_since]]" --withImages --progress -qd 10
      wikipush -s $l_source -t myor -q "[[Category:Event series]][[Modification date::>$l_since]]" --withImages --progress -qd 10
    ;;
    fix)
      # generate LocationPages
      python ../migration/ormigrate/EventLocationHandler.py --decile 9 -s orclone --wikiTextPath ~/.or/showcase
      # backup event and event series pages to apply the fixers to
      wikibackup -s $l_source -q "[[isA::Event]][[Modification date::>$l_since]]" --withImages --progress -qd 10 --backupPath ~/.or/showcase
      wikibackup -s $l_source -q "[[Category:Event series]][[Modification date::>$l_since]]" --withImages --progress -qd 10 --backupPath ~/.or/showcase
      # apply fixers
      python ../migration/ormigrate/issue220_location.py -s $l_source --fix --wikiTextPath ~/.or/showcase --force
      wikirestore -t myor --backupPath ~/.or/showcase
    ;;
  esac
}

since=2006
wikiId=orclone
mode=copy
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
    --fix)
      mode=fix
      ;;
  esac
  shift
done
timestamp=$(getIsoTime)
echo "Starting to create a local docker copy of OPENRESEARCH  at $timestamp ..."
getBackup $wikiId
timestamp=$(getIsoTime)
echo "Installing docker SemanticMediaWiki with extensions at $timestamp ..."
installAndGetMediaWikiDocker
setupWikiUser $wikiId
echo "copying wiki content in mode $mode"
copyWiki $wikiId $since $mode
echo "Done with creating a local docker copy of OPENRESEARCH."
date
