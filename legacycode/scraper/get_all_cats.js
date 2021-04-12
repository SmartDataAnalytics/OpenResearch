 const rp = require('request-promise');
const cheerio = require('cheerio');
const colors = require('colors');
const fs = require('fs');
const utils = require('./utils');
const _ = require('lodash');
const db = require('./db');



const OUTPUT_FILE_PATH = './outputs/wcf-cats.json';
let baseUrl = 'http://www.wikicfp.com';
let url = baseUrl + '/cfp/allcat';

// where the program actually starts
(async function() {

	try {
		console.log('trying to download the category url'.cyan);
		let html = await utils.proxify('GET', url, null, null);
		const $ = cheerio.load(html.body);
		console.log('loaded successfuly'.cyan);

		// select nodes
		let misc = $('a', '.contsec');
		let count = misc.length;

		let keys = _.times(count, String);
		let links = [];
		keys.forEach(x => {
			links.push({title: $(misc[x]).text(), link: baseUrl +  $(misc[x]).attr('href')});
		});

		links.forEach(async (link) => {
			console.log(link);
			await db.Category.create(link);
		});

		console.log(links);

		
		// fs.writeFile(OUTPUT_FILE_PATH, JSON.stringify(links), 'utf8', function(err, done) {
			
		// 	if (!err) {
		// 		console.log(`Generated ${OUTPUT_FILE_PATH}. \n\rOperation completed successfuly`.green );
		// 	} else {
		// 		console.error(err);
		// 	}
		// });
		
	} catch(err) {
		console.log('err', err);
	}
	 
})();
