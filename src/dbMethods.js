const SQL = require('sql.js');
const fs = require('fs');

var filebuffer = fs.readFileSync("./data/tweetDB.db");
var db = new SQL.Database(filebuffer);

function load_all(tablename){
    var temp = db.exec('SELECT * FROM ' + tablename + ';');
    var records = temp[0].values;
    return records;
}

module.exports = load_all;