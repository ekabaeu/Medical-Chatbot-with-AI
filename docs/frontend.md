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
- Responsive design for various screen sizes with mobile-first approach
- Markdown support for rich text responses with HTML sanitization
- Automatic chat history saving
- Session management with auto-generated unique identifiers
- Modern UI with gradient-based design and smooth animations
- Mobile-friendly layout with hamburger menu navigation
- Error handling for API communication failures
- Patient data extraction from response headers

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
- Gradient background with radial pattern
- Responsive font sizing with clamp function
- Smooth font rendering with antialiasing
- Padding for mobile responsiveness

#### Chat Container
- Fixed width and height with max constraints
- Rounded corners and shadow effects
- Flexbox layout for dynamic resizing
- Background with subtle radial pattern

#### Message Styling
- Different styles for user and bot messages with gradient backgrounds
- Rounded corners with directional styling (speech bubble effect)
- Proper alignment (right for user, left for bot)
- Smooth fade-in animations
- Word wrapping for long messages

#### Input Area
- Flex layout for input field and send button
- Styled input field with focus effects and transitions
- Circular send button with hover effects and scaling animations
- Gap spacing for better visual separation
- Shadow effects for depth

#### Responsive Design
- Media queries for different screen sizes
- Mobile-first approach with progressive enhancement
- Hamburger menu for mobile navigation
- Flexible grid container for content organization
- Scalable text with CSS clamp function

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
- `sendMessageFromInput()`: Handles user input submission and session initialization
- `processUserMessage()`: Processes and displays user messages with timestamp
- `getBotResponse()`: Communicates with backend API and handles streaming responses with real-time UI updates
- `displayMessage()`: Renders messages in the chat interface with markdown support

#### Auto-save Functionality
```javascript
async function autoSaveChat()
```
- Automatically saves chat history after each interaction
- Sends data to `/save-chat` endpoint with error handling
- Includes patient data with each save
- Uses fetch API with JSON payload

#### Markdown Processing
```javascript
function convertMarkdownToHTML(text)
```
- Uses Marked.js for markdown parsing with GFM (GitHub Flavored Markdown) support
- Uses DOMPurify for HTML sanitization to prevent XSS attacks
- Ensures safe rendering of markdown content
- Configured for proper line breaks and formatting

#### Event Listeners
```javascript
sendButton.addEventListener('click', sendMessageFromInput);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessageFromInput();
});
```
- Click event for send button
- Enter key support for message submission
- Prevents empty message submissions
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
- Uses Fetch API for modern HTTP requests
- JSON payload with chat history
- Error handling with try/catch blocks

#### Streaming Response Handling
- Uses `response.body.getReader()` for streaming
- Processes chunks in real-time with TextDecoder
- Updates UI as data arrives for better user experience
- Maintains connection until stream is complete
- Handles connection errors gracefully

#### Header Data Extraction
```javascript
const patientHeader = response.headers.get('X-Patient-Data');
```
- Extracts patient data from response headers
- Updates local patient data state
- JSON parsing with error handling
- Conditional updates based on available data

## User Interface Components

### Chat Header
- Displays application title "Medical Chat Assistant"
- Fixed at top of interface
- Green gradient color scheme for medical theme
- Box shadow for depth effect
- Responsive padding and font sizing

### Chat Box
- Scrollable message container with custom scrollbar
- Dynamically adds messages with fade-in animation
- Auto-scrolls to bottom on new messages
- Background with subtle radial pattern for visual interest
- Flexbox layout for message alignment

### Message Elements
- **User Messages**: Green gradient bubbles aligned to right with speech bubble styling
- **Bot Messages**: Light gray gradient bubbles aligned to left with speech bubble styling
- **Styling**: Rounded corners, padding, proper typography, and box shadows
- **Markdown Support**: Rich text formatting with safe HTML rendering
- **Animations**: Smooth fade-in effect for new messages

### Input Area
- Text input field with placeholder "Ketik Nama, Umur, Gender, dan Keluhan Awal Anda..."
- Send button with arrow icon and hover effects
- Enter key support for message submission
- Focus effects with green border and box shadow
- Responsive design with gap spacing
- Minimum height constraints for touch targets

## Data Flow

### Message Sending Flow
1. User types message and clicks send or presses Enter
2. Message validated to prevent empty submissions
3. Session ID generated on first message if not already present
4. Message added to chat history with timestamp
5. Displayed in chat box immediately with user styling
6. Request sent to `/chat` endpoint with JSON payload
7. User input field cleared and focused

### Response Receiving Flow
1. Streaming response from backend via Fetch API
2. Chunks processed as they arrive using TextDecoder
3. Bot message updated in real-time with markdown rendering
4. Chat box auto-scrolls to show new content
5. Patient data extracted from response headers if available
6. Final message saved to chat history
7. UI updated with smooth animations

### Auto-save Flow
1. After bot response received and displayed
2. `autoSaveChat()` function triggered automatically
3. Current chat history and patient data sent to `/save-chat`
4. JSON payload with session ID and all conversation data
5. Success/failure handled silently with error logging
6. No user interruption during save process

### Session Management
1. Session ID generated on first message using timestamp
2. Maintained throughout conversation in memory
3. Included in all save operations for data association
4. Used to associate chat history with patient data
5. Preserved during page reloads (in future enhancements)

### Patient Data Handling
1. Extracted from response headers after first message
2. Stored in `patientData` object with name and age
3. Included in auto-save requests for data persistence
4. Updated as more information becomes available from backend
5. Used for personalizing future interactions
6. Protected against XSS with JSON parsing and validation