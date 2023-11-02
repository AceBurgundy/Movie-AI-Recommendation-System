import { 
    makeToastNotification, 
    queryElements,
    eyeToggle, 
    getId
} from "../../../static/helper.js"

getId("to-login").addEventListener("click", () => window.location = "/login")

const pattern = /(where)|(select)|(update)|(delete)|(.schema)|(from)|(drop)|\d|[!@#$%^&()_}{":?><*+['./,]|-/gi
const userNameCircle = getId("first-name-circle")
const passwordInput = getId("regpassword")
const emailCircle = getId("email-circle")
const email = getId("register-email")
const form = getId("form-register")
const userName = getId("username")

eyeToggle(
    getId("regpassword-icon-container"),
    passwordInput,
    getId("regeye"),
    getId("reg-eye-off")
)

let stillHasErrors = true

/**
 * The function `fillCircleAndToast` changes the color of an element and displays a toast notification
 * with a given message.
 * 
 * @param element - The element parameter is the HTML element that you want to modify. It could be any
 * valid HTML element such as a div, span, button, etc.
 * @param message - The message parameter is a string that represents the message you want to display
 * in the toast notification.
 * @param [fill=false] - The `fill` parameter is a boolean value that determines whether to fill the
 * circle element with the color red or change the text color to red. If `fill` is `true`, the circle
 * element will be filled with red color. If `fill` is `false`, the text color of the
 */
const fillCircleAndToast = (element, message, fill=false) => {

    if (fill) {
        element.style.fill = "red"
    } else {
        element.style.color = "red"
    }
    
    makeToastNotification(message)
}

/**
 * The function `validateRegister` checks if the email input is valid and displays error messages if it
 * is not.
 * 
 * @returns the result of calling the `fillCircleAndToast` function with the `emailCircle` element and
 * an error message as arguments.
 */
function validateRegister() {

    const emailValue = email.value.trim()

    if (emailValue !== "") {

        const validations = [
            emailValue.match(/@/),
            emailValue.match(".com"),
            emailValue !== ""
        ]
        
        if (validations[0] === null) {
            return fillCircleAndToast(emailCircle, "Missing @")
        } 
        
        if (validations[1] === null) {
            return fillCircleAndToast(emailCircle, "Missing .com")
        }
        
        if (!validations[2]) {
            return fillCircleAndToast(emailCircle, "Email cannot be empty")
        }
        
        emailCircle.style.fill = "green"

        stillHasErrors = validations.some(validation => validation === null || validation === false)
    }
}

/**
 * The function `validatePassword` checks if a password meets certain criteria and displays an error
 * message if it doesn't.
 * 
 * @returns either a call to the `fillCircleAndToast` function with an error message and `true` as
 * arguments, or it is setting the `color` property of the `passwordInput` element to "green".
 */
function validatePassword() {

    const passwordValue = passwordInput.value.trim()

    if (passwordValue !== "") {

        const validations = [
            !passwordValue.match(/(where)|(select)|(update)|(delete)|(.schema)|(from)|(drop)|-/gi),
            passwordValue.match(/[!@#$%^&*()_}{":?><+['./,]/),
            passwordValue.match(/\d/),
        ]

        if (!validations[0]) {
            return fillCircleAndToast(passwordInput, "Password should not contain forbidden keywords.", true)
        }
        
        if (validations[1] === null || validations[2] === null) {
            return fillCircleAndToast(passwordInput, "Password should contain at least one number and one special character.", true)
        }

        passwordInput.style.color = "green"

        stillHasErrors = validations.some(validation => validation === null || validation === false)
    }
}

/**
 * The function `validateUsername` checks if a username input meets certain criteria and displays an
 * error message if it doesn't.
 * 
 * @returns a call to the `fillCircleAndToast` function with the appropriate error message based on the
 * validation that failed.
 */
function validateUsername() {

    const usernameValue = userName.value.trim()

    if (usernameValue !== "") {

        const validations = [
            usernameValue.length > 2,
            usernameValue.length < 30,
            !usernameValue.match(pattern),
            usernameValue !== ""
        ]

        if (!validations[0]) {
            return fillCircleAndToast(userNameCircle, "Username should have at least 3 characters.")
        }
        
        if (!validations[1]) {
            return fillCircleAndToast(userNameCircle, "Username should have at most 30 characters.")
        } 
        
        if (!validations[2]) {
            return fillCircleAndToast(userNameCircle, "Username should not contain special characters or numbers.")
        }
        
        if (!validations[3]) {
            return fillCircleAndToast(userNameCircle, "Username should not be empty.")
        }
        
        userNameCircle.style.fill = "green"

        stillHasErrors = !!validations.includes(false)
    }
}

/**
 * The function `validateForm` is used to validate the password, email, and username fields in a form.
 * 
 * @param [event=null] - The event parameter is an optional parameter that represents the event that
 * triggered the form validation. It can be an event object that contains information about the event,
 * such as the target element that triggered the event. If the event parameter is not provided, the
 * function will perform form validation without considering the event that triggered
 */
function validateForm(event = null) {

    if (event) {

        const target = event.target

        if (target.id === "regpassword") {
            validatePassword()
        }
    
        if (target.id === "register-email") {
            validateRegister()
        }
    
        if (target.id === "username") {
            validateUsername()
        }

    }

    if (!event) {
        validatePassword()
        validateRegister()
        validateUsername()
    }
}

const inputList = [...queryElements("input")]

inputList.forEach(input => input.onclick = event => validateForm(event))

/* 
The code block is setting up an interval that runs every 100 milliseconds. Within the interval, it
checks if there are any input fields with the `-webkit-autofill` pseudo-class applied to them. If
there are any filled inputs, it clears the interval and calls the `validateForm()` function. This is great
especially as form filled with auto-fill isnt directly triggered by validateForm() but a -webkit-autofill
will always be added to auto-filled forms, the interval is just a trigger to continuosly check these inputs
*/
let intervalId = setInterval(() => {
    const filledInputs = queryElements("input:-webkit-autofill")

    if (filledInputs.length > 0) {
        clearInterval(intervalId)
        validateForm()
    }
}, 100)
  
form.onkeyup = event => validateForm(event)
form.oninput = event => validateForm(event)

const registerButton = getId("register-button")

registerButton.onclick = async event => {

    event.preventDefault()

    validateForm()
    
    if (stillHasErrors) return

    const formData = new FormData(form)

    // submits the form to the route
    try {

        const response = await fetch(form.getAttribute("data-route"), {
            method: "POST",
            body: formData,
        })
    
        if (response.ok) {

            /**
             * This check block catches for any cases where the response is ok, but the response
             * body contains an html code instead of a json response, thus it redirects to the html.
             */
            const contentType = response.headers.get("content-type")

            if (contentType.includes("text/html")) {
                const htmlContent = await response.text();
                const htmlBlob = new Blob([htmlContent], { type: "text/html" });
                const url = URL.createObjectURL(htmlBlob);
                window.location.href = url;
                return
            }

            // This runs in a case that it isnt an html but indeed a JSON Response
            const data = await response.json()

            if (data.message) {
                makeToastNotification(data.message)
            }
    
            if (data.status === "success" && data.body.url) {
                window.location.href = data.body.url
                return
            }
    
        }

    } catch (error) {
        console.warn(error);
    }

}
