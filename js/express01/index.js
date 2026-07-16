let express = require("express"),
http = require("http"),
app = express();

app.set("port", process.env.PORT || 3000);
app.get("/heartbeat",
    function(req, res) {
  res.status(200).json( 'OK')
    })
http.createServer(app).listen(
    app.get('port'));
module.exports = app;