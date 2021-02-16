const request = require('request');
const cheerio = require('cheerio');
const colors = require('colors');
const Agent = require('socks5-http-client/lib/Agent');
const newId = require('./new-id');
const Q = require('q');
const fs = require('fs');
const _ = require('lodash');


// calls a request through tor. Once it gets permission denied, will try to get a new identity from tor and try again until succeeds. 
function proxify(method, link, cookie, form) {

    let deferred =  Q.defer();

    let options = {
		resolveWithFullResponse: true,
		uri: link,
		headers: {
			Cookie: cookie,
			'Host': 'wikicfp.com',
			'Accept-Language': 'en-US,en;q=0.5',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Content-Type': 'text/html; charset=utf-8'
		},
		agentClass: Agent,
		agentOptions: {
			socksHost: 'localhost', // Defaults to 'localhost'.
			socksPort: 9050 // Defaults to 1080.
		},
		method: method,
		form: form
    };
	
    Q.spawn(function*() {
		
		let response = yield rp(options);
		
		if (response.statusCode === 200 || response.statusCode === 302)
			deferred.resolve(response);
		else {
			console.log(response.statusCode);
			
			if( response.statusCode === 403) {
				console.log('Permission Denied'.red);
				console.log('Trying to get a new ID'.bold.green);
				yield newId();
			}
			
			yield sleep(3000);
			deferred.resolve((yield proxify(method, link, cookie)));
		}
    });
    
    return deferred.promise;
}

// wrap request, instead of using request-promise which doesn't work with proxy configs to use tor
function rp(options) {
    return new Promise((resolve, reject) => {
		request(options, function(err, response) {
			if(err)
				reject(err);
			else if (response)
				resolve(response);
		});
    });
}
 
function sleep(time_ms) {
    return Q.promise(resolve => {
		console.log('Sleeping for',  time_ms.toString().cyan , 'mseconds');
		setTimeout(_ => resolve(), time_ms);
    });
}

module.exports = {
	proxify,
	sleep
}
