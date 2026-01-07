# Mobile Query Automation App

A cross-platform mobile application (iOS & Android) that connects to a server and automates queries based on user requirements.

## Features

- **Cross-Platform**: Works on both iOS and Android devices
- **Server Connection**: Connect to any server endpoint with authentication
- **Windows Authentication**: Automatic login using current Windows user credentials
- **Manual Authentication**: Username/password login with JWT tokens
- **Database Selection**: View and select from available databases
- **Requirement Input**: Enter natural language requirements
- **Automated Queries**: Server processes requirements and generates automated queries
- **Real-time Results**: View query results in the mobile app
- **Secure Storage**: JWT tokens stored securely using Expo SecureStore

## Prerequisites

- Node.js (v14 or higher)
- Expo CLI (`npm install -g @expo/cli`)
- For iOS development: Xcode (macOS only)
- For Android development: Android Studio

## Setup

1. **Install dependencies:**
```bash
cd mobile-query-app
npm install
```

2. **Start the development server:**
```bash
npm start
```

3. **Run on device/simulator:**
```bash
# For iOS (requires macOS)
npm run ios

# For Android
npm run android

# For web browser
npm run web
```

## Usage

### Windows Authentication (Default)
1. **Enter Server URL**: Type server URL (default: http://localhost:5000)
2. **Enable Windows Auth**: Keep "Use Windows Authentication" enabled
3. **Connect**: Tap "Connect" to authenticate automatically
4. **Select Database**: Choose from available databases
5. **Enter Requirements**: Type your requirements in natural language
6. **Execute Query**: Tap "Execute Query" to send requirements to server
7. **View Results**: Automated queries and results appear on the results screen

### Manual Authentication
1. **Disable Windows Auth**: Turn off "Use Windows Authentication"
2. **Enter Credentials**: Server URL, username, and password
3. **Connect**: Tap "Connect" to authenticate manually
4. **Continue**: Follow steps 4-7 above

## Default Credentials

- **admin** / password123
- **user1** / mypass
- **demo** / demo123

## Building for Production

### Android APK
```bash
expo build:android
```

### iOS IPA (requires Apple Developer account)
```bash
expo build:ios
```

## Server Requirements

The mobile app expects the same server API as the desktop version:

- `GET /health` - Health check endpoint
- `POST /auth` - Authenticate user and return JWT token
- `GET /databases` - Get list of available databases (requires auth)
- `POST /query` - Process requirements and return automated queries (requires auth)

## Project Structure

```
mobile-query-app/
├── src/
│   ├── screens/
│   │   ├── LoginScreen.js      # Authentication screen
│   │   ├── HomeScreen.js       # Database selection
│   │   ├── QueryScreen.js      # Requirements input
│   │   └── ResultsScreen.js    # Query results display
│   ├── services/
│   │   └── api.js              # API service for server communication
│   └── components/             # Reusable components
├── App.js                      # Main app component with navigation
├── app.json                    # Expo configuration
├── package.json                # Dependencies and scripts
└── README.md                   # This file
```

## Technologies Used

- **React Native**: Cross-platform mobile development
- **Expo**: Development platform and build tools
- **React Navigation**: Navigation between screens
- **Expo SecureStore**: Secure token storage
- **Fetch API**: HTTP requests to server

## Development Notes

- The app uses React Navigation for screen navigation
- JWT tokens are stored securely using Expo SecureStore
- The UI is designed to be responsive on both iOS and Android
- Error handling is implemented for network requests
- Loading states provide user feedback during operations