from corpus.datasources.openresearch import OREvent
from wikifile.smw import TemplatePage, Template, Table
from wikifile.utils import TemplateParam, MagicWord, PageLink, Widget, ParserFunction, SetProperties


class Show(Widget):
    """Renders a show query for the given property of the page"""

    def __init__(self, prop:str):
        self.prop=prop

    def render(self):
        markup=f"{{{{#show:{ MagicWord('PAGENAME') }|?{self.prop} }}}}"
        return markup


class LocationTemplatePage(TemplatePage):
    """
    Renders the Template page for openresearch locations
    """

    @property
    def viewmodes(self) -> dict:
        """
        overwrites the default view mode
        """
        viewmodes = super(LocationTemplatePage, self).viewmodes
        # overwrite the default viewmode
        template=f"""
{ '{{' }#display_map:center={ TemplateParam('coordinates') }|zoom={ TemplateParam('zoomLevel', defaultValue=5) }|service=leaflet|width=280|height=280{ '}}' }
{ '{{' }#ask: [[location partOf::{ MagicWord('PAGENAME') }]]
|mainLabel=parts
|?Location locationKind=kind
{ '}}' }

'''Conferences'''
{ '{{' }#ask: [[isA::Event]] [[has location city::{ TemplateParam('name') }]]
|format=count
{ '}}' } events for { TemplateParam('name') } are known to this wiki.
{ '{{' }HideShow|ConferencesForLocation|
{ '{{' }#ask: [[isA::Event]] [[has location city::{ TemplateParam('name') }]]
| ?title = Name
| ?has location city = City
| ?has location country = Country
| ?Start date#-F[M j] = Start
| ?End date#-F[M j] = End
| mainlabel=Acronym
| format=table
| limit = 50
| sort= Start date
{ '}}' }
{ '}}' }

Upcoming:
<small>
{ '{{' }#ask: [[isA::Event]] [[has location city::{ TemplateParam('name') }]] [[End date::>{ MagicWord('CURRENTYEAR') }-{MagicWord('CURRENTMONTH') }-{MagicWord('CURRENTDAY') }]]
| ?title = Name
| ?has location city = City
| ?has location country = Country
| ?Submission deadline#-F[M j] = Submissions due
| ?Start date#-F[M j] = Start
| ?End date#-F[M j] = End
| mainlabel=Acronym
| format=table
| limit = 7
| sort= Start date
{ '}}' }
</small>"""
        viewmodes['#default'] = viewmodes['#default'] + template
        return viewmodes
class EventTemplatePage(TemplatePage):
    """
    Renders the Template page for openresearch events
    uses the current or event template and sets it as default viewmode. To separate the property assignment from the
    displaying of the entity informtation the property assignments were removed from the entity information table.

    Note: This Widget is in an early stage currently only mimics the current design.
    """

    @property
    def storemodes(self) -> dict:
        storemodes=super(EventTemplatePage, self).storemodes
        # add isA property to storemode
        default=storemodes.get("#default")
        if isinstance(default, SetProperties):
            if isinstance(default.arguments, list):
                default.arguments.append(f"isA={self.topic.get_pageTitle()}")
                default.arguments.append("Has year="+"{{{Year|{{#time:Y|{{{Start date|1500}}}}}}}}")
        return storemodes

    @property
    def viewmodes(self) -> dict:
        """
        overwrites the default view mode
        """
        viewmodes = super(EventTemplatePage, self).viewmodes
        escape=True
        pipeStr="{{!}}" if escape else "|"
        basicInformationRows=[
            "{{#ifeq:{{{Logo|}}}|||{{Tablelongrow|Align=Center|Value=[[Image:{{{Logo}}}|frameless|Logo of {{{Name|{{PAGENAME}}}}}]] }}}}",
            "{{#ifeq:{{{Title|}}}|||{{Tablelongrow|Value={{{Title}}} }}}}",
            "{{#ifeq:{{{Ordinal|}}}|||{{TableRow|Label=Ordinal|Value={{{Ordinal}}}}}}}",
            "{{#ifeq:{{{Series|}}}|||{{TableRow|Label=Event in series|Value=[[{{{Series}}}]]}}}}",
            "{{#ifeq:{{{Superevent|}}}|||{{TableRow|Label=Subevent of|Value={{{Superevent}}}}}}}",
            "{{#ifeq:{{{Start date|}}}|||{{TableRow|Label=Dates|Value={{{Start date}}} {{#ifeq:{{{End date|}}}|||<small>{{#ask:[[{{PAGENAME}}]]|?start date=start|?end date=end|?has location city=location|searchlabel=(iCal)|format=icalendar}}</small>}}}} - {{#ifeq:{{{End date|}}}|||{{{End date}}}}} }}",
            "{{#ifeq:{{{presence|}}}|||{{TableRow|Label=Presence|Value={{{presence}}}}}}}",
            "{{#ifeq:{{{Homepage|}}}|||{{TableRow|Label=Homepage:|mandatory|Value={{#show: {{PAGENAME}}|?Homepage}} }}}}",
            "{{#ifeq:{{{Twitter account|}}}|||{{TableRow|Label=Twitter account:|Value={{{Twitter account}}}}}}}",
            "{{#ifeq:{{{Submitting link|}}}|||{{TableRow|Label=Submitting link:|Value={{{Submitting link}}}}}}}",
        ]
        locationInfoRows=[
            "{{#ifeq:{{{City|}}}{{{State|}}}{{{Country|}}}|||{{Tablesection|Label=Location|Color=#ADD8E6|Textcolor=#fff}}}}",
            "{{TableRow| Label=Location:| | Value={{#ifeq:{{{City|}}}|||{{{City}}}}}{{#ifeq:{{{State|}}}|||, {{{State}}}}}{{#ifeq:{{{Country|}}}|||, {{{Country}}}}} }}",
            "{{#if:{{{City|}}}|{{Tablesection|Label={{#display_map:{{{City|}}}|service=leaflet|width=280|height=280}}<br />}}}}",
        ]
        dateInfoRows=[
            "{{#ifeq:{{{Abstract deadline|}}}{{{Submission deadline|}}}{{{Notification|}}}{{{Camera ready|}}}{{{Paper deadline|}}}{{{Poster deadline|}}}{{{Demo deadline|}}}|||{{Tablesection|Label=Important dates|Color= #ADD8E6|Textcolor=#fff}}}}",
            "{{#ifeq:{{{Workshop deadline|}}}|||{{TableRow|Label=Workshops:|Value={{{Workshop deadline}}}}}}}",
            "{{#ifeq:{{{Tutorial deadline|}}}|||{{TableRow|Label=Tutorials:|Value={{{Tutorial deadline}}}}}}}",
            "{{#ifeq:{{{Abstract deadline|}}}|||{{TableRow|Label=Abstracts:|Value={{{Abstract deadline}}}}}}}",
            "{{#ifeq:{{{Paper deadline|}}}|||{{TableRow|Label=Papers:|Value={{{Paper deadline}}}}}}}",
            "{{#ifeq:{{{Poster deadline|}}}|||{{TableRow|Label=Posters:|Value={{{Poster deadline}}}}}}}",
            "{{#ifeq:{{{Demo deadline|}}}|||{{TableRow|Label=Demos:|Value={{{Demo deadline}}}}}}}",
            "{{#ifeq:{{{Submission deadline|}}}|||{{TableRow|Label=Submissions:|Value={{{Submission deadline}}}}}}}",
            "{{#ifeq:{{{Last Accepted Rates|}}}|||{{TableRow|Label=Last Accepted Rates:|Value={{{Last Accepted Rates}}}}}}}",
            "{{#ifeq:{{{Notification|}}}|||{{TableRow|Label=Notification:|Value={{{Notification}}}}}}}",
            "{{#ifeq:{{{Camera ready|}}}|||{{TableRow|Label=Camera ready due:|Value={{{Camera ready}}}}}}}",
            "{{#ifeq:{{{Superevent|}}}||{{Tablelongrow|Align=Left|Font size=80%|Value={{#ask: [[subevent of::{{PAGENAME}}]]| intro=Subevents:_ | sep=,_}}}}|}}",
            "{{#ifeq:{{{Registration link|}}}|||{{TableRow|Label=Registration link:|Value={{{Registration link}}}}}}}",
            "{{#ifeq:{{{Accepted short papers|}}}|||{{TableRow|Label=Accepted short papers:|Value={{{Accepted short papers}}}}}}}",
            "{{#ifeq:{{{Attendance fee|}}}|||{{TableRow|Label=Attendance fee:|Value={{{Attendance fee currency}}} {{{Attendance fee}}} / {{{Attendance fee reduced}}} (reduced)}}}}",
            "{{#ifeq:{{{Early bird student|}}}|||{{TableRow|Label=Early bird student:|Value={{{Attendance fee currency}}} {{{Early bird student}}} / {{{Early bird fee reduced}}} (reduced)}}}}",
            "{{#ifeq:{{{On site student|}}}|||{{TableRow|Label=On site student:|Value={{{Attendance fee currency}}} {{{On site student}}} / {{{On site fee reduced}}} (reduced)}}}}",
            "{{#ifeq:{{{Early bird regular|}}}|||{{TableRow|Label=Early bird regular:|Value={{{Attendance fee currency}}} {{{Early bird regular}}}}} }}",
            "{{#ifeq:{{{On site regular|}}}|||{{TableRow|Label=On site regular:|Value={{{Attendance fee currency}}} {{{On site regular}}}}} }}",
            "{{#ifeq:{{{Submitted papers|}}}|||{{TableRow|Label=Papers:|Value=Submitted {{{Submitted papers}}} / Accepted {{{Accepted papers}}} ([[Acceptance rate::{{#expr:{{{Accepted papers}}}/{{{Submitted papers}}}*100 round 1}}]] %)}}}}"   # Note: Acceptance rate is a property that is generated and set by the template therefore it currently stays here but should be moved to the storemode section for a clear separation of concerns
        ]
        committeesInfoRows=[
            "{{#ifeq:{{{Has coordinator|}}}{{{has general chair|}}}{{{has program chair|}}}{{{has workshop chair|}}}{{{has OC member|}}}{{{has tutorial chair|}}}{{{has demo chair|}}}{{{Has PC member|}}}|||{{Tablesection|Label=Committees|Color= #ADD8E6|Textcolor=#fff}}}}",
            "{{#ifeq:{{{Has coordinator|}}}|||{{TableRow|Label=Organizers:|Value={{{Has coordinator|}}} }} }}",
            "{{#ifeq:{{{has general chair|}}}|||{{TableRow|Label=General chairs:|Value={{{has general chair|}}} }} }}",
            "{{#ifeq:{{{has program chair|}}}|||{{TableRow|Label=PC chairs:|Value={{{has program chair|}}} }} }}",
            "{{#ifeq:{{{has workshop chair|}}}|||{{TableRow|Label=Workshop chairs:|Value={{{has workshop chair|}}} }} }}",
            "{{#ifeq:{{{has OC member|}}}|||{{TableRow|Label=Panel Chair:|Value={{{has OC member|}}} }} }}",
            "{{#ifeq:{{{has tutorial chair|}}}|||{{TableRow|Label=Seminars Chair:|Value={{{has tutorial chair|}}} }} }}",
            "{{#ifeq:{{{has demo chair|}}}|||{{TableRow|Label=Demo chairs:|Value={{{has demo chair|}}} }} }}",
            "{{#ifeq:{{{Has PC member|}}}|||{{TableRow|Label=PC members:|Value={{{Has PC member|}}} }} }}",
            "{{#ifeq:{{{has Keynote speaker|}}}|||{{TableRow|Label=Keynote speaker:|Value={{{has Keynote speaker|}}} }} }}"
        ]
        tableOfContentsRow=[
            "{{Tablesection|Label=Table of Contents|Color=#ADD8E6|Textcolor=#fff}}",
            f'{pipeStr} colspan="2" style="padding-top: 2px; " {pipeStr}<div id="smworgtable-toc" style="font-size: 90%;">__TOC__</div>'
        ]
        twitterRows=[
            "{{#if:{{{Twitter account|}}}|{{Tablesection|Label=Tweets by {{{Twitter account}}}|Color=#ADD8E6|Textcolor=#fff}}|}}"
            f'{pipeStr}  colspan="2" style="padding-top: 2px; " {pipeStr} '+' {{#if:{{{Twitter account|}}}|<div><html><a class="twitter-timeline" height="400" width="350" href="https://twitter.com/</html>{{{Twitter account}}}<html>">Tweets by {{{Twitter account}}}</a> <script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script></html></div>|}}'
        ]
        joinStr=f"\n{pipeStr}-\n"
        #ToDo: add event template
        template=f"""
 {{{pipeStr} cellspacing="0" cellpadding="5" style="position:relative; margin: 0 0 0.5em 1em; border-collapse: collapse; border: 1px solid #aaa; background: #fff; float: right; clear: right; width: 20em"
! colspan="2" style="background: #ADD8E6; color: black" {pipeStr} { MagicWord('PAGENAME') }     
{ joinStr.join([*basicInformationRows,*locationInfoRows,*dateInfoRows,*committeesInfoRows,*tableOfContentsRow,*twitterRows]) }
{pipeStr}}}
__SHOWFACTBOX__
{{{{#default_form:Event}}}}
"""
        viewmodes["#default"] = template
        return viewmodes

class RatedEventTemplatePage(EventTemplatePage):
    """
    Renders the template page for a rated event. This means that an event page is rendered with aggregated rating
    information and a link to the rating subpage.
    """

    @staticmethod
    def getRatingTable():
        table = Table(css_class="wikitable", escape=True)
        header = table.add_row()
        header.add_cell("median", is_header=True)
        header.add_cell("worst", is_header=True)
        painRow = table.add_row()
        painRow.add_cell(
            "{{PainScale|{{#expr: ceil({{#ask:[[-has subobject::{{PAGENAME}}/rating]]|mainlabel=-|?Rating pain|format=median}})}}}}")
        painRow.add_cell(
            "{{PainScale|{{#ask:[[-has subobject::{{PAGENAME}}/rating]]|mainlabel=-|?Rating pain|format=max}}}}")
        return table

    @property
    def viewmodes(self) -> dict:
        viewmodes = super(RatedEventTemplatePage, self).viewmodes
        table=self.getRatingTable()

        template=f"""
== Event Rating ==
{ table.render() }
List of all ratings can be found at [[{MagicWord('PAGENAME')}/rating]]
"""
        viewmodes["#default"]=template+viewmodes["#default"]
        return viewmodes

class RatingTemplatePage(TemplatePage):
    """
    Renders the Template page for the Rating topic.
    Overwrites the viewmodes of the default storemode
    """

    @property
    def viewmodes(self) -> dict:
        viewmodes=super(RatingTemplatePage, self).viewmodes
        # overwrite the default viewmode
        ratingComparisonTable=Table(css_class="wikitable", escape=True)
        ratingOnlyTable = Table(css_class="wikitable", escape=True)
        for table, withFixerCol in [(ratingOnlyTable, False), (ratingComparisonTable, True)]:
            fixerRow=table.add_row()
            fixerRow.add_cell(PageLink("Rating fixer::@@@","fixer"), is_header=True)
            fixerRow.add_cell(TemplateParam("fixer"), is_header=True, colspan=2)
            timeRow=table.add_row()
            if withFixerCol:
                timeRow.add_cell("",is_header=True)
                timeRow.add_cell("Before", is_header=True)
                timeRow.add_cell("After", is_header=True)
            for prop in ["pain", "reason", "hint"]:
                row = table.add_row()
                row.add_cell(PageLink(f"Rating {prop}::@@@",prop),is_header=True)
                if prop == "pain":
                    painScale=lambda x:f"{{{{#ifeq:{x}|||[[File:Pain{x}.svg|50px|link=https://commons.wikimedia.org/wiki/File:Pain{x}.svg]]}}}}"
                    row.add_cell(painScale(TemplateParam(prop)))
                    if withFixerCol:
                        row.add_cell(painScale(TemplateParam(f"{prop}After")))
                else:
                    row.add_cell(TemplateParam(prop))
                    if withFixerCol:
                        row.add_cell(TemplateParam(f"{prop}After"))
        viewmodes={
            'ratingOnly':ratingOnlyTable.render(),
            'ratingComparison':None, # fall through
            '#default':ratingComparisonTable.render()
        }
        return viewmodes

class EventSeriesTemplatePage(TemplatePage):
    """
    Renders the temlate page for or event series
    """

    @property
    def storemodes(self) -> dict:
        storemodes = super(EventSeriesTemplatePage, self).storemodes
        # add isA property to storemode
        default = storemodes.get("#default")
        if isinstance(default, SetProperties):
            if isinstance(default.arguments, list):
                default.arguments.append(f"isA={self.topic.get_pageTitle()}")
        return storemodes

    @property
    def viewmodes(self) -> dict:
        viewmodes = super(EventSeriesTemplatePage, self).viewmodes
        # overwrite the default viewmode
        escape=True
        pipeStr="{{!}}" if escape else "|"
        joinStr = f"\n{pipeStr}-\n"
        basicInfoRows=[
            str(DisplayValueInRowIfPresent("Logo", TableLongRow("[[Image:{{{Logo}}}|frameless|Logo of {{{Name|{{PAGENAME}}}}}]]", escape=True))),   # Testing Widget usefulness
            "{{#ifeq:{{{Title|}}}|||{{Tablelongrow|Value='''{{{name}}}'''|Color=#fdddbb}}}}",
            "{{#ifeq:{{{Field|}}}|||{{Tablelongrow|Value=Categories: {{{Field|}}} }} }}",
            "{{#ifeq:{{{Homepage|}}}|||{{Tablelongrow|Value={{#show: {{PAGENAME}}|?Homepage}} }} }}",
            "{{#ifeq:{{{WikiDataId|}}}|||{{TableRow|Label=WikiDataId:|Value={{#show: {{PAGENAME}}|mainlabel=-|?Wikidataid}} }}}}",
            "{{#ifeq:{{{WikiDataId|}}}|||{{TableRow|Label=Scholia:|Value=https://scholia.toolforge.org/event-series/{{{WikiDataId}}}}}}}",
            "{{#ifeq:{{{DblpSeries|}}}|||{{TableRow|Label=DblpSeries:|Value={{#show: {{PAGENAME}}|mainlabel=-|?DblpSeries}} }}}}",
            "{{#ifeq:{{{WikiCfpSeries|}}}|||{{TableRow|Label=WikiCFP Series:|Value={{#show: {{PAGENAME}}|mainlabel=-|?WikiCfpSeries}} }}}}",
            "{{#ifeq:{{{has Twitter|}}}|||{{TableRow|Label=Twitter:|Value={{{has Twitter}}} }}}}",
            "{{#ifeq:{{{organizer|}}}|||{{TableRow|Label=Organizer:|Value={{{organizer}}} }}}}",
            "{{#ifeq:{{{has Bibliography|}}}|||{{TableRow|Label=Bibliography:|Value= {{{has Bibliography}}} }}}}",
            "{{#ifeq:{{{has CORE2017 Rank|}}}|||{{TableRow|Label=CORE Rank (2017):|Value={{{has CORE2017 Rank}}}}}}}",
            "{{#ifeq:{{{has CORE2018 Rank|}}}|||{{TableRow|Label=CORE Rank (2018):|Value={{{has CORE2018 Rank}}}}}}}",
            "{{#if: {{#ask: [[Event in series::{{PAGENAME}}]] | ?Acceptance rate | format=average}} | {{TableRow|Label=Avg. acceptance rate:|Value=[[has Average Acceptance Rate:={{#expr:{{#ask: [[Event in series::{{PAGENAME}}]] | ?Acceptance rate | format=average}} round 1}}]]}} }}",
            "{{{isA|Event series}}}",
            "{{#if: {{#ask: [[Event in series::{{PAGENAME}}]] | ?Acceptance rate | format=average | sort = Start date| order = DESC | limit = 5}}| {{TableRow|Label=Avg. acceptance rate (last 5 years):|Value=[[has Average 5y Acceptance Rate:={{#expr:{{#ask: [[Event in series::{{PAGENAME}}]] | ?Acceptance rate | format=average | sort = Start date| order = DESC | limit = 5}} round 1}}]]}} }}"
        ]
        tableOfContentsRows=[
            "{{Tablesection|Label=Table of Contents|Color=#fdddbb|Textcolor=#fff}}",
            f'{pipeStr} colspan="2" style="padding-top: 2px; " {pipeStr}<div id="smworgtable-toc" style="font-size: 90%;">__TOC__</div>'
        ]
        twitterRows=[
            "{{#if:{{{Twitter account|}}}|{{Tablesection|Label=Tweets by {{{has Twitter}}}|Color=#fdddbb|Textcolor=#fff}}|}}",
            f'{pipeStr}  colspan="2" style="padding-top: 2px; " {pipeStr} '+' {{#if:{{{Twitter account|}}}|<div><html><a class="twitter-timeline" height="400" width="350" href="https://twitter.com/</html>{{{Twitter account}}}<html>">Tweets by {{{Twitter account}}}</a> <script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script></html></div>|}}'
        ]
        metrics="""{{#if: {{#ask: [[Event in series::{{PAGENAME}}]] | ?Acceptance rate | format=average}} | 
{{{Title}}} ({{PAGENAME}}) has an average acceptance rate of [[has Average Acceptance Rate:={{#expr:{{#ask: [[Event in series::{{PAGENAME}}]] | ?Acceptance rate | format=average}} round 1}}]]% 
{{#if: {{#ask: [[Event in series::{{PAGENAME}}]] | ?Acceptance rate | format=average | sort = Start date| order = DESC | limit = 5}} |
(last 5 years  [[has Average 5y Acceptance Rate:={{#expr:{{#ask: [[Event in series::{{PAGENAME}}]] | ?Acceptance rate | format=average | sort = Start date| order = DESC | limit = 5}} round 1}}]]%)
}}.
}}"""
        eventsShowCase="""==Events==
{{EventSeriesOverview|{{PAGENAME}} }}

==Submission/Acceptance==
{{#ask: [[Event in series::{{PAGENAME}}]][[Submitted papers::>0]][[Accepted papers::>0]]
 |?Submitted papers
 |?Accepted papers
 |?Acceptance rate
 |sort=,
 |order=descending
 |format=jqplotseries
 |charttype=bar
 |height=480|width=90%
 |headers=show
 |direction=vertical
 |group=property
 |numbersaxislabel=
 |datalabels=value
 |show=true
 |theme=simple
 |mainlabel={{PAGENAME}}
 |valueformat=%d
 |class=demo-float-right
 |grouplabel=subject
 |chartlegend=ne
}}

==Locations==
{{#ask: [[Event in series::{{PAGENAME}}]]
 | ?Has location city.Location coordinates
 | format = openlayers
}}

<!--
{{#ifeq:{{#arraymap:{{{Field|}}}|, |var|[[Category:var]]|&#32;}}|||{{#arraymap:{{{Field|}}}|, |var|[[Category:var]]|&#32;}}}}
-->
{{#ifeq:{{{Field|}}}|||{{#arraymap:{{{Field|}}}|, |var|[[Category:var]]|&#32;}}}}
{{#ifeq:{{{Field|}}}|||{{#arraymap:{{{Field|}}}|, |var|[[Has subject::Category:var| ]]|&#32;}}}}
"""
        template=f"""__NOCACHE__
{{{pipeStr} cellspacing="0" cellpadding="5" style="position:relative; margin: 0 0 0.5em 1em; border-collapse: collapse; border: 1px solid #aaa; background: #fff; float: right; clear: right; width: 20em"
! colspan="2" style="background: #ef7c00; color: white" {pipeStr} { MagicWord('PAGENAME') }
{joinStr.join([*basicInfoRows, *tableOfContentsRows, *twitterRows])}
{pipeStr}}}
{metrics}
{eventsShowCase}
__SHOWFACTBOX__
{{{{#default_form:EventSeries}}}}
"""
        viewmodes['#default'] = template
        return viewmodes
class RatedEventSeriesTemplatePage(EventSeriesTemplatePage):

    @property
    def viewmodes(self) -> dict:
        viewmodes = super(RatedEventSeriesTemplatePage, self).viewmodes
        table = RatedEventTemplatePage.getRatingTable()
        template = f"""
== Event series Rating ==
{table.render()}
List of all ratings can be found at [[{MagicWord('PAGENAME')}/rating]]
    """
        viewmodes["#default"] = template + viewmodes["#default"]
        return viewmodes


class TableLongRow(Widget):
    """
    Renders a headline row
    This Widget is equivalent to the Template:Tablelongrow
    """

    def __init__(self, value, align:str="center", color:str="white", fontSize:str="100%", escape:bool=False):
        """

        Args:
            value: vlaue to display
            align: alignment of the row content
            color: background color
            fontSize: fontsize
        """
        self.value=value
        self.align=align
        self.color=color
        self.fontSize=fontSize
        self.escape=escape

    def render(self):
        pipe="{{!}}" if self.escape else "|"
        markup=f'{pipe} colspan="2" style="text-align: {self.align}; background: {self.color}"{pipe}<div style="font-size: {self.fontSize}">{self.value}</div>'
        return markup

class TableRow(Widget):
    """
    Renders a two column row intended for a label and a value
    This widget is equivalent to Template:TableRow
    """

    def __init__(self, label, value):
        self.label=label
        self.value=value

    def render(self):
        pipe = "{{!}}" if self.escape else "|"
        markup=f'{pipe}style="vertical-align: top;" {pipe}{self.label}\n{pipe} {self.value}'
        return markup

class TableSection(Widget):
    """
    Renders a Table section
    This widget is equivalent to Template:Section
    """
    def __init__(self, label, color:str="#eee"):
        self.label=label
        self.color=color

    def render(self):
        pipe = "{{!}}" if self.escape else "|"
        markup=f'! colspan="2" style="text-align: center; background: {self.color}"{pipe} {self.label}\n'
        return markup

class DisplayValueInRowIfPresent(Widget):
    """
    Shows the property in the info table if defined
    """

    def __init__(self, check, value):
        """

        Args:
            check: template value to check
            value: value to display if template param has a value
        """
        self.check=check
        self.value=value

    def render(self):
        templatePram=TemplateParam(self.check)
        markup=f'{{{{#ifeq:{templatePram}|||{self.value}}}}}'
        return markup