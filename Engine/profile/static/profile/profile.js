import makeToastNotification, {
    autoResize,
    counter,
    eyeToggle,
    getCurrentOrientation,
} from "../../../static/helper.js";

const element = (className) => document.querySelector(className);

const bannerInput = element("#motto");

autoResize(bannerInput);
bannerInput.addEventListener("input", () => autoResize(bannerInput));

counter("motto", "motto-counter", 200);

document.addEventListener("click", (event) => {
    if (event.target.closest(".close-button")) {
        window.history.back();
    }
});

element("#profile-top-controls").innerHTML += `
      <div class="button close-button" id="close-text">Go Back</div>
      <div class="button" id="profile-close-button">Cancel</div>
      <svg class="close-button" id="x-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M13.41,12l6.3-6.29a1,1,0,1,0-1.42-1.42L12,10.59,5.71,4.29A1,1,0,0,0,4.29,5.71L10.59,12l-6.3,6.29a1,1,0,0,0,0,1.42,1,1,0,0,0,1.42,0L12,13.41l6.29,6.3a1,1,0,0,0,1.42,0,1,1,0,0,0,0-1.42Z"/></svg>
  `;

const targetElement =
    element(
        getCurrentOrientation() === "portrait"
        ? "#profile-bottom"
        : "#profile-top-controls"
    );

const changePasswordBtn = `<div class="button" id="change-password">Change password</div>`;
const deleteAccountBtn = `<div class="button" id="delete-account-toggle">Delete Account</div>`;

function isAllowed() {
    if (targetElement) {
        if (targetElement.hasAttribute("data-user-id") && targetElement.hasAttribute("data-current-user-id")) {
            if (targetElement.getAttribute("data-user-id") === targetElement.getAttribute("data-current-user-id")) {
                return true
            } else {
                return false
            }
        } else {
            return true
        }
    } 
}

if (isAllowed()) {
    targetElement.insertAdjacentHTML("afterbegin", changePasswordBtn);
    targetElement.insertAdjacentHTML("afterbegin", deleteAccountBtn);
}

const deleteAccountToggle = element("#delete-account-toggle");
const profilePictureInput = element("#profile-picture-input");
const profileTopControls = element("#profile-top-controls")
const cancelButton = element("#profile-close-button");
const cameraIcon = element("#camera-icon-container");
const imageInput = element("#profile-picture-input");
const formBackground = element("#form-background");
const bottomSave = element("#bottom-save-button");
const inputCounter = element("#motto-counter");
const topSave = element("#top-save-button");
const editButton = element("#edit-button");
const usernameInput = element("#username");

const blockElements = [
    deleteAccountToggle,
    cancelButton,
    cameraIcon,
    inputCounter,
    imageInput,
];

const hideElements = [
    cancelButton,
    deleteAccountToggle,
    inputCounter
];

const readonlyElements = [bannerInput, profilePictureInput, usernameInput];
const backgroundColorElements = [bannerInput, usernameInput];

getCurrentOrientation() === "landscape"
    && [...profileTopControls.children].forEach(child => child.classList.remove("button"))

if (editButton) {
    editButton.addEventListener("click", event => {
        getCurrentOrientation() === "portrait"
            ? (bottomSave.style.display = "block")
            : (topSave.style.display = "block");
    
        blockElements.forEach((element) => (element.style.display = "block"));
        backgroundColorElements.forEach(
            (element) => (element.style.backgroundColor = "var(--input-background)")
        );
        readonlyElements.forEach((element) => element.removeAttribute("readonly"));
        event.target.style.display = "none"
    });
}

cancelButton.addEventListener("click", event => {
    getCurrentOrientation() === "portrait"
        ? (bottomSave.style.display = "none")
        : (topSave.style.display = "none");

    hideElements.forEach((element) => (element.style.display = "none"));
    backgroundColorElements.forEach(
        (element) => (element.style.backgroundColor = "inherit")
    );
    readonlyElements.forEach((element) =>
        element.setAttribute("readonly", "readonly")
    );
    event.target.style.display = "none"
    editButton.style.display = "block"
});

const changePasswordToggle = element("#change-password");

// new password
const newPasswordCancel = element("#new-password-close-button");
const newPasswordForm = element("#new-password-modal");

if (changePasswordToggle) {
    changePasswordToggle.addEventListener("click", () => {
        formBackground.classList.add("active");
        newPasswordForm.classList.add("active");
    });
}

newPasswordCancel.addEventListener("click", () => {
    formBackground.classList.remove("active");
    newPasswordForm.classList.remove("active");
});

eyeToggle(
    element("#verify-eyes-icon-container"),
    element("#old-password-input"),
    element("#verify-eye"),
    element("#verify-eye-off")
);

eyeToggle(
    element("#new-password-eyes-icon-container"),
    element("#new-password-input"),
    element("#new-password-eye"),
    element("#new-password-eye-off")
);

eyeToggle(
    element("#delete-verify-eyes-icon-container"),
    element("#delete-account-password-input"),
    element("#delete-verify-eye"),
    element("#delete-verify-eye-off")
);

element("#new-password-update-button").addEventListener("click", (event) => {
    event.preventDefault();

    const old_password = element("#old-password-input").value;
    const new_password = element("#new-password-input").value;

    fetch("/change-password", {
        method: "POST",
        body: JSON.stringify({ old_password, new_password }),
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then((response) => response.json())
    .then((response) => {
        if (response.status === "success") {
            makeToastNotification(response.message);
            newPasswordForm.classList.remove("active");
            formBackground.classList.remove("active");
        } else {
            makeToastNotification(response.message);
        }
    })
    .catch((error) => {
        console.log(error);
    });
});

if (deleteAccountToggle) {
    deleteAccountToggle.addEventListener("click", () => {
        formBackground.classList.add("active");
        element("#delete-account-form").classList.add("active");
    });
}

element("#delete-account-cancel").addEventListener("click", () => {
    formBackground.classList.remove("active");
    element("#delete-account-form").classList.remove("active");
});

// delete account form submission
element("#delete-account-form").addEventListener("submit", (event) => {
    
    event.preventDefault();

    const formData = new FormData(element("#delete-account-form"));

    fetch("/profile/delete", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((response) => {
            if (response.status === "error") {
                makeToastNotification(response.message);
                element("#delete-account-form").reset();
            } else {
                window.location.href = response.url;
            }
        })
        .catch((error) => {
            console.log(error);
        });
});
