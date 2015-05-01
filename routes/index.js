var express = require('express');
var router = express.Router();

// if we need db umncomment this
// // connect to db to get info for page rendering
// var mongo = require('mongodb');
// var mongoose = require('mongoose');
// var ObjectID = mongo.ObjectID;
// var db;

// // connects to db
// mongo.MongoClient.connect('mongodb://localhost:27017/vi', function(err, database) {
// 	if (err) throw err;
// 	db = database;
// });

// get home page and list groups
router.get('/', function(req, res) {
	res.render('index', { title: 'Home' });
});

router.get('/results', function(req, res) {
	res.render('results', { title: 'Results' });
});

module.exports = router;
