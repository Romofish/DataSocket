// test-listen.js
const http = require('http');

const server = http.createServer((req, res) => {
  res.end('Hello');
});

server.listen(5173, '127.0.0.1', () => {
  console.log('Listening on 127.0.0.1:5173');
});
