const WebSocket = require('ws');

const url = 'ws://localhost:8000/ws';
console.log(`Attempting to connect to ${url}...`);

const ws = new WebSocket(url);

ws.on('open', () => {
    console.log('✓ WebSocket connection opened');
    console.log('Sending ping...');
    ws.send(JSON.stringify({ type: 'ping', payload: {} }));
    
    // Test message
    setTimeout(() => {
        console.log('Sending test message...');
        ws.send(JSON.stringify({ 
            type: 'message', 
            payload: { content: 'Hello from Node.js test', session_id: 'test-session' } 
        }));
    }, 1000);
    
    // Close after 3 seconds
    setTimeout(() => {
        console.log('Closing connection...');
        ws.close();
    }, 3000);
});

ws.on('message', (data) => {
    console.log('✓ Received message:', data);
});

ws.on('close', (code, reason) => {
    console.log('✗ WebSocket connection closed:', code, reason.toString());
});

ws.on('error', (error) => {
    console.error('✗ WebSocket error:', error);
});