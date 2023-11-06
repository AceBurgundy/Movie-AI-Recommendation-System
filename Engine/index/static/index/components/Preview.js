import {getId, hideBackdrop, queryElement, showBackdrop } from "../../../../static/helper.js"
import { genres } from "../../../../static/genres.js"
import PreviewComment from "./PreviewComment.js"
import PreviewRate from "./PreviewRate.js"
import Comment from "./Comment.js"

export default class Preview {

    constructor(movieData) {
        const { data, backdropUrl, posterUrl, movieTrailer, } = movieData
        const { csv_id, genre_ids, overview, title, vote_average, vote_count} = data
           
        const movieGenres = genre_ids.map(id => genres[id])

        this.movieCsvId = csv_id
        this.backdropUrl = backdropUrl
        this.currentUserCsvId = null
        
        const previewId = [title.toLowerCase().split(' ').join('-'), "preview"].join('-')
        
        this.voteAverageId = ["preview-page-box-child-center-rating-circle-score", previewId].join('-')
        this.voteCountId = ["preview-page-box-child-center-rating-vote-count", previewId].join('-')
        
        this.commentListId = "preview-page-comment-list"
        this.commentBuilder = "preview-page-comment-builder"
        
        this.ratingBoxId = ["preview-page-box-child-center-trailer", previewId].join('-')
        
        this.previewPageTrailerId = ["preview-page-trailer", previewId].join('-')
        this.trailerSectionCloseButtonId = ["preview-page-trailer-close-button", previewId].join('-')

        this.watchTrailerId = ["trailer-button", previewId].join('-')
        this.closeButtonId = ["close-button", previewId].join('-')

        const ratingColor = {
            good: "#27ae60",
            okay: "#f1c40f",
            bad: "#e74c3c"
        }

        let scoreClass = null
        let gradient = null

        if (vote_average && vote_count) {

            if (vote_average < 4.0) {
                scoreClass = "bad"
            } else if (vote_average < 6.0) {
                scoreClass = "okay"
            } else {
                scoreClass = "good"
            }

            gradient = `background: conic-gradient(${ ratingColor[scoreClass] } ${Math.floor(vote_average * 10)}%, transparent 0 100%)`    
        }

        this.template = `
            <section class="preview__page">
                <section class="preview-page__box">
                    <div class="preview-page__box__child-left">
                        <img class="preview-page__box__child-left__poster" src=${posterUrl ?? ''} alt="${ title }">
                    </div>
                    <div class="preview-page__box__child-center">
                        <div class="preview-page__box__child-center">
                            <p class="preview-page__box__child-center__title">${ title }</p>
                            <p class="preview-page__box__child-center__genres">${ movieGenres.join(" - ") }</p>
                        </div>
                        <div class="preview-page__box__child-center__trailer">
                            <button id="${ this.watchTrailerId }">Watch Trailer</button>
                            <div id=${ this.ratingBoxId }></div>
                        </div>
                        <p class="preview-page__box__child-center__overview">${ overview ?? '' }</p>
                        <div class="preview-page__box__child-center__rating">
                            <div class="preview-page__box__child-center__rating__circle ${ scoreClass }" style="${ gradient }">
                                <p id="${ this.voteAverageId }">${ vote_average ? vote_average.toFixed(1) : 0 }</p>
                            </div>
                            <p id="${ this.voteCountId }">Voted by: ${ vote_count || '' } users</p>
                        </div>
                    </div>
                </section>
                <div id="${ this.closeButtonId }" class="preview-close-button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" id="preview-close-icon"><path d="M5.3 18.7c.2.2.4.3.7.3s.5-.1.7-.3l5.3-5.3 5.3 5.3c.2.2.5.3.7.3s.5-.1.7-.3c.4-.4.4-1 0-1.4L13.4 12l5.3-5.3c.4-.4.4-1 0-1.4s-1-.4-1.4 0L12 10.6 6.7 5.3c-.4-.4-1-.4-1.4 0s-.4 1 0 1.4l5.3 5.3-5.3 5.3c-.4.4-.4 1 0 1.4z"></path></svg>
                </div>
            </section>
            <section class="preview__page" id="${ this.previewPageTrailerId }">
                <div id="${ this.trailerSectionCloseButtonId }" class="preview-close-button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" id="preview-close-icon"><path d="M5.3 18.7c.2.2.4.3.7.3s.5-.1.7-.3l5.3-5.3 5.3 5.3c.2.2.5.3.7.3s.5-.1.7-.3c.4-.4.4-1 0-1.4L13.4 12l5.3-5.3c.4-.4.4-1 0-1.4s-1-.4-1.4 0L12 10.6 6.7 5.3c-.4-.4-1-.4-1.4 0s-.4 1 0 1.4l5.3 5.3-5.3 5.3c-.4.4-.4 1 0 1.4z"></path></svg>
                </div>
                <iframe class="preview-page__trailer" frameborder="0" src="${ movieTrailer || '' }" allowfullscreen></iframe>
                <section id="preview-page-comment">
                    <div id="${ this.commentBuilder }"></div>
                    <div id="${ this.commentListId }"></div>            
                </section>
            </section>
        `

        this.loadScripts()
    }

    toString() {
        return this.template
    }

    fetchAndLoadAllComments = async (refresh=false) => {

        const commentList = getId(this.commentListId)

        const response = await fetch(`/comments/${this.movieCsvId}`)
        const data = await response.json()

        if (data.status === "failed") return
        
        const comments = data.body.comments
        const currentUserCsvId = data.body.current_user_csv_id

        if (refresh) {
            commentList.innerHTML = ''
        }

        comments.forEach((comment, index) => {
            commentList.innerHTML += new Comment(comment, currentUserCsvId, index)
        })
        
    }

    showPreview = () => {

        const preview = queryElement(".preview")

        showBackdrop()   
        preview.style.backgroundImage = `url(${this.backdropUrl})`
        preview.style.display = "block"
        setTimeout(() => preview.classList.add("active"), 100)
    }

    closePreview = () => {

        const preview = queryElement(".preview")

        preview.classList.remove("active")
        hideBackdrop()
    
        setTimeout(() => {
            preview.style.display = "none"
            preview.removeAttribute("style")
            preview.innerHTML = ''
        }, 250)
    }

    showTrailerSection() {
        const trailerSection = getId(this.previewPageTrailerId)
        trailerSection.style.display = "flex"
        setTimeout(() => trailerSection.classList.add("active"), 100);
    }

    hideTrailerSection() {
        const trailerSection = getId(this.previewPageTrailerId)
        trailerSection.classList.remove("active")
        setTimeout(() => trailerSection.style.display = "none", 100);
    }

    loadScripts() {
        setTimeout(async () => {
            const trailerSectionCloseButton = getId(this.trailerSectionCloseButtonId)
            const watchTrailerButton = getId(this.watchTrailerId)
            const closeButton = getId(this.closeButtonId)

            await this.fetchAndLoadAllComments()
            
            this.showPreview()
            
            closeButton.onclick = () => this.closePreview()
            watchTrailerButton.onclick = () => this.showTrailerSection()
            trailerSectionCloseButton.onclick = () => this.hideTrailerSection()
            
            getId(this.commentBuilder).innerHTML = new PreviewComment(this.movieCsvId, this.commentListId)
            getId(this.ratingBoxId).innerHTML = new PreviewRate(this.movieCsvId, this.previewId, this.voteAverageId, this.voteCountId)
        }, 0)
    }
}