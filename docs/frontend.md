# Frontend Documentation

This document provides detailed information about the frontend components of the Medical Chatbot application.

## Table of Contents

- [Frontend Architecture](#frontend-architecture)
- [HTML Structure (index.html)](#html-structure-indexhtml)
- [Styling (style.css)](#styling-stylecss)
- [JavaScript Functionality (script.js)](#javascript-functionality-scriptjs)
- [User Interface Components](#user-interface-components)
- [Data Flow](#data-flow)

## Frontend Architecture

The frontend is a single-page application built with vanilla HTML, CSS, and JavaScript. It features a real-time chat interface that communicates with the backend API.

### Key Features

- Real-time chat interface with message streaming
- Responsive design for various screen sizes
- Markdown support for rich text responses
- Automatic chat history saving
- Session management

## HTML Structure (index.html)

The main HTML file that defines the structure of the chat interface.

### Key Elements

#### Document Head
```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical Chatbot</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
    <link rel="stylesheet" href="style.css">
</head>
```

#### Chat Container
```html
<div id="chat-container">
    <div id="chat-header">
        <span>Medical Chat Assistant</span>
    </div>
    
    <div id="chat-box">
        <!-- Messages will be dynamically added here -->
    </div>
    
    <div id="input-area">
        <input type="text" id="user-input" placeholder="Ketik Nama, Umur, Gender, dan Keluhan Awal Anda...">
        <button id="send-button">➤</button>
    </div>
</div>
```

#### Script Loading
```html
<script src="script.js" defer></script>
```

## Styling (style.css)

CSS file that provides responsive styling for the chat interface.

### Key Styling Components

#### Global Reset
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```

#### Body Styling
- Centered layout with flexbox
- Background color and font settings
- Responsive font sizing

#### Chat Container
- Fixed width and height with max constraints
- Rounded corners and shadow effects
- Flexbox layout for dynamic resizing

#### Message Styling
- Different styles for user and bot messages
- Rounded corners with directional styling
- Proper alignment (right for user, left for bot)

#### Input Area
- Flex layout for input field and send button
- Styled input field with focus effects
- Circular send button with hover effects

## JavaScript Functionality (script.js)

JavaScript file that handles all frontend logic and API communication.

### Global Variables

```javascript
const BACKEND_URL = window.location.origin;
let chatHistory = [];
let sessionId = null;
let patientData = { name: 'unknown', age: 'unknown' };
```

### Key Functions

#### Message Handling
- `sendMessageFromInput()`: Handles user input submission
- `processUserMessage()`: Processes and displays user messages
- `getBotResponse()`: Communicates with backend API and handles streaming responses
- `displayMessage()`: Renders messages in the chat interface

#### Auto-save Functionality
```javascript
async function autoSaveChat()
```
- Automatically saves chat history after each interaction
- Sends data to `/save-chat` endpoint
- Includes patient data with each save

#### Markdown Processing
```javascript
function convertMarkdownToHTML(text)
```
- Uses Marked.js for markdown parsing
- Uses DOMPurify for HTML sanitization
- Ensures safe rendering of markdown content

#### Event Listeners
```javascript
sendButton.addEventListener('click', sendMessageFromInput);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessageFromInput();
});
```

### API Communication

#### Chat Endpoint
```javascript
const response = await fetch(`${BACKEND_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ history: chatHistory })
});
```

#### Streaming Response Handling
- Uses `response.body.getReader()` for streaming
- Processes chunks in real-time
- Updates UI as data arrives

#### Header Data Extraction
```javascript
const patientHeader = response.headers.get('X-Patient-Data');
```
- Extracts patient data from response headers
- Updates local patient data state

## User Interface Components

### Chat Header
- Displays application title
- Fixed at top of interface
- Green color scheme for medical theme

### Chat Box
- Scrollable message container
- Dynamically adds messages
- Auto-scrolls to bottom on new messages

### Message Elements
- **User Messages**: Green bubbles aligned to right
- **Bot Messages**: Gray bubbles aligned to left
- **Styling**: Rounded corners, padding, and proper typography

### Input Area
- Text input field with placeholder
- Send button with arrow icon
- Enter key support for message submission

## Data Flow

### Message Sending Flow
1. User types message and clicks send or presses Enter
2. Message added to chat history
3. Displayed in chat box immediately
4. Request sent to `/chat` endpoint
5. User input field cleared

### Response Receiving Flow
1. Streaming response from backend
2. Chunks processed as they arrive
3. Bot message updated in real-time
4. Chat box auto-scrolls to show new content
5. Final message saved to chat history

### Auto-save Flow
1. After bot response received
2. `autoSaveChat()` function triggered
3. Current chat history and patient data sent to `/save-chat`
4. Success/failure handled silently

### Session Management
1. Session ID generated on first message
2. Maintained throughout conversation
3. Included in all save operations
4. Used to associate chat history with patient data

### Patient Data Handling
1. Extracted from response headers after first message
2. Stored in `patientData` object
3. Included in auto-save requests
4. Updated as more information becomes available