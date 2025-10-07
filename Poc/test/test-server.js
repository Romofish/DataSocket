const http = require('http');

const port = 5176; // Using a completely new, unused port
const host = '127.0.0.1';

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello World!\n');
});

server.on('error', (err) => {
  console.error(`❌ Server Error:`, err);
});

server.listen(port, host, () => {
  console.log(`✅ Server is running successfully at http://${host}:${port}/`);
});