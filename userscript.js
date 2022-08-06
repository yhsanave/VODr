// ==UserScript==
// @name         VODr
// @version      1.0
// @description  Import title and description from VODr exports with one button press
// @updateURL    https://raw.githubusercontent.com/yhsanave/VODr/main/userscript.js
// @downloadURL  https://raw.githubusercontent.com/yhsanave/VODr/main/userscript.js
// @website      https://github.com/yhsanave/VODr
// @supportURL   https://github.com/yhsanave/VODr
// @author       Yhsanave
// @match        https://studio.youtube.com/*
// ==/UserScript==

(function () {
    'use strict';
    var data = {};

    window.addEventListener("keydown", keyboardHandler, false);

    // Set the value of the input field and then fire the input event to force it to update
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
                    if (data[filename]) {
                        setField(titleField, data[filename].title);
                        setField(descField, data[filename].description);
                    } else {
                        alert('Filename not found, press ctrl+F8 to enter your export code and do not rename files after processing them');
                    }
                } catch (err) {
                    console.error(err);
                }
            }

            zEvent.preventDefault();
            zEvent.stopPropagation();
        }
    }
})();
