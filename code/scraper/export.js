const builder = require('xmlbuilder');
const db = require('./db');
const moment = require('moment');
const fs = require('fs');

const DATE_FORMAT = 'YYYY/MM/DDThh:mm:ss';

let template = `{{Event 
|Acronym={$Acronym} 
|Title={$Title} 
|Type={$Type} 
|Field={$Field}
|Start date={$Start}
|End date={$End} 
|City={$City} 
|Country={$Country}
|Homepage={$Homepage}
|Submission deadline={$Submission_date}
}}
{$description}`;


(async function() {


	let j = 0;
	while (true) {
		let conferences = await db.Conference.findAll({where:{title: {$not: null}, export_safe: true, submission_deadline: {$gt: new Date()}}, include: [{model: db.Category, where: {active: true}}], offset: j * 50, limit: 50});



		if (conferences.length == 0)
			break;
		
		let root = createRoot();
		for (let i = 0; i < conferences.length; i++) {
	 		let conference = conferences[i];
			createPage(root, conference);
		}

		console.log('import', (j + 1), conferences.length);
		fs.writeFile('/home/omid/Desktop/import' + (j + 1) + '.xml', root.end({pretty: true}), 'utf8');
		j++;
	}

	
})();


function createRoot() {
	let root = builder.create('mediawiki',{version: '1.0', encoding: 'UTF-8'});
	root.att('xsi:schemaLocation', 'http://www.mediawiki.org/xml/export-0.4/ http://www.mediawiki.org/xml/export-0.4.xsd');
	root.att('xmlns','https://www.mediawiki.org/xml/export-0.4/');
	root.att('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance');
	root.att('version', '0.4');

	return root;
}

function createPage(root, obj) {
	let page = root.ele('page');
	page.ele('title', obj.title.split('\n')[0]);
	let revision = page.ele('revision');
	revision.ele('timestamp', obj.acronym);


	let type = 'Conference';
	if (obj.title.split('\n')[0].match(/workshop/ig)) {
		type = 'Workshop';
	} 

	// console.log(type, obj.title.split('\n')[0]);;
	let content = template.replace('{$Acronym}', obj.acronym)
			.replace('{$Title}', obj.title.split('\n')[0])
			.replace('{$Homepage}', obj.original_link)
			.replace('{$Submission_date}', moment(obj.submission_deadline).format(DATE_FORMAT))
			.replace('{$description}', obj.description)
			.replace('{$Field}', obj.Category.title)
			.replace('{$Type}', type);
	
	if (obj.duration !== null && obj.duration !== 'N\A') {
		let parts = obj.duration.split('-');
		content = content
			.replace('{$Start}', moment(parts[0]).format(DATE_FORMAT))
			.replace('{$End}', moment(parts[1]).format(DATE_FORMAT));
	}

	if (obj.location !== null && obj.location !== 'N\A') {
		let parts = obj.location.split(',');
		content = content
			.replace('{$City}', parts[0])
			.replace('{$Country}', parts[1]);
	}
	
	revision.ele('text', content).att('xml:space', 'preserve');

	return page;
}



// console.log(root.end({pretty: true}));
