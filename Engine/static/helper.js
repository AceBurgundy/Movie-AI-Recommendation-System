
/**
 * The function `getId` takes a tag name as input and returns the element with the corresponding id.
  * @param {string} tag - The id of the element.
  * @returns {HTMLElement|null}
 */
export const getId = tag => document.getElementById(tag)

/**
 * The function "newElement" creates a new HTML element based on the provided tag name.
 * @param {string} tagName - tag name of the new element.
 * @returns {HTMLElement|null}
 */
export const newElement = tagName => document.createElement(tagName)

/**
 * The function "queryElement" takes a tag as input and returns the first element in the document that
 * matches the tag.
 *
 * @param {string} tag - tagName or attribute of an element.
 * @returns {HTMLElement|null}
 */
export const queryElement = tag => document.querySelector(tag)

/**
 * The function `queryElements` takes a tag as input and returns a list of all elements in the document
 * that match that tag.
 * @param {string} tag - tagName or attribute of an element.
 * @returns {HTMLElement[]|null}
*/
export const queryElements = tag => document.querySelectorAll(tag)

/**
 * Adds a character counter to an input field and updates a corresponding counter element.
 * @param {string} inputId - The id of the input field.
 * @param {string} counterId - The id of the counter element.
 * @param {number|null} restriction - The character limit (null for no limit).
 */
export const counter = (inputId, counterId, restriction) => {
    const inputElement = getId(inputId)
    const counterElement = getId(counterId)

    if (restriction) {
        inputElement.setAttribute("maxlength", restriction);
    }

    inputElement.oninput = () => {
        counterElement.children[0].textContent = inputElement.value.length
        if (restriction && inputElement.value.length > restriction) {
            inputElement.value = inputElement.value.slice(0, restriction)
        }
    }

    window.onload = () => counterElement.children[0].textContent = inputElement.value.length
}

/**
 * Toggles the visibility of eye icons in a form.
 * @param {string} eyesContainerId - The id of the container for eye icons.
 * @param {string} inputId - The id of the input field.
 * @param {string} eyeId - The id of the eye icon (open).
 * @param {string} eyeSlashId - The id of the eye icon (close).
 */
export const eyeToggle = (eyesContainerId, inputId, eyeId, eyeSlashId) => {
    eyesContainerId.addEventListener("click", () => {
        if (inputId.getAttribute("type") === "text") {
            inputId.setAttribute("type", "password")
            eyeId.style.display = "none"
            eyeSlashId.style.display = "block"
        } else {
            inputId.setAttribute("type", "text")
            eyeId.style.display = "block"
            eyeSlashId.style.display = "none"
        }
    })
}

/**
 * The `makeToastNotification` function creates a toast notification with a given message and adds it
 * to the DOM.
 * 
 * @param message - The `message` parameter is the content of the toast notification that you want to
 * display. It can be a string or an array of strings. If it is a string, a single toast notification
 * will be created with that message. If it is an array of strings, multiple toast notifications will
 * be created
 * 
 * @returns The function does not explicitly return anything.
 */
const flashes = queryElement(".flashes")

export function makeToastNotification(message) {
    
    if (!Array.isArray(message)) {

        if (message === "") return

        let newToast = `
            <li class="message">${message}</li>
        `
        
        flashes.innerHTML += newToast
        newToast = flashes.lastElementChild

        newToast.classList.toggle("active")
    
        setTimeout(() => {
            newToast.classList.remove("active")
            setTimeout(() => newToast.remove(), 500)
        }, 2000)

        return
    }
    
    message.forEach(messageItem => makeToastNotification(messageItem))

}

/**
 * Automatically resizes a textarea element to fit its content.
 */
export const autoResize = element => {
    element.style.height = "auto"
    element.style.height = element.scrollHeight + "px"
}

const statusList = getId("status-list")

// appends new element to the status
export const updateStatus = message => {

    if (!statusList) return console.error("Status List element not found")
    if (!message) return

    const statusElement = newElement("div")
    statusElement.className = "status-message"
    statusElement.textContent = message

    if (statusList.children.length > 0) {
        const recentElement = statusList.lastElementChild
        recentElement.classList.add("end")
        recentElement.classList.remove("start")
        setTimeout(() => {
            recentElement.remove()
        }, 250)
    }

    statusList.appendChild(statusElement)

    setTimeout(() => {
        statusElement.classList.add("start")
    }, 250)

}

/**
 * As the status element holds message elements which on their own has a remove timer except for the last element
 * This function simply removes the element in any chance the it was not removed.
 * 
 */
export const clearStatus = () => {

    if (!statusList) return console.error("Status List element not found")
    if (statusList.children.length > 0) {
        const recentElement = statusList.lastElementChild
        recentElement.classList.add("end")
        recentElement.classList.remove("start")
        setTimeout(() => {
            recentElement.remove()
        }, 250)
    }

}

/**
 * Brings back to the state where only the movie query form is showing
 */
export const resetToMenu = () => {
    const box = getId("recommendations")
    box.classList.remove("active")

    setTimeout(() => {

        box.innerHTML = ''

        const movieQueryForm = getId("movie-query")
        const refreshWarn = getId("refresh-warn")
        const refreshToggle = getId("toggle-refresh")

        if (movieQueryForm) {
            movieQueryForm.classList.add("active")
            movieQueryForm.style.display = "flex"
        }

        if (refreshWarn) {
            refreshWarn.classList.remove("active")
        }

        if (refreshToggle) {
            refreshToggle.classList.remove("active")
        }

    }, 250)
}

// Shows the backdrop
export const showBackdrop = () => {
    const box = getId("backdrop")
    box.style.display = "block"
    setTimeout(() => {
        box.classList.add("active")
    }, 250)
}

// hides the backdrop
export const hideBackdrop = () => {
    const box = getId("backdrop")
    box.classList.remove("active")
    setTimeout(() => {
        box.style.display = "none"
    }, 250)
}

// returns true if landscape
export const isLandscape = () => window.matchMedia("(orientation: landscape)").matches

// returns false if landscape
export const isPortrait = () => window.matchMedia("(orientation: portrait)").matches

const movieQueryForm = getId("movie-query")
const refreshButton = getId("toggle-refresh") 

// shows the query form
export const showQueryForm = () => {
    movieQueryForm.style.display = "flex"
    setTimeout(() => {
        movieQueryForm.classList.add("active")        
    }, 100)
}

// hides the query form
export const hideQueryForm = () => {
    movieQueryForm.classList.remove("active")
    setTimeout(() => {
        movieQueryForm.style.display = "none"
    }, 100)
    queryElements(".ownership").forEach(ownership => ownership.style.display = "none")
}

// shows the refresh button
export const showRefreshButton = () => {
    refreshButton.classList.add("active")
}

/**
 * The function `changeParticleColor` changes the color of particles in a particleJS animation based on
 * the mode (either "Night" or not).
 */
const changeParticleColor = mode => {
	const newColor = mode === "Night" ? "#fff" : "#000"
	
    if (!pJSDom[0]) {
        console.warn("Cannot change particleJS color as it cannot be found")
        return
    }
    
    pJSDom[0].pJS.particles.array.forEach(function (p) {
		p.color.value = newColor
		p.color.rgb = hexToRgb(newColor)
		pJSDom[0].pJS.particles.line_linked.color_rgb_line = hexToRgb(newColor)
	})
}

const html = queryElement("html")

/**
 * The `setMode` function is responsible for changing the mode of the application, updating the UI, and
 * making a POST request to update the server-side mode.
 */
export const setMode = mode => {

    changeParticleColor(mode)

    switch (mode) {
        case "Night":
            html.classList.add("night")
            html.classList.remove("day")
            break;

        case "Day":
            html.classList.remove("night")
            html.classList.add("day")
            break;
    }

    fetch("/night-mode", {
        method: "POST",
        body: JSON.stringify({ mode: mode }),
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(response => {
        if (response.status === "success") {
            makeToastNotification(mode)
        } else {
            makeToastNotification(response.message)
        }
    })
    .catch(error => {
        console.log(error)
    })
}