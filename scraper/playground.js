const db = require('./db');


(async function() {

	let results = await db.Conference.update({export_safe: true},{where:{acronym: {$regexp: '[a-zA-Z]( )?[0-9]+'}} });
	// let results = await db.Conference.findAll();
	// results.forEach(async (x) => {
	// 	x.export_safe = true;
	// 	await x.save();
	// 	console.log(x.id, x.acronym);
	// });
})();
