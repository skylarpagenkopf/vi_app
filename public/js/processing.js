var cv = require('opencv');

exports.process = function(imagePath) {
	// handle image processing and matching here
	cv.readImage(imagePath, function(err, im){
		// find human in picture
		// compare to outfit images
	});
};