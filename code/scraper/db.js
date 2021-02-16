const Sequelize = require('sequelize');

let sequelize = new Sequelize('scraper', 'postgres', '12345', {
	dialect: 'postgres',
	host: 'localhost',
	logging: null
});

let Category = sequelize.define('Category', {
	id: {
		type: Sequelize.UUID,
		defaultValue: Sequelize.UUIDV4,
		primaryKey: true
	},
	title: Sequelize.STRING,
	link: Sequelize.STRING,
	active: {
		type: Sequelize.BOOLEAN
	},
	last_scraped: {
		type: Sequelize.DATE
	}
});

let Conference = sequelize.define('Conference', {
	id: {
		type: Sequelize.UUID,
		defaultValue: Sequelize.UUIDV4,
		primaryKey: true
	},
	acronym: {
		type: Sequelize.STRING,
		unique: true,
		allowNull: false
	},
	link: {
		type: Sequelize.STRING,
		allowNull: false
	},
	original_link: Sequelize.STRING,
	title: Sequelize.TEXT,
	location: Sequelize.STRING,
	duration: Sequelize.STRING,
	submission_deadline: Sequelize.DATE,
	notification_due: Sequelize.DATE,
	finalversion_due: Sequelize.DATE,
	description: Sequelize.TEXT,
	series_link: Sequelize.STRING,
	category_id: Sequelize.UUID,
	export_safe: Sequelize.BOOLEAN
});


sequelize.sync().then(_ => {
	console.log('sync performed successfuly');
}).catch(err => {
	console.log('sync failed');
});

Conference.belongsTo(Category, {foreignKey: 'category_id'});

module.exports = {
	Category,
	Conference,
	Sequelize
}
