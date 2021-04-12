const Q = require('q');
const spawn = require('child_process').spawn;

function shspawn(command) {
    let child = spawn('sh', ['-c', command]);
} 

module.exports = function() {
    return Q.promise((resolve, reject) => {
	shspawn('pidof tor | xargs sudo kill -HUP');
	resolve();
    });
}
