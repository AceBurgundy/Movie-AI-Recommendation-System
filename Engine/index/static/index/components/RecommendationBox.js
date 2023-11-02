import { queryElements, getId, isLandscape, isPortrait } from "../../../../static/helper.js"
import Card from "./Card.js"

export default class RecommendationBox {

    constructor(movieObjects) {

        this.cardsLoaded = false
        this.dragHeight = 0
        this.movieObjects = movieObjects        
        this.movieObjectsLength = movieObjects ? movieObjects.length : 0
        this.box = getId("recommendations")
        this.loadScripts()        
    }

    toString() {
        this.show()
    }

    clear() {
        this.box.classList.remove("active")
        setTimeout(() => {
            this.box.innerHTML = ''
        }, 1000)
    }

    async generateCards() {
        return new Promise(resolve => {
            this.movieObjects.forEach(async (movie, index) => {
                const card = new Card(movie)
                this.box.innerHTML += card
                await new Promise(innerResolve => setTimeout(innerResolve, this.delay))
    
                if (index === this.movieObjects.length - 1) {
                    resolve(true) 
                }
            })
        })
    }

    async show() {
    
        this.box.classList.add("active")
        
        const cardsCreated = await this.generateCards()

		if (cardsCreated) {
			const cards = queryElements(".card")
			let cardsRevealed = 0

			cards.forEach((card, index) => {
				setTimeout(() => {
					card.classList.remove("hidden")
					cardsRevealed++

					if (cardsRevealed === cards.length) {
						this.cardsLoaded = true
					}

                }, 250 * index)
			})
		}

    }

    loadScripts = () => setTimeout(async () => await this.show(), 0)
}