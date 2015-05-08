var express = require('express');
var fs = require('fs');
var path = require('path');
// var processing = require('../public/js/processing.js');
var appDir = path.dirname(require.main.filename);
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

// get home page where user can upload or select example image
router.get('/', function(req, res) {
	res.render('index', { title: 'Home' });
});

// post user selected image, get results and display
router.post('/results', function(req, res) {
	var results = [],
		filePath,
		relPath,
		detailsPath;
	// upload file to temp folder
	fs.readFile(req.files.inputFile.path, function (err, data) {
		filePath = appDir + '/public/images/temp/' + req.files.inputFile.name;
		relPath = 'images/temp/' + req.files.inputFile.name,
		details = req.files.inputFile.name.split('.'),
		detailsPath = 'images/temp/' + details[0] + 'details.' + details[1];
		fs.writeFile(filePath, data, function (err) {
			// do image processing
			var python = require('child_process').spawn('python',
			     // second argument is array of parameters, e.g.:
			     [appDir + '/public/python/processing.py'
			     , filePath
			     , appDir]
		     );
		     var output = '';
		     python.stdout.on('data', function(data) { output += data });
		     python.on('close', function(code){ 
		     	results = JSON.parse(output);
		     	// render page
				res.render('results', { 
					title: 'Results',
					relPath: relPath,
					detailsPath: detailsPath,
					results: results
				});
		     });
		});
	});
});

// remove temp image after processing so we don't have a million images in our app
router.get('/remove/:image', function (req, res) {
	var filePath = appDir + '/public/images/temp/' + req.params.image,
		details = req.params.image.split('.'),
		detailsPath = appDir + '/public/images/temp/' + details[0] + 'details.' + details[1];
	fs.unlinkSync(filePath);
	fs.unlinkSync(detailsPath);
});

// get example image results
router.get('/results/:filename', function(req, res) {
	// use image specified in filename param
	var filePath = appDir + '/public/images/' + req.params.filename + '.jpg',
		relPath = '../images/' + req.params.filename + '.jpg',
		detailsPath = '../images/' + req.params.filename + 'details.jpg',
		results = [];
	// do image processing
	var python = require('child_process').spawn('python',
	     // second argument is array of parameters, e.g.:
	     [appDir + '/public/python/processing.py'
	     , filePath
	     , appDir]
     );
     var output = '';
     python.stdout.on('data', function(data) { output += data });
     python.on('close', function(code){ 
     	results = JSON.parse(output);
     	// render page
		res.render('results', { 
			title: 'Results',
			relPath: relPath,
			detailsPath: detailsPath,
			results: results
		});
     });
});

module.exports = router;
