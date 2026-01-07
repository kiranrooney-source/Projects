# Session Recorder Chrome Extension

A Chrome extension that records user interactions and generates Selenium Python and JMeter scripts.

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right corner
3. Click "Load unpacked" button
4. Select the `chrome-extension` folder
5. The extension will appear in your extensions list

## Usage

1. Click the extension icon in the Chrome toolbar
2. Click "Start Recording" to begin capturing interactions
3. Perform actions on the webpage (clicks, form inputs, navigation)
4. Click "Stop Recording" when finished
5. Choose "Generate Selenium Script" or "Generate JMeter Script"
6. Copy the generated script from the text area

## Features

- Records clicks, form inputs, and page navigation
- Generates robust CSS selectors for elements
- Creates ready-to-run Selenium Python scripts
- Generates JMeter test plans in XML format
- Handles dynamic content and multiple element selection strategies

## Generated Scripts

### Selenium Python
- Uses WebDriverWait for reliable element detection
- Includes proper imports and setup
- Adds timing delays for stability
- Handles form inputs and clicks

### JMeter
- Creates complete test plan XML
- Configures HTTP samplers for requests
- Sets up thread groups and loop controllers
- Ready to import into JMeter

## Troubleshooting

- Ensure the extension has permissions for the target website
- Refresh the page if recording doesn't start
- Check browser console for any error messages
- Verify Chrome developer mode is enabled