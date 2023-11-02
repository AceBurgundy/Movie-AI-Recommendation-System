import { getId, makeToastNotification } from "../../../../static/helper.js"

export default class PreviewRate {

    constructor(movieCsvId, previewId, voteAverageId, voteCountId) {

        this.ratingOptions = {
            CREATE: "create",
            DELETE: "delete"
        }
        
        this.currentRatingOption = this.ratingOptions.CREATE

        this.voteAverageId = voteAverageId
        this.voteCountId = voteCountId
        this.movieCsvId = movieCsvId
        
        this.ratingButtonId = ["rate-button", previewId].join('-')
        this.ratingInputId = ["rate-input", previewId].join('-')
    
        this.template = `
            <button id="${ this.ratingButtonId }">
            ${ 
                this.currentRatingOption === this.ratingOptions.CREATE ? "Rate" : "Clear Rating" 
            }
            </button>
            <input 
                class="preview-page__box__child-center__trailer__rate-input"
                id="${ this.ratingInputId }" 
                type="number" 
                step="0.1" 
                min="0" 
                max="5" 
                name="rating"
                placeholder="3.7">
        `
    
        this.loadScripts()
    }

    toString() {
        return this.template
    }

    /**
     * The `removeRating` function is an asynchronous function that removes a rating for a movie and
     * updates the current rating option.
     * 
     * @param {HTMLInputElement} ratingInput - The `ratingInput` parameter is an input element that represents the rating
     * value that needs to be removed.
     */
    removeRating() {

        const ratingInput = getId(this.ratingInputId)

        const oldRating = ratingInput.value

        ratingInput.value = ''

        fetch(`/rate/${this.movieCsvId}/delete`, {
            method: 'POST',
        })
            .then(response => response.json())
            .then(data => {
                if (data.status) {
                    makeToastNotification(data.message);
                }
            
                if (data.status === "failed") {
                    this.setRatingValue(oldRating)
                    this.setButtonAsDelete();
                } else {
                    this.setButtonAsCreate();
                }
            })
            .catch(error => console.error(error));
        
    }

    /**
     * The function `createRating` is an asynchronous function that takes a `ratingInput` as a parameter
     * and performs various checks and actions based on the input. 
     */
    createRating() {
        
        const ratingInput = getId(this.ratingInputId)

        if (ratingInput.value.trim() === '') {
            makeToastNotification("Rating cannot be empty")
            return
        }

        const rating = parseFloat(ratingInput.value);

        if (isNaN(rating) || rating < 0 || rating > 5) {
            makeToastNotification("Rating can only be a value between 0 - 5")
            this.setButtonAsCreate()
            return
        }

        fetch(`/rate/${this.movieCsvId}/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rating: rating }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.status == "failed") {
                    makeToastNotification(`from response ${response.message}`);
                    this.setButtonAsCreate();
                } else {
                    this.setButtonAsDelete();
                }
            })
            .catch(error => console.error(error));
        
    }

    /**
     * The function sets the text content of a button to "Rate" and updates a variable to indicate the
     * current rating option as "CREATE".
     */
    setButtonAsCreate() {
        getId(this.ratingButtonId).textContent = "Rate"
        this.currentRatingOption = this.ratingOptions.CREATE
    }

    /**
     * The function sets a button's text content to "Delete Rating" and updates the current rating option
     * to "DELETE".
     */
    setButtonAsDelete() {
        getId(this.ratingButtonId).textContent = "Delete Rating"
        this.currentRatingOption = this.ratingOptions.DELETE
    }

    /**
     * The function sets the value of a rating input field to a specified decimal value.
     * @param value - The value parameter is a number representing the rating value that needs to be set.
     */
    setRatingValue(value) {
        const ratingInput = getId(this.ratingInputId)
        ratingInput.value = value.toFixed(2);
    }

    /**
     * fetches the user rating for a movie and sets it in the rating input field.
     */
    fetchAndSetUserRating() {
        fetch(`/rate/${this.movieCsvId}/user`)
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    this.setRatingValue(data.body.content);
                    this.setButtonAsDelete();
                }
            })
            .catch(error => { console.error(error) });
    }

    /**
     * fetches and sets the average rating and vote count for a movie from a CSV file.
     */
    fetchAndSetCsvRating() {
        fetch(`/rate/${this.movieCsvId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    const rating = data.body.avarage_rating.toFixed(2);
                    const voteCount = data.body.vote_count;

                    getId(this.voteAverageId).textContent = rating;
                    getId(this.voteCountId).textContent = `${voteCount} from database`;
                }
            })
            .catch(error => { console.error(error) });
    }

    loadScripts() {
        
        setTimeout(() => {
            
            this.fetchAndSetUserRating()
            this.fetchAndSetCsvRating()

            const rateButton = getId(this.ratingButtonId)

            rateButton.onclick = () => {
                this.currentRatingOption == this.ratingOptions.CREATE ? this.createRating() : this.removeRating()
            }

        }, 0);
    }
}