import { getId, resetToMenu } from "../../../../static/helper.js"

export default class Warning {

    constructor(message) {

        this.message = message || "Clear and start again?"

        this.template = `
            <div id="refresh-dialog">
                <p id="refresh-dialog-message">${this.message}</p>
                <div id="refresh-dialog-options">
                    <div class="refresh-dialog-options-button" id="cancel-refresh">Nevermind</div>
                    <div class="refresh-dialog-options-button" id="continue-refresh">Continue</div>
                </div>
            </div>
        `
        this.loadScripts()
    }

    toString() {
        return this.template
    }

    show() {
        setTimeout(() => {

            this.warningElement = getId("refresh-warn")
            
            this.warningElement.style.display = "block"
            setTimeout(() => {
                this.warningElement.classList.add("active")
            }, 250);
        }, 0);
    }

    remove() {
        this.warningElement.classList.remove("active")
        setTimeout(() => {
            this.warningElement.style.display = "none"
            this.warningElement.innerHTML = ''
        }, 250);
    }
    
    loadScripts() {
        setTimeout(() => {
            this.warningElement = getId("refresh-warn")
            
            const cancel = getId("cancel-refresh")
            const continueButton = getId("continue-refresh")
    
            cancel.onclick = () => this.remove()
            continueButton.onclick = () => {
                this.remove()
                resetToMenu()
            }
        }, 0);
    }
}