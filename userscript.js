// ==UserScript==
// @name         VODr
// @version      1.0
// @description  Enter title, description, and game from VODr
// @author       Yhsanave
// @match        https://studio.youtube.com/*
// ==/UserScript==

(function () {
    'use strict';
    var data = {};

    window.addEventListener("keydown", keyboardHandler, false);

    function setField(element, value) {
        element.textContent = value;
        element.focus();
        element.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function keyboardHandler(zEvent) {
        if (zEvent.key == 'F8') {
            if (zEvent.ctrlKey) {
                data = JSON.parse(prompt('Paste VODr export code here'));
            } else {
                const filename = document.querySelector('#original-filename').textContent.trim();
                const titleField = document.querySelector('#title-textarea > ytcp-form-input-container:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > ytcp-social-suggestion-input:nth-child(1) > div:nth-child(1)');
                const descField = document.querySelector('#description-textarea > ytcp-form-input-container:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > ytcp-social-suggestion-input:nth-child(1) > div:nth-child(1)');
    
                try {
                    setField(titleField, data[filename].title)
                    setField(descField, data[filename].description)
                } catch (err) {
                    console.error(err);
                }
            } 

            zEvent.preventDefault();
            zEvent.stopPropagation();
        }
    }
})();
