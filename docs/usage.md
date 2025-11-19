# Usage Guide

This document provides detailed instructions on how to use the Medical Chatbot application effectively.

## Table of Contents

- [Getting Started](#getting-started)
- [Initial Consultation Process](#initial-consultation-process)
- [Three-Stage Diagnostic System](#three-stage-diagnostic-system)
- [Patient Information Format](#patient-information-format)
- [Chat Interface Navigation](#chat-interface-navigation)
- [Special Features](#special-features)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Getting Started

### Accessing the Application

1. Open your web browser
2. Navigate to the application URL (provided by your administrator or deployment)
3. The chat interface will load automatically

### First-Time Use

1. Ensure your internet connection is stable
2. Familiarize yourself with the chat interface
3. Prepare to provide your medical information in the correct format

## Initial Consultation Process

### Starting a New Session

1. Locate the input field at the bottom of the chat interface
2. Enter your information in the required format:
   ```
   [Name] [Age] [Gender] [Initial Complaint]
   ```
3. Example:
   ```
   John 25 male I have a headache and fever
   ```
4. Press Enter or click the send button (➤)

### Information Format Details

- **Name**: Your first name (will be extracted automatically)
- **Age**: Your age in years followed by "tahun" or "thn"
- **Gender**: "male"/"laki-laki" or "female"/"perempuan"
- **Initial Complaint**: Describe your main medical concern clearly

## Three-Stage Diagnostic System

The Medical Chatbot follows a structured three-stage approach to provide comprehensive medical assistance.

### Stage 1: Information Collection

**What happens:**
- The system acknowledges your initial complaint
- Automatically extracts your basic information
- Generates a unique patient ID
- Asks exactly 3 targeted diagnostic questions

**Your role:**
- Answer the 3 questions honestly and completely
- Provide specific details about your symptoms
- Example responses:
  - "The pain is located in my lower back and started 3 days ago"
  - "I've had a fever between 38-39°C for the past 2 days"

### Stage 2: Symptom Analysis

**What happens:**
- The system analyzes all provided information
- Generates a comprehensive medical assessment
- Identifies possible causes for your symptoms
- Provides specific recommendations

**What you'll receive:**
- Detailed medical analysis
- List of possible conditions with explanations
- Clear recommendations for treatment or next steps
- Advice on when to seek immediate medical attention

### Stage 3: Follow-up Conversation

**What happens:**
- Natural conversation mode is activated
- You can ask additional medical questions
- The system provides concise, relevant responses

**Your role:**
- Ask specific follow-up questions about your condition
- Request clarification on previous recommendations
- Inquire about treatment options or medications
- Example questions:
  - "What over-the-counter medications can I take?"
  - "Should I be concerned about these symptoms?"

## Patient Information Format

### Required Information Format

When starting a conversation, provide information in this exact format:
```
[Name] [Age] [Gender] [Initial Complaint]
```

### Examples

**Correct Format:**
```
Sarah, 32 tahun, perempuan, sakit perut
```

**Correct Format:**
```
Michael, 45 tahun, laki-laki, sakit kepala
```

### Format Guidelines

1. **Name**: Use your first name only
2. **Age**: Number followed by "tahun" or "thn" (e.g., "25 tahun" or "25 thn")
3. **Gender**: Use "male/laki-laki" or "female/perempuan"
4. **Initial Complaint**: Be as descriptive as possible about your main concern

## Chat Interface Navigation

### Main Components

#### Chat Header
- Displays "Medical Chat Assistant"
- Remains fixed at the top of the interface

#### Message Area
- Shows conversation history
- User messages appear on the right (green bubbles)
- Bot responses appear on the left (gray bubbles)
- Auto-scrolls to show latest messages

#### Input Area
- Text input field for typing messages
- Send button (➤) to submit messages
- Supports Enter key for submission

### Message Features

#### User Messages
- Right-aligned green bubbles
- Display exactly what you typed
- Timestamp not shown but recorded in history

#### Bot Messages
- Left-aligned gray bubbles
- Support markdown formatting:
  - **Bold text** for emphasis
  - *Italic text* for additional information
  - Bullet points for lists
  - Line breaks for readability

### Special Interactions

#### Real-time Streaming
- Bot responses appear character by character
- Provides immediate feedback during processing
- Indicates the system is actively working

#### Auto-save Functionality
- Conversations automatically save after each interaction
- No manual save required
- Session data persists between interactions

## Special Features

### Non-medical Query Handling

The system is designed to focus exclusively on medical topics. If you ask non-medical questions:

**Restricted Topics:**
- Mathematics ("1+1", calculations)
- Weather inquiries
- Historical questions
- Political questions
- General knowledge ("siapa kamu")

**Response to Non-medical Queries:**
```
"Maaf, saya hanya dapat memproses pertanyaan terkait kesehatan."
```

### Patient Data Access

You can retrieve your own patient information during a session:

**How to Access:**
1. Type "cek [your-patient-id]" in the chat
2. Example: "cek A1B2C"

**What You'll See:**
- Your patient ID
- Name
- Age
- Gender
- Initial complaint

### Markdown Support

Bot responses support markdown formatting for better readability:

- **Bold text** for important terms
- *Italic text* for emphasis
- Bullet point lists for recommendations
- Line breaks for clear sections

## Troubleshooting

### Common Issues and Solutions

#### No Response from Bot
1. Check your internet connection
2. Refresh the page
3. Verify the backend service is running
4. Check browser console for errors (F12)

#### Error Messages
- **"Maaf, terjadi kesalahan"**: Backend service issue
  - Solution: Try again in a few minutes
  - If persistent: Contact system administrator

#### Input Not Recognized
- Ensure proper format: [Name] [Age] [Gender] [Complaint]
- Check for typos in age or gender specifications
- Use clear, descriptive language for complaints

#### Slow Response Times
- First response may be slower due to cold start
- Subsequent responses should be faster
- Check internet connection speed

### Browser Compatibility

**Supported Browsers:**
- Chrome (latest version)
- Firefox (latest version)
- Safari (latest version)
- Edge (latest version)

**Mobile Support:**
- Responsive design works on mobile devices
- Touch-friendly interface elements
- Optimized for both portrait and landscape modes

### Error Handling

#### Connection Errors
- System automatically displays error messages
- Provides guidance on next steps
- Maintains chat history locally

#### Processing Errors
- Detailed error messages in browser console
- Graceful degradation of functionality
- Option to retry failed operations

## Best Practices

### For Optimal Results

1. **Be Specific**: Provide detailed descriptions of symptoms
2. **Be Honest**: Accurate information leads to better analysis
3. **Be Complete**: Answer all diagnostic questions thoroughly
4. **Be Patient**: Allow time for comprehensive analysis

### Information Security

1. **Confidentiality**: 
   - Only share information you're comfortable providing
   - Understand that data is stored in the database
   - Review privacy policies of your deployment

2. **Data Handling**:
   - Patient data is automatically saved
   - Session information is associated with your chat
   - No personal identification beyond what you provide

### Medical Advice Limitations

**Important Disclaimers:**
- This system provides preliminary assistance only
- Not a substitute for professional medical consultation
- Emergency situations require immediate professional help
- Always consult healthcare providers for serious conditions

### When to Seek Immediate Help

Contact emergency services or visit a hospital immediately if you experience:
- Chest pain with difficulty breathing
- Severe allergic reactions
- High fever with severe symptoms
- Any life-threatening conditions

### Follow-up Actions

After using the chatbot:
1. Review all recommendations carefully
2. Follow suggested next steps
3. Keep a record of your conversation
4. Consult a healthcare provider for persistent issues
5. Bring chat history to medical appointments if needed

## Additional Resources

### For Administrators
- Refer to deployment documentation for setup
- Check configuration guides for customization
- Review backend documentation for maintenance

### For Developers
- Review backend and frontend documentation
- Check API documentation for integration details
- Refer to deployment guides for scaling information

### For Users
- Contact your system administrator for support
- Report any issues or feedback through proper channels
- Suggest improvements to enhance the service