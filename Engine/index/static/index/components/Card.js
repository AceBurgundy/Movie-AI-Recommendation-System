import { getId, makeToastNotification, queryElement } from "../../../../static/helper.js"
import Preview from "./Preview.js"

export default class Card {
    
    constructor(movieData) {

        this.movieData = movieData

        const { data, posterUrl } = movieData
        const { title } = data

        const cleanTitle = title.includes(" ") ? title.split(" ").join("-") : title

        this.cardId = [cleanTitle, "card"].join("-")
        this.template = this.generateTemplate(title, posterUrl)
        this.loadScripts(movieData)
    }

    toString() {
        return this.template
    }

    generateTemplate(title, poster) {
        return `
            <section class="card hidden" id="${this.cardId}">
                <img src="${poster}" alt="${title}" class="card__image">
                <p class="card__title">${title}</p>
            </section>
        `
    }

    loadScripts(movieData) {
        setTimeout(() => {
            const card = getId(this.cardId)

            if (document.body.contains(card)) {
                card.onclick = () => {
                    makeToastNotification("Loading movie data")
                    queryElement(".preview").innerHTML = new Preview(movieData) 
                }
            }
        }, 0);
    }
}