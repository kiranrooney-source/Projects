let isRecording = false;

document.addEventListener('DOMContentLoaded', function() {
  const recordBtn = document.getElementById('recordBtn');
  const stopBtn = document.getElementById('stopBtn');
  const generateBtn = document.getElementById('generateBtn');
  const status = document.getElementById('status');
  const generateSection = document.getElementById('generateSection');
  const actionsCount = document.getElementById('actionsCount');
  const seleniumCheck = document.getElementById('seleniumCheck');
  const jmeterCheck = document.getElementById('jmeterCheck');
  const fileName = document.getElementById('fileName');

  recordBtn.addEventListener('click', startRecording);
  stopBtn.addEventListener('click', stopRecording);
  generateBtn.addEventListener('click', generateAndDownload);

  // Check current recording state
  chrome.storage.local.get(['isRecording', 'recordedActions'], function(result) {
    if (result.isRecording) {
      recordBtn.style.display = 'none';
      stopBtn.style.display = 'block';
      status.textContent = 'Recording...';
      status.className = 'status recording';
    }
    if (result.recordedActions && result.recordedActions.length > 0) {
      showGenerateSection(result.recordedActions.length);
    }
  });

  function startRecording() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        func: initializeRecording
      }, () => {
        chrome.tabs.sendMessage(tabs[0].id, {action: 'startRecording'});
        chrome.storage.local.set({isRecording: true});
        recordBtn.style.display = 'none';
        stopBtn.style.display = 'block';
        status.textContent = 'Recording...';
        status.className = 'status recording';
      });
    });
  }

  function stopRecording() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.tabs.sendMessage(tabs[0].id, {action: 'stopRecording'}, (response) => {
        chrome.storage.local.set({isRecording: false});
        stopBtn.style.display = 'none';
        recordBtn.style.display = 'block';
        status.textContent = 'Recording stopped';
        status.className = 'status';
        
        if (response && response.actionsCount > 0) {
          showGenerateSection(response.actionsCount);
        }
      });
    });
  }

  function showGenerateSection(count) {
    generateSection.style.display = 'block';
    actionsCount.style.display = 'block';
    actionsCount.textContent = `${count} actions recorded`;
  }

  function generateAndDownload() {
    const filename = fileName.value.trim() || 'recorded_session';
    const generateSelenium = seleniumCheck.checked;
    const generateJMeter = jmeterCheck.checked;
    
    if (!generateSelenium && !generateJMeter) {
      alert('Please select at least one script type to generate');
      return;
    }
    
    chrome.storage.local.get(['recordedActions'], function(result) {
      const actions = result.recordedActions || [];
      
      if (generateSelenium) {
        const seleniumScript = generateSeleniumScript(actions);
        downloadFile(seleniumScript, `${filename}.py`, 'text/python');
      }
      
      if (generateJMeter) {
        const jmeterScript = generateJMeterScript(actions);
        downloadFile(jmeterScript, `${filename}.jmx`, 'application/xml');
      }
    });
  }

  function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function generateSeleniumScript(actions) {
    let script = `from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize driver
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

try:
`;

    actions.forEach((action, index) => {
      switch(action.type) {
        case 'navigate':
          script += `    driver.get("${action.url}")
    time.sleep(2)
`;
          break;
        case 'click':
          if (action.selector) {
            if (action.selector.startsWith('//')) {
              // XPath selector
              script += `    try:
        element_${index} = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "${action.selector}"))
        )
        element_${index}.click()
        time.sleep(1)
    except Exception as e:
        print(f"Could not click element ${index}: {e}")
`;
            } else {
              // CSS selector
              const escapedSelector = action.selector.replace(/"/g, '\\"');
              script += `    try:
        element_${index} = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "${escapedSelector}"))
        )
        element_${index}.click()
        time.sleep(1)
    except Exception as e:
        print(f"Could not click element ${index}: {e}")
`;
            }
          }
          break;
        case 'input':
          if (action.selector && action.value) {
            const escapedValue = action.value.replace(/"/g, '\\"');
            if (action.selector.startsWith('//')) {
              // XPath selector
              script += `    try:
        input_${index} = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "${action.selector}"))
        )
        input_${index}.clear()
        input_${index}.send_keys("${escapedValue}")
        time.sleep(1)
    except Exception as e:
        print(f"Could not input to element ${index}: {e}")
`;
            } else {
              // CSS selector
              const escapedSelector = action.selector.replace(/"/g, '\\"');
              script += `    try:
        input_${index} = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "${escapedSelector}"))
        )
        input_${index}.clear()
        input_${index}.send_keys("${escapedValue}")
        time.sleep(1)
    except Exception as e:
        print(f"Could not input to element ${index}: {e}")
`;
            }
          }
          break;
      }
    });

    script += `
except Exception as e:
    print(f"Script error: {e}")
finally:
    driver.quit()
    print("Test completed")`;
    return script;
  }

  function generateJMeterScript(actions) {
    let script = `<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Recorded Test Plan">
      <elementProp name="TestPlan.arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables"/>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">1</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">1</stringProp>
        <stringProp name="ThreadGroup.ramp_time">1</stringProp>
      </ThreadGroup>
      <hashTree>
`;

    actions.forEach((action, index) => {
      if (action.type === 'navigate' || (action.type === 'click' && action.url)) {
        const url = new URL(action.url || window.location.href);
        script += `        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Request ${index + 1}">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables"/>
          <stringProp name="HTTPSampler.domain">${url.hostname}</stringProp>
          <stringProp name="HTTPSampler.port">${url.port || (url.protocol === 'https:' ? '443' : '80')}</stringProp>
          <stringProp name="HTTPSampler.protocol">${url.protocol.replace(':', '')}</stringProp>
          <stringProp name="HTTPSampler.path">${url.pathname}</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
`;
      }
    });

    script += `      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>`;
    return script;
  }
});

// Function to inject into the page
function initializeRecording() {
  if (window.sessionRecorderInitialized) return;
  window.sessionRecorderInitialized = true;
  
  let isRecording = false;
  let recordedActions = [];

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'startRecording') {
      startRecording();
      sendResponse({success: true});
    } else if (request.action === 'stopRecording') {
      const count = stopRecording();
      sendResponse({success: true, actionsCount: count});
    }
  });

  function startRecording() {
    isRecording = true;
    recordedActions = [];
    
    recordedActions.push({
      type: 'navigate',
      url: window.location.href,
      timestamp: Date.now()
    });

    document.addEventListener('click', handleClick, true);
    document.addEventListener('input', handleInput, true);
    document.addEventListener('change', handleChange, true);
  }

  function stopRecording() {
    isRecording = false;
    
    document.removeEventListener('click', handleClick, true);
    document.removeEventListener('input', handleInput, true);
    document.removeEventListener('change', handleChange, true);
    
    chrome.storage.local.set({recordedActions: recordedActions});
    return recordedActions.length;
  }

  function handleClick(event) {
    if (!isRecording) return;
    
    const element = event.target;
    const selector = generateSelector(element);
    
    recordedActions.push({
      type: 'click',
      selector: selector,
      tagName: element.tagName,
      text: element.textContent?.trim().substring(0, 50),
      href: element.href,
      url: window.location.href,
      timestamp: Date.now()
    });
  }

  function handleInput(event) {
    if (!isRecording) return;
    
    const element = event.target;
    const selector = generateSelector(element);
    
    recordedActions.push({
      type: 'input',
      selector: selector,
      value: element.value,
      tagName: element.tagName,
      inputType: element.type,
      timestamp: Date.now()
    });
  }

  function handleChange(event) {
    if (!isRecording) return;
    
    const element = event.target;
    const selector = generateSelector(element);
    
    recordedActions.push({
      type: 'change',
      selector: selector,
      value: element.value,
      tagName: element.tagName,
      timestamp: Date.now()
    });
  }

  function generateSelector(element) {
    if (element.id && /^[a-zA-Z][\w-]*$/.test(element.id)) {
      return `#${element.id}`;
    }
    
    if (element.name && /^[a-zA-Z][\w-]*$/.test(element.name)) {
      return `[name="${element.name}"]`;
    }
    
    if (element.className && typeof element.className === 'string') {
      const classes = element.className.split(' ').filter(c => c.trim() && /^[a-zA-Z][\w-]*$/.test(c));
      if (classes.length > 0) {
        return `.${classes[0]}`;
      }
    }
    
    // Use XPath for complex cases
    let path = [];
    let current = element;
    
    while (current && current.nodeType === Node.ELEMENT_NODE && current !== document.body) {
      let selector = current.tagName.toLowerCase();
      
      let sibling = current;
      let nth = 1;
      while (sibling = sibling.previousElementSibling) {
        if (sibling.tagName === current.tagName) nth++;
      }
      
      selector += `[${nth}]`;
      path.unshift(selector);
      current = current.parentElement;
    }
    
    return `//${path.join('/')}`;
  }
}