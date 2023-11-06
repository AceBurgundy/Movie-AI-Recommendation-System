import {
    makeToastNotification,
    autoResize,
    counter,
    eyeToggle,
    getId,
    isLandscape,
    isPortrait
} from "../../../static/helper.js"

const bannerInput = getId("motto")

autoResize(bannerInput)

bannerInput.oninput = () => autoResize(bannerInput)

counter("motto", "motto-counter", 200)

document.onclick = event => {
    if (event.target.closest(".close-button")) window.history.back()
}

getId("profile-top-controls").innerHTML += `
    <div class="button close-button" id="close-text">
        Go Back
    </div>
    <div class="button" id="profile-close-button">
        Cancel
    </div>
    <svg class="close-button" id="x-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M13.41,12l6.3-6.29a1,1,0,1,0-1.42-1.42L12,10.59,5.71,4.29A1,1,0,0,0,4.29,5.71L10.59,12l-6.3,6.29a1,1,0,0,0,0,1.42,1,1,0,0,0,1.42,0L12,13.41l6.29,6.3a1,1,0,0,0,1.42,0,1,1,0,0,0,0-1.42Z"/></svg>
`

const targetElement = getId(isPortrait() ? "profile-bottom" : "profile-top-controls")

const changePasswordBtn = `<div class="button" id="change-password">Change password</div>`
const deleteAccountBtn = `<div class="button" id="delete-account-toggle">Delete Account</div>`

function isAllowed() {
    if (targetElement) {
        if (targetElement.hasAttribute("data-user-id") && targetElement.hasAttribute("data-current-user-id")) {
            return targetElement.getAttribute("data-user-id") === targetElement.getAttribute("data-current-user-id")
        } else {
            return true
        }
    } 
}

if (isAllowed()) {
    targetElement.insertAdjacentHTML("afterbegin", changePasswordBtn)
    targetElement.insertAdjacentHTML("afterbegin", deleteAccountBtn)
}

const deleteAccountToggle = getId("delete-account-toggle")
const profilePictureInput = getId("profile-picture-input")
const profileTopControls = getId("profile-top-controls")
const cancelButton = getId("profile-close-button")
const cameraIcon = getId("camera-icon-container")
const imageInput = getId("profile-picture-input")
const formBackground = getId("form-background")
const bottomSave = getId("bottom-save-button")
const inputCounter = getId("motto-counter")
const topSave = getId("top-save-button")
const editButton = getId("edit-button")
const usernameInput = getId("username")

const blockElements = [
    deleteAccountToggle,
    cancelButton,
    cameraIcon,
    inputCounter,
    imageInput,
]

const hideElements = [
    cancelButton,
    deleteAccountToggle,
    inputCounter
]

const readonlyElements = [bannerInput, profilePictureInput, usernameInput]
const backgroundColorElements = [bannerInput, usernameInput]

isLandscape() && [...profileTopControls.children].forEach(child => child.classList.remove("button"))

if (editButton) {
    editButton.onclick = event => {
        
        if (isPortrait()) {
            bottomSave.style.display = "block"
        } else {
            topSave.style.display = "block"
        }

        blockElements.forEach(element => element.style.display = "block")
        backgroundColorElements.forEach(element => {
            element.style.backgroundColor = "var(--input-background)"
        })
        readonlyElements.forEach(element => element.removeAttribute("readonly"))
        event.target.style.display = "none"
    }
}

cancelButton.onclick = event => {
    
    if (isPortrait()) {
        bottomSave.style.display = "none"
    } else {
        topSave.style.display = "none"
    }

    hideElements.forEach(element => (element.style.display = "none"))
    backgroundColorElements.forEach(
        element => (element.style.backgroundColor = "inherit")
    )
    readonlyElements.forEach(element =>
        element.setAttribute("readonly", "readonly")
    )
    event.target.style.display = "none"
    editButton.style.display = "block"
}

const changePasswordToggle = getId("change-password")

// new password
const newPasswordCancel = getId("new-password-close-button")
const newPasswordForm = getId("new-password-modal")

if (changePasswordToggle) {
    changePasswordToggle.onclick = () => {
        formBackground.classList.add("active")
        newPasswordForm.classList.add("active")
    }
}

newPasswordCancel.onclick = () => {
    formBackground.classList.remove("active")
    newPasswordForm.classList.remove("active")
}

eyeToggle(
    getId("verify-eyes-icon-container"),
    getId("old-password-input"),
    getId("verify-eye"),
    getId("verify-eye-off")
)

eyeToggle(
    getId("new-password-eyes-icon-container"),
    getId("new-password-input"),
    getId("new-password-eye"),
    getId("new-password-eye-off")
)

eyeToggle(
    getId("delete-verify-eyes-icon-container"),
    getId("delete-account-password-input"),
    getId("delete-verify-eye"),
    getId("delete-verify-eye-off")
)

getId("new-password-update-button").onclick = (event) => {
    event.preventDefault()

    const old_password = getId("old-password-input").value
    const new_password = getId("new-password-input").value

    fetch("/change-password", {
        method: "POST",
        body: JSON.stringify({ old_password, new_password }),
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(response => response.json())
    .then(response => {
        if (response.status === "success") {
            makeToastNotification(response.message)
            newPasswordForm.classList.remove("active")
            formBackground.classList.remove("active")
        } else {
            makeToastNotification(response.message)
        }
    })
    .catch(error => console.log(error))
}

if (deleteAccountToggle) {
    deleteAccountToggle.onclick = () => {
        formBackground.classList.add("active")
        getId("delete-account-form").classList.add("active")
    }
}

getId("delete-account-cancel").onclick = () => {
    formBackground.classList.remove("active")
    getId("delete-account-form").classList.remove("active")
}

// delete account form submission
getId("delete-account-form").addEventListener("submit", (event) => {
    
    event.preventDefault()

    const formData = new FormData(getId("delete-account-form"))

    fetch("/profile/delete", {
        method: "POST",
        body: formData,
    })
        .then(response => response.json())
        .then(response => {
            if (response.status === "error") {
                makeToastNotification(response.message)
                getId("delete-account-form").reset()
            } else {
                window.location.href = response.url
            }
        })
        .catch(error => console.log(error))
})
