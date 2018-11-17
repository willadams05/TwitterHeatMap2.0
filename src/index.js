//Code from: https://www.youtube.com/watch?v=Zy89Nj7tNNM
//https://stackoverflow.com/questions/16098397/pass-variables-to-javascript-in-expressjs
const express = require('express');
const ejs = require('ejs-mate');
const db_methods = require('./dbMethods');

// Initialization
const app = express();

// Settings
app.engine('ejs', ejs);
app.set('view engine', 'ejs');
app.set('views', __dirname + '/views');

// Routes
data = db_methods("trump");
app.get('/', function(req, res){
    res.render('index.ejs', {
        rows: data
    });
});

// Static Files
app.use(express.static(__dirname+"/public"));

//db_methods("trump");

// Start Server
app.listen(8080, () => {
    console.log("Server on port 8080");
});