
const cheerio = require('cheerio');
const colors = require('colors');
const utils = require('./utils');
const _ = require('lodash');
const db = require('./db');

const html2String = require('html-to-text');

(async function() {

	while(true) {

		let conferences = await db.Conference.findAll({
			where: {
				submission_deadline: {
					$not: null
				},
				original_link: null
			},
			order: [
				['submission_deadline', 'DESC']
			], limit: 1000
		});

		console.log('confences', conferences.length);


		for (let i = 0; i < conferences.length; i++) {
			let conference = conferences[i];

			try {
				let data = await scrape_one_event(conference.link);
				Object.assign(conference, data);
				await conference.save();
				console.log('conference', conference.acronym);
			} catch(err) {
				console.log(err);
				// ignore, carry on..
			}
		}
		
		// await utils.sleep(3000);
	}
	
})();

// (async function() {
// 	let data = await scrape_one_event('http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=64989&copyownerid=100138');
// })();

async function scrape_one_event(link) {

	return new Promise(async (resolve, reject) => {
		try { 
			let html = await utils.proxify('GET', link, null, null);
			const $ = cheerio.load(html.body);

			let conference = {
				title: $('h2 span').text().trim(),
				duration: $('.gglu tr:nth-child(1) th+ td').text().trim(),
				location: $('tr:nth-child(2) th+ td').text().trim(),
				description: $('td .cfp').html().trim(),
				series_link: $('tr~ tr+ tr a').attr('href'),
				original_link: $('center tr~ tr+ tr a').attr('href')
			};

			if (conference.description) {
				conference.description = html2String.fromString(conference.description, {wordWrap: 130});
			}
			
			try {
				conference.submission_deadline =  safe_copy_date($('tr:nth-child(3) span').text());
				conference.notification_due = safe_copy_date($('tr:nth-child(4) span').text());
				conference.finalversion_due =  safe_copy_date($('tr:nth-child(5) span').text());
			} catch(err) {
				// ignore
			}
			
			resolve(conference);
			
		} catch(err) {
			reject(err);
		}
	});
}

function safe_copy_date(value) {

	if (value) {
		try {
			return new Date(value.trim().split('\n')[0]);
		}catch(err) {
			return null;
		}
	}
	
}

