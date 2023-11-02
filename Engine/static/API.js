import { apiKeyValue } from "./apiKey.js"
import { makeToastNotification } from "./helper.js"

const LOST_CONNECTION = "Check your internet connection and try again"

async function handleNetworkErrors(response) {
	if (!response.ok) {
		makeToastNotification(`HTTP error! Status: ${response.status}`)
		throw new Error(`HTTP error! Status: ${response.status}`)
	}
}

async function fetchJson(url) {
	const response = await fetch(url)
	await handleNetworkErrors(response)
	return response.json()
}

export const recommend = async movieForm => {
	try {

		const response = await fetch("/recommend", {
			method: "POST",
			body: movieForm,
		})

		await handleNetworkErrors(response)

		const data = await response.json()

		if (data.status === "success") {
			return data.body
		}

		makeToastNotification("Error in fetching data")
		return []
		
	} catch (error) {
		makeToastNotification(LOST_CONNECTION)
		return new Error("Network error")
	}
}

async function getMovie(title) {
	try {
		const apiKey = apiKeyValue
		const cleanTitle = title.includes(" ") ? title.split(" ").join("+") : title
		const url = `https://api.themoviedb.org/3/search/movie?api_key=${apiKey}&query=${cleanTitle}&page=1&include_adult=false&language=en-US&sort_by=popularity.desc&append_to_response=videos,images`

		const data = await fetchJson(url)

		return data.results.length > 0 ? data.results[0] : null
	} catch (error) {
		makeToastNotification(LOST_CONNECTION)
		return new Error("Failed to get movie")
	}
}

async function getMovieTrailer(movieId) {
	try {
		if (!movieId) {
			return new Error("Movie Id is needed")
		}

		const apiKey = apiKeyValue
		const url = `https://api.themoviedb.org/3/movie/${movieId}/videos?api_key=${apiKey}`

		const data = await fetchJson(url)

		let embedLink = ""

		for (const result of data.results) {
			if (result.key && result.site === "YouTube" && result.name.toLowerCase().includes("trailer")) {
				embedLink = `https://www.youtube.com/embed/${result.key}`
				break
			}
		}

		if (!embedLink) {
			return new Error("Official trailer not found")
		}

		return embedLink
	} catch (error) {
		makeToastNotification(LOST_CONNECTION)
		return new Error("Failed to get movie trailer")
	}
}

export const getMovieData = async title => {
	try {
		const movieData = await getMovie(title)

		if (!movieData) {
			makeToastNotification("Movie not found")
			return null
		}

		const baseUrl = "https://image.tmdb.org/t/p/original"
		const backdropUrl = `${baseUrl}${movieData.backdrop_path}`
		const posterUrl = `${baseUrl}${movieData.poster_path}`
		const movieTrailer = await getMovieTrailer(movieData.id)

		return {
			data: movieData,
			backdropUrl,
			posterUrl,
			movieTrailer,
		}
	} catch (error) {
		makeToastNotification(LOST_CONNECTION)
		return new Error("Failed to get movie data")
	}
}
