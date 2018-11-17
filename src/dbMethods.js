const SQL = require('sql.js');
const fs = require('fs');

var filebuffer = fs.readFileSync("./test.db");
var db = new SQL.Database(filebuffer);

function load_all(tablename){
    var temp = db.exec('SELECT * FROM ' + tablename + ';');
    var records = temp[0].values;
    var length = records.length;
    for (var i = 0; i < length; i++){
        id = records[i][0];
        text = records[i][1];
        date = records[i][2];
        long = records[i][3];
        lat = records[i][4];
        sent = records[i][5];
        console.log(long + " " + lat + " " + sent);
    }
    return records;
}

module.exports = load_all;