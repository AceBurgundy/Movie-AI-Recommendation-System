import RecommendationBox from "./components/RecommendationBox.js"
import { recommend, getMovieData } from "../../../static/API.js"
import Warning from "./components/Warning.js"

import { 
    getId,
    makeToastNotification,
    updateStatus,
    clearStatus,
    showQueryForm,
    showRefreshButton,
    hideQueryForm
} from "../../../static/helper.js"

particlesJS.load('particles-js', "../../../static/particles.json", function() {
    console.log('callback - particles.js config loaded')
})

const movieQueryForm = getId("movie-query")
const warningBox = getId("refresh-warn")

getId("toggle-refresh").onclick = () => {
	const warning = new Warning()
	warningBox.innerHTML = warning.toString()
	warning.show()
}

const loadRecommendationBox = async movieObjects => {
	if (movieObjects) new RecommendationBox(movieObjects)
}

const reset = (message = null) => {
	showQueryForm()
	clearStatus()
	if (message) makeToastNotification(message)
}

const movieObjectsListApproved = movieObjectsList => {
	if (!Array.isArray(movieObjectsList)) {
		reset()
		return false
	}

	
	if (movieObjectsList.length === 0) {
		reset("Did not receive any recommendations")
		return false
	}

	return true
}

const movieTitleInput = getId("movie-query-director-input")

movieQueryForm.onsubmit = async event => {

    event.preventDefault()

	const title = movieTitleInput.value.trim()

	if (title === "") return makeToastNotification("Must not be empty")

	hideQueryForm()

	updateStatus("Using AI for tailored results")

    const formData = new FormData(movieQueryForm)

	const movieObjectsList = await recommend(formData)
	console.log(movieObjectsList);
	
	if (!movieObjectsListApproved(movieObjectsList)) return

	const noDate = inputString => inputString.replace(/\([^)]*\)/g, "")

	updateStatus("Retrieving movie data")

    const filteredMovieObjects = await Promise.all(movieObjectsList.map(async movie => {
		const movieTitle = movie["title"]
		const movieCsvId = movie["movie_id"]

		const movieData = await getMovieData(noDate(movieTitle))

		if (movieData.data === null || movieData === null) {
			return null
		}
		
		movieData.data["csv_id"] = movieCsvId
		return movieData
	}))
    
	updateStatus("Loading library")

	setTimeout(() => {
		clearStatus()
	}, 250)

	await loadRecommendationBox(filteredMovieObjects)

	showRefreshButton()
}
