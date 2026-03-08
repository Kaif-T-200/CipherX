// Backend State
let activeTab = 'operations';
let currentRecipe = [];

// =========================
// TOOLTIP FUNCTIONALITY
// =========================
let currentTooltip = null;

function getHoverOperationInfo(mode, method) {
    const info = {
        decode: {
            base64: 'Decodes Base64 text back into original readable content.',
            base32: 'Decodes Base32 input into its original text form.',
            hex: 'Converts hexadecimal pairs into readable text bytes.',
            binary: 'Converts binary 0/1 bit groups back into characters.',
            url: 'Decodes percent-encoded URL text (for example, %20 to space).',
            rot13: 'Applies ROT13 to reveal readable text from ROT13 input.',
            caesar: 'Attempts Caesar shift reversal to recover plaintext.',
            atbash: 'Applies Atbash mirror substitution to reveal original text.',
            morse: 'Translates Morse dots and dashes into letters, numbers, and words.',
            jwt: 'Decodes JWT parts to inspect header and payload data.',
            unicode: 'Converts Unicode escape sequences into normal characters.',
            reverse: 'Reverses text to recover original forward string.',
            xor: 'Applies XOR decryption using key-based transformation.'
        },
        encode: {
            base64: 'Encodes text into Base64 for safe transport and storage.',
            base32: 'Encodes input into Base32 using A-Z and 2-7 symbols.',
            hex: 'Encodes text bytes into hexadecimal representation.',
            binary: 'Encodes text into binary bit sequences.',
            url: 'Encodes special characters for safe URLs and query strings.',
            rot13: 'Applies ROT13 substitution to obfuscate text.',
            caesar: 'Shifts letters by a fixed amount to encode plaintext.',
            atbash: 'Applies Atbash mirror substitution to transform plaintext.',
            morse: 'Converts letters and numbers into Morse code symbols.',
            reverse: 'Reverses character order for simple obfuscation.',
            xor: 'Applies XOR encoding using a key-based transformation.'
        }
    };

    return info[mode]?.[method] || 'Applies the selected operation to transform your text.';
}

function setModeSpecificHoverInfo() {
    const operationButtons = document.querySelectorAll('.op-btn');

    operationButtons.forEach(button => {
        const clickHandler = button.getAttribute('onclick') || '';
        const mode = clickHandler.includes('encodeOperation(') ? 'encode' : 'decode';
        const methodMatch = clickHandler.match(/\('(.*?)'\)/);
        const method = methodMatch ? methodMatch[1] : null;

        if (method) {
            button.setAttribute('data-tooltip', getHoverOperationInfo(mode, method));
        }
    });
}

function initializeTooltips() {
    const buttons = document.querySelectorAll('[data-tooltip]');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', function () {
            if (currentTooltip && currentTooltip !== this) {
                hideTooltip(currentTooltip);
            }
            showTooltip(this);
            currentTooltip = this;
        });
    });

    document.addEventListener('mouseover', function (e) {
        if (!e.target.closest('[data-tooltip]') && currentTooltip) {
            hideTooltip(currentTooltip);
            currentTooltip = null;
        }
    });
}

function showTooltip(button) {
    const tooltip = button._tooltip;
    if (!tooltip) return;

    tooltip.style.opacity = '1';
    tooltip.style.visibility = 'visible';

    const rect = button.getBoundingClientRect();
    tooltip.style.left = `${rect.right + 10}px`;
    tooltip.style.top = `${rect.top + rect.height / 2}px`;
    tooltip.style.transform = 'translateY(-50%)';
}

function hideTooltip(button) {
    const tooltip = button._tooltip;
    if (!tooltip) return;

    tooltip.style.opacity = '0';
    tooltip.style.visibility = 'hidden';
}

function createTooltipElements() {
    const buttons = document.querySelectorAll('[data-tooltip]');

    buttons.forEach(button => {
        const existingTooltip = button._tooltip;
        if (existingTooltip) {
            existingTooltip.remove();
        }

        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip-content';
        tooltip.textContent = button.getAttribute('data-tooltip');
        tooltip.style.cssText = `
            position: fixed;
            background: var(--primary-color);
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.85em;
            width: 280px;
            white-space: normal;
            z-index: 10000;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s, visibility 0.2s;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            line-height: 1.4;
            pointer-events: none;
            word-wrap: break-word;
            overflow-wrap: break-word;
        `;

        button._tooltip = tooltip;
        document.body.appendChild(tooltip);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    setModeSpecificHoverInfo();
    createTooltipElements();
    initializeTooltips();
});

// API base URL (supports custom backend via ?api=...; defaults to current origin)
const API_BASE = new URLSearchParams(window.location.search).get('api') || window.location.origin;

// Update stats on input
document.getElementById('inputText').addEventListener('input', function () {
    const text = this.value;
    document.getElementById('inputStats').textContent = `Length: ${text.length} | Lines: ${text.split('\n').length}`;
});

document.getElementById('outputText').addEventListener('input', function () {
    const text = this.value;
    document.getElementById('outputStats').textContent = `Length: ${text.length} | Lines: ${text.split('\n').length}`;
});

// Auto Decode with AI
async function autoDecode() {
    const text = document.getElementById("inputText").value;
    const resultsDiv = document.getElementById("results");
    const outputText = document.getElementById("outputText");
    const isDeep = document.getElementById("deepAnalysis")?.checked || false;

    if (!text.trim()) {
        resultsDiv.innerHTML = "<p style='color: red;'>Please enter some text to decode!</p>";
        return;
    }

    resultsDiv.innerHTML = `<p class='loading'>🤖 AI is ${isDeep ? 'deeply' : ''} analyzing and decoding...</p>`;
    outputText.value = "Processing...";

    try {
        const response = await fetch(`${API_BASE}/decode`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, deep: isDeep })
        });

        console.log("Response status:", response.status);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Received data:", data);

        resultsDiv.innerHTML = "";
        outputText.value = "";  // Clear output field first

        if (!data.results || data.results.length === 0) {
            resultsDiv.innerHTML = "<p>No decodings found. The text might already be plaintext.</p>";
            outputText.value = text;
            document.getElementById('outputStats').textContent = `Length: ${text.length}`;
            return;
        }

        // Set top result as output (fresh)
        const topResult = data.results[0];
        outputText.value = topResult.decoded;
        document.getElementById('outputStats').textContent = `Length: ${topResult.decoded.length}`;

        const scoreVal = topResult.score !== undefined ? topResult.score : (topResult.confidence || 0);
        addToHistory("AI Auto-Decode", `Found ${data.results.length} possible decodings.<br>Top Match: ${topResult.method.toUpperCase()} (Score: ${scoreVal}/100)`);

        // Display all results
        data.results.forEach((r, index) => {
            const div = document.createElement("div");
            div.className = "result-card";

            // Use score or confidence field (handle both old and new format)
            const scoreValue = r.score !== undefined ? r.score : (r.confidence !== undefined ? r.confidence : 0);

            // Add score-based styling
            if (scoreValue >= 70) {
                div.classList.add("high-score");
            } else if (scoreValue >= 40) {
                div.classList.add("medium-score");
            } else {
                div.classList.add("low-score");
            }

            const scoreEmoji = scoreValue >= 70 ? "🎯" : scoreValue >= 40 ? "✓" : "⚠️";
            const layer = r.layer !== undefined ? r.layer : 1;
            const chainName = r.chain || r.method || "Unknown";

            div.innerHTML = `
                <div class="result-header">
                    <div>
                        <strong>${scoreEmoji} Score:</strong> ${scoreValue}/100 
                        <strong style="margin-left: 15px;">Layer:</strong> ${layer}
                    </div>
                    <button class="pivot-btn" onclick="pivotAndDecode('${escapeHtml(r.decoded.replace(/'/g, "\\'"))}')" title="Use this as new input and decode again">🚀 Pivot</button>
                </div>
                <div class="chain">
                    <strong>Method:</strong> ${chainName}
                </div>
                <div class="decoded-content">${escapeHtml(r.decoded)}</div>
            `;

            // Click content to copy to output
            div.querySelector('.decoded-content').onclick = (e) => {
                e.stopPropagation();
                outputText.value = r.decoded;
                document.getElementById('outputStats').textContent = `Length: ${r.decoded.length}`;
                showNotification("Copied to output!");
            };

            resultsDiv.appendChild(div);
        });
    } catch (error) {
        console.error("Error:", error);
        resultsDiv.innerHTML = `<p style='color: red;'>Error: ${error.message}<br>Make sure the backend server is running on ${API_BASE}</p>`;
        outputText.value = "";
    }
}

// Pivot result to input and decode again
function pivotAndDecode(text) {
    document.getElementById("inputText").value = text;
    // Trigger input event to update stats
    document.getElementById("inputText").dispatchEvent(new Event('input'));
    autoDecode();
    showNotification("Pivoted result to input!");
}
async function manualOperation(method) {
    const text = document.getElementById("inputText").value;
    const outputText = document.getElementById("outputText");
    const resultsDiv = document.getElementById("results");

    if (!text.trim()) {
        showNotification("Please enter some text first!");
        return;
    }

    // Map frontend names to backend operations
    const map = {
        'base64': 'from_base64',
        'base32': 'from_base32',
        'base58': 'from_base58',
        'base85': 'from_base85',
        'hex': 'from_hex',
        'binary': 'from_binary',
        'url': 'from_url',
        'rot13': 'rot13',
        'caesar': 'caesar_bruteforce',
        'atbash': 'atbash',
        'vigenere': 'vigenere_decrypt',
        'morse': 'from_morse',
        'jwt': 'from_jwt',
        'unicode': 'from_utf8_bytes',
        'reverse': 'reverse',
        'xor': 'xor_cipher',
        'affine': 'affine_decrypt',
        'railfence': 'rail_fence_decrypt'
    };

    const op = map[method] || method;
    let params = {};

    // Parameter handling based on UI inputs
    const paramKey = document.getElementById("paramKey").value || "secret";
    const paramRails = parseInt(document.getElementById("paramRails").value) || 3;

    if (method === 'vigenere' || method === 'xor') {
        params.key = paramKey;
    } else if (method === 'caesar' || method === 'affine') {
        params.shift = paramRails;
        params.a = paramRails;
        if (method === 'affine') {
            params.b = 8; // Default trailing Affine parameter
        }
    } else if (method === 'railfence') {
        params.rails = paramRails;
    }

    // Recipe Mode: Add to chain if in recipe tab
    if (activeTab === 'recipe') {
        addToRecipe(op, params);
        return;
    }

    showNotification(`Decoding with ${method}...`);
    outputText.value = "Processing...";

    try {
        const response = await fetch(`${API_BASE}/encode`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, operation: op, params })
        });

        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || `Error: ${response.status}`);

        outputText.value = data.output;
        document.getElementById('outputStats').textContent = `Length: ${data.output.length}`;

        // Show in results panel to satisfy user curiosity
        resultsDiv.innerHTML = `
            <div class="result-card high-score">
                <div><strong>🎯 Manual Result:</strong> ${method.toUpperCase()}</div>
                <div class="decoded-content">${escapeHtml(data.output)}</div>
            </div>
        `;
        showNotification(`${method} applied!`);
        addToHistory(`Decode: ${method.toUpperCase()}`, `Input length: ${text.length} ➔ Output length: ${data.output.length}`);
    } catch (error) {
        console.error("Error:", error);
        showNotification("Error: " + error.message);
        outputText.value = "";
    }
}

// Encode operation
async function encodeOperation(method) {
    const text = document.getElementById("inputText").value;
    const outputText = document.getElementById("outputText");
    const resultsDiv = document.getElementById("results");

    if (!text.trim()) {
        showNotification("Please enter some text to encode!");
        return;
    }

    // Map frontend names to backend operations
    const map = {
        'base64': 'to_base64',
        'base32': 'to_base32',
        'base58': 'to_base58',
        'base85': 'to_base85',
        'hex': 'to_hex',
        'binary': 'to_binary',
        'url': 'to_url',
        'rot13': 'rot13',
        'caesar': 'caesar_cipher',
        'atbash': 'atbash',
        'vigenere': 'vigenere_encrypt',
        'morse': 'to_morse',
        'reverse': 'reverse',
        'xor': 'xor_hex',
        'affine': 'affine_encrypt',
        'railfence': 'rail_fence_encrypt',
        'gzip': 'to_gzip',
        'zlib': 'to_zlib',
        'aes': 'aes_encrypt',
        'double64': 'double_base64_encode',
        'html': 'to_html',
        'upper': 'to_upper',
        'lower': 'to_lower',
        'nowhitespace': 'remove_whitespace',
        'ascii': 'to_ascii_codes',
        'utf8': 'to_utf8_bytes',
        'unicode': 'to_unicode'
    };

    const op = map[method] || method;
    let params = {};

    // Parameter handling based on UI inputs
    const paramKey = document.getElementById("paramKey").value || (method === 'aes' ? "16byte_secret_key" : "secret");
    const paramRails = parseInt(document.getElementById("paramRails").value) || 3;

    if (method === 'vigenere' || method === 'xor' || method === 'aes') {
        params.key = paramKey;
    } else if (method === 'caesar' || method === 'affine') {
        params.shift = paramRails;
        params.a = paramRails;
        if (method === 'affine') {
            params.b = 8; // Default trailing Affine parameter
        }
    } else if (method === 'railfence') {
        params.rails = paramRails;
    }

    // If recipe tab is active, add to recipe instead of executing
    if (activeTab === 'recipe') {
        addToRecipe(op, params);
        return;
    }

    showNotification(`Encoding with ${method}...`);

    try {
        const response = await fetch(`${API_BASE}/encode`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, operation: op, params })
        });

        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || `Error: ${response.status}`);

        outputText.value = data.output;
        document.getElementById('outputStats').textContent = `Length: ${data.output.length}`;
        showNotification(`Encoded with ${method}!`);
        addToHistory(`Encode: ${method.toUpperCase()}`, `Input length: ${text.length} ➔ Output length: ${data.output.length}`);

        resultsDiv.innerHTML = `
            <div class="result-card high-score">
                <div><strong>✓ Encoded with:</strong> ${method.toUpperCase()}</div>
                <div class="decoded-content">${escapeHtml(data.output)}</div>
            </div>
        `;

    } catch (error) {
        console.error("Error:", error);
        showNotification("Error: " + error.message);
    }
}

// File operations
function loadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById('inputText').value = e.target.result;
        document.getElementById('inputStats').textContent = `Length: ${e.target.result.length} | File: ${file.name}`;
        showNotification(`Loaded: ${file.name}`);
    };
    reader.readAsText(file);
}

function downloadOutput() {
    const text = document.getElementById('outputText').value;

    if (!text.trim()) {
        showNotification("No output to save!");
        return;
    }

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cipherx_output.txt';
    a.click();
    URL.revokeObjectURL(url);

    showNotification("File downloaded!");
}

// Helper functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message) {
    // Simple notification system
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #667eea;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// Theme Toggle Logic
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');

    if (body.classList.contains('light-mode')) {
        body.classList.replace('light-mode', 'dark-mode');
        themeIcon.textContent = '☀️';
        localStorage.setItem('theme', 'dark-mode');
    } else {
        body.classList.replace('dark-mode', 'light-mode');
        themeIcon.textContent = '🌙';
        localStorage.setItem('theme', 'light-mode');
    }
}

// Initialize theme
(function () {
    const savedTheme = localStorage.getItem('theme') || 'light-mode';
    const themeIcon = document.getElementById('theme-icon');
    document.body.className = savedTheme;
    if (themeIcon) {
        themeIcon.textContent = savedTheme === 'dark-mode' ? '☀️' : '🌙';
    }
})();

// Extraction operations
function extractOperation(type) {
    const text = document.getElementById("inputText").value;
    const outputText = document.getElementById("outputText");
    const resultsDiv = document.getElementById("results");

    if (!text.trim()) {
        showNotification("Please enter some text first!");
        return;
    }

    const patterns = {
        'emails': /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
        'urls': /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/g,
        'ipv4': /\b(?:\d{1,3}\.){3}\d{1,3}\b/g,
        'md5': /\b[a-fA-F0-9]{32}\b/g,
        'sha256': /\b[a-fA-F0-9]{64}\b/g,
        'base64': /\b[A-Za-z0-9+/]{8,}(?:={0,2})\b/g
    };

    const pattern = patterns[type];
    if (!pattern) return;

    const matches = text.match(pattern);

    if (!matches || matches.length === 0) {
        showNotification(`No ${type} found.`);
        outputText.value = `No ${type} found in input text.`;
        resultsDiv.innerHTML = `
            <div class="result-card low-score">
                <div><strong>⚠️ Extraction:</strong> ${type.toUpperCase()}</div>
                <div class="decoded-content">No matches found.</div>
            </div>
        `;
        return;
    }

    // Remove duplicates
    const uniqueMatches = [...new Set(matches)];

    // Format output
    let resultText = `🎯 Extraction Results: ${type.toUpperCase()}\n`;
    resultText += `📊 Found ${uniqueMatches.length} unique items (from ${matches.length} total matches)\n`;
    resultText += `------------------------------------------------------------\n\n`;
    resultText += uniqueMatches.join('\n');

    outputText.value = resultText;
    document.getElementById('outputStats').textContent = `Length: ${resultText.length} | Items: ${uniqueMatches.length}`;

    showNotification(`Extracted ${uniqueMatches.length} ${type}!`);

    // Show in results panel
    resultsDiv.innerHTML = `
        <div class="result-card high-score">
            <div><strong>🎯 Extracted ${type.toUpperCase()}:</strong> ${uniqueMatches.length} Items</div>
            <div class="decoded-content">${escapeHtml(uniqueMatches.join(', '))}</div>
        </div>
    `;
}

// Tab Switching Logic
function switchTab(tabName) {
    activeTab = tabName;

    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Deactivate all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab content
    const targetTab = document.getElementById(`tab-${tabName}`);
    if (targetTab) {
        targetTab.classList.add('active');
    }

    // Activate clicked button
    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn =>
        btn.textContent.toLowerCase().includes(tabName)
    );
    if (activeBtn) {
        activeBtn.classList.add('active');
    }

    if (tabName === 'recipe') {
        showNotification("Recipe Mode Enabled: Click operations to add steps!");
    }
}

// Placeholder functions for Batch/Recipe/History
function clearFavorites() {
    document.getElementById('favoritesList').innerHTML = "";
    showNotification("Favorites cleared!");
}

async function showHashAll() {
    const text = document.getElementById("inputText").value;
    const outputText = document.getElementById("outputText");

    if (!text.trim()) {
        showNotification("Please enter some text to hash!");
        return;
    }

    showNotification("Generating all hashes...");
    outputText.value = "Calculating hashes...";

    const algorithms = ['md5', 'sha1', 'sha256', 'sha512', 'sha3-256', 'sha3-512', 'blake2b', 'blake2s'];
    let results = `🔐 CYBERX MULTI-HASH RESULTS\n`;
    results += `------------------------------------------------------------\n\n`;

    try {
        const hashPromises = algorithms.map(alg =>
            fetch(`${API_BASE}/hash/${alg}?text=${encodeURIComponent(text)}`)
                .then(r => r.json())
        );

        const hashResults = await Promise.all(hashPromises);

        hashResults.forEach(res => {
            if (res.hash) {
                results += `[${res.algorithm.toUpperCase()}]\n${res.hash}\n\n`;
            }
        });

        outputText.value = results;
        document.getElementById('outputStats').textContent = `Generated ${algorithms.length} hashes`;
    } catch (error) {
        showNotification("Error generating hashes: " + error.message);
        outputText.value = "Failed to generate hashes.";
    }
}

async function hashOperation(algorithm) {
    const text = document.getElementById("inputText").value;
    const outputText = document.getElementById("outputText");

    if (!text.trim()) {
        showNotification("Please enter some text!");
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/hash/${algorithm}?text=${encodeURIComponent(text)}`);
        const data = await response.json();

        if (data.hash) {
            outputText.value = data.hash;
            document.getElementById('outputStats').textContent = `Algorithm: ${algorithm.toUpperCase()}`;
            showNotification(`${algorithm.toUpperCase()} hash generated!`);
            addToHistory(`Hash: ${algorithm.toUpperCase()}`, `Generated hash length: ${data.hash.length}`);
        }
    } catch (error) {
        showNotification("Error: " + error.message);
    }
}


function addToRecipe(operation, params = {}) {
    currentRecipe.push({ operation, params });
    updateRecipeUI();
    showNotification(`Added ${operation} to recipe!`);
}

function updateRecipeUI() {
    const container = document.getElementById('recipeSteps');
    const countSpan = document.getElementById('recipeCount');
    if (countSpan) countSpan.textContent = currentRecipe.length;

    container.innerHTML = "";

    if (currentRecipe.length === 0) {
        container.innerHTML = "<p style='opacity: 0.5; font-style: italic;'>No operations in recipe. Click operations to add them!</p>";
        return;
    }

    currentRecipe.forEach((step, index) => {
        const div = document.createElement('div');
        div.className = "recipe-step-item";
        div.style = "background: rgba(255,255,255,0.05); padding: 10px; margin-bottom: 5px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;";

        const paramsStr = Object.keys(step.params).length > 0 ? ` (${JSON.stringify(step.params)})` : "";

        div.innerHTML = `
            <span><strong>${index + 1}.</strong> ${step.operation}${paramsStr}</span>
            <button class="btn-sm" onclick="removeRecipeStep(${index})" style="background: rgba(255,0,0,0.2); color: #ff5e5e; padding: 4px 8px;">✕</button>
        `;
        container.appendChild(div);
    });
}

function removeRecipeStep(index) {
    currentRecipe.splice(index, 1);
    updateRecipeUI();
}

function clearRecipe() {
    currentRecipe = [];
    updateRecipeUI();
    showNotification("Recipe cleared!");
}

async function executeRecipe() {
    const text = document.getElementById("inputText").value;
    const outputText = document.getElementById("outputText");
    const resultsDiv = document.getElementById("results");

    if (!text.trim()) {
        showNotification("Please enter some text!");
        return;
    }

    if (currentRecipe.length === 0) {
        showNotification("Recipe is empty!");
        return;
    }

    showNotification("Executing recipe chain...");
    outputText.value = "Executing chain...";

    try {
        const response = await fetch(`${API_BASE}/recipe`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, operations: currentRecipe })
        });

        const data = await response.json();

        if (data.success) {
            outputText.value = data.final_output;
            document.getElementById('outputStats').textContent = `Length: ${data.final_output.length} | Steps: ${data.total_steps}`;

            resultsDiv.innerHTML = `
                <div class="result-card high-score">
                    <div><strong>✓ Recipe Executed Successfully</strong></div>
                    <div style="font-size: 0.8em; margin: 10px 0;">Completed ${data.total_steps} steps in order.</div>
                    <div class="decoded-content">${escapeHtml(data.final_output)}</div>
                </div>
            `;
            showNotification("Recipe execution complete!");
            addToHistory("Recipe Builder", `Executed chain of ${data.total_steps} sequence steps.<br>Final Output length: ${data.final_output.length}`);
        } else {
            showNotification("Error: " + data.error);
            outputText.value = "Recipe failed at step " + (data.completed_steps ? data.completed_steps.length + 1 : "unknown");
        }
    } catch (error) {
        console.error("Error:", error);
        showNotification("Error: " + error.message);
    }
}

function saveRecipe() {
    if (currentRecipe.length === 0) return;
    localStorage.setItem('cipherx_recipe', JSON.stringify(currentRecipe));
    showNotification("Recipe saved to local storage!");
}

function loadRecipe() {
    const saved = localStorage.getItem('cipherx_recipe');
    if (saved) {
        currentRecipe = JSON.parse(saved);
        updateRecipeUI();
        showNotification("Saved recipe loaded!");
    } else {
        showNotification("No saved recipe found.");
    }
}

function executeBatch() {
    showNotification("Processing batch inputs...");
}

function downloadBatchResults() {
    showNotification("Exporting batch results...");
}

function addToHistory(operation, details) {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    // Remove "No history" placeholder if it's there
    if (historyList.innerHTML.includes("No operations")) {
        historyList.innerHTML = "";
    }

    const time = new Date().toLocaleTimeString();

    // Create history item
    const item = document.createElement('div');
    item.className = 'history-item';
    item.style = 'background: rgba(255,255,255,0.05); border-left: 3px solid #6b8eff; padding: 10px; margin-bottom: 10px; border-radius: 4px; border-bottom: 1px solid rgba(255,255,255,0.1);';

    item.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <strong>${operation}</strong>
            <span style="font-size: 0.8em; opacity: 0.6;">${time}</span>
        </div>
        <div style="font-size: 0.9em; opacity: 0.8;">
            ${details}
        </div>
    `;

    // Add to top of list
    historyList.prepend(item);
}

function clearHistory() {
    document.getElementById('historyList').innerHTML = "<p style='opacity: 0.5; font-style: italic;'>No operations recorded yet.</p>";
    showNotification("History cleared!");
}

function clearInput() {
    document.getElementById('inputText').value = "";
    document.getElementById('inputStats').textContent = "Length: 0";
}

function copyOutput() {
    const output = document.getElementById('outputText');
    const copyBtn = document.querySelector('.output-section .btn-sm');

    output.select();
    document.execCommand('copy');

    // Visual feedback on button
    const originalText = copyBtn.textContent;
    copyBtn.textContent = "✅ Copied!";
    copyBtn.style.background = "#4ecca3";
    copyBtn.style.color = "white";

    showNotification("Output copied to clipboard!");

    setTimeout(() => {
        copyBtn.textContent = originalText;
        copyBtn.style.background = "";
        copyBtn.style.color = "";
    }, 2000);
}

// Global Keyboard Shortcuts
document.addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        document.getElementById('operationSearch').focus();
    }
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        downloadOutput();
    }
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        autoDecode();
    }
});

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
