chrome.runtime.onInstalled.addListener(() => {
  console.log('Session Recorder extension installed');
});

chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['content.js']
  });
});