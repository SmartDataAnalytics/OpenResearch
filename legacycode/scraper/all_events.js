const rp = require('request-promise');
const cheerio = require('cheerio');
const colors = require('colors');
const fs = require('fs');
const utils = require('./utils');
const _ = require('lodash');
const db = require('./db');

const baseUrl =  'http://www.wikicfp.com';


let link = baseUrl + '/cfp/call?conference=computer science';

(async function() {

	let categories = await db.Category.findAll();
	for(let i = 0; i < categories.length; i++) {
		let x = categories[i];
		try {
			console.log('scraping', x.title);
			await getCategory(x);
			x.last_scraped = new Date();
			await x.save();
		}
		catch(err) {
			console.log(err);
		}
		finally {
			await utils.sleep(5000);			
		}
	}
})();

async function getCategory(cat) {

	return new Promise(async (resolve, reject) => {
		
		let currentPage = 1;
		let totalPages = 1;

		while(currentPage <= totalPages && currentPage < 21) {
			try {
				totalPages = await parsePage(cat.link + '&page=' + currentPage, currentPage, cat);
			} catch(err) {
				console.log(err);
				reject();
			}
			currentPage += 1;
		}
		
		resolve();
	});
}


async function parsePage(link, curPage, cat) {
	return new Promise(async (resolve, reject) => {
		console.log('page #', curPage);
		let html = await utils.proxify('GET', link, null, null);
		const $ = cheerio.load(html.body);
		console.log('loaded successfuly'.cyan);

		console.log('page', curPage);

		// number of total pages 
		let totalPages = $('tr:nth-child(4) tr td:nth-child(2)').text().trim();
		totalPages = totalPages.match(/\d+/g)[1];

		// all of the links -- except for the very 3 last links which are 'last', 'first', 'current' links
		let misc =  $('tr~ tr+ tr a');
		let count = misc.length - 3;
		if (curPage > 1)
			count--;

		// create the conference objects
		let keys = _.times(count, String);
		let links = [];

		keys.forEach(event => {
			links.push({acronym: $(misc[event]).text(), link: baseUrl + $(misc[event]).attr('href')});
			console.log($(misc[event]).text());
		});


		// save them in the db
		for (let i = 0; i < links.length; i++) {
			try {
				links[i].category_id = cat.id;
				await db.Conference.create(links[i]);
			} catch(e) {
			}
		}
		
		resolve(totalPages);
	});



}
