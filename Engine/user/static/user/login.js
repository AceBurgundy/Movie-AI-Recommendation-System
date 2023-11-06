import { 
    makeToastNotification, 
    queryElement, 
    eyeToggle, 
    getId
} from "../../../static/helper.js"

eyeToggle(
    getId("logpassword-icon-container"),
    getId("logpassword"),
    getId("logeye"),
    getId("log-eye-off")
)

const toRegister = getId("to-register")

toRegister.addEventListener("click", () => window.location = "/register")

const form = queryElement(".authentication-form")

getId("login-button").onclick = async event => {
    
    event.preventDefault()

    const formData = new FormData(form)
    const route = form.getAttribute("data-route")

    const response = await fetch(route, {
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
            const htmlContent = await response.text()
            const htmlBlob = new Blob([htmlContent], { type: "text/html" })
            const url = URL.createObjectURL(htmlBlob)
            window.location.href = url
            return
        }

        const data = await response.json()
        
        if (data.body && Array.isArray(data.body[0])) {
            makeToastNotification(data.body[0])
        }

        if (data.message) {
            makeToastNotification(data.mesasge)
        }

        if (data.status === "success" && data.body.url) {
            window.location.href = data.body.url
            return
        } 
    
    }

}
