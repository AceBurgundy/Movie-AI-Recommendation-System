import { autoResize, getId, isLandscape, makeToastNotification } from "../../../../static/helper.js"
import Comment from "./Comment.js"

export default class PreviewComment {
    
    constructor(movieCsvId, commentListId) {

        this.movieCsvId = movieCsvId
        this.commentListId = commentListId

        this.template = `
            <div id="preview-page-comment-builder-left">
                <img id="preview-page-comment-builder-left-image">
            </div>
            <div id="preview-page-comment-builder-right">
                <p id="preview-page-builder-right-username">Author</p>
                <div id="preview-page-comment-builder-right-input-builder">
                    <textarea 
                        id="preview-page-comment-builder-right-input-builder-input"
                        name="comment"
                        required
                        rows="1"></textarea>
                </div>
                <div id="preview-page-comment-builder-right-options">
                    <p id="preview-page-comment-builder-right-options-cancel">Cancel</p>
                    <button id="preview-page-comment-builder-right-options-comment">Comment</button>
                </div>
            </div>
        `

        this.loadScripts()
    }

    toString = () => {
        return this.template
    }
    
    fetchAndSetUserName = () => {
        
        const userNameElement = getId("preview-page-builder-right-username")

        fetch("/user/username")
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    userNameElement.textContent = data.body.username
                }
            })
            .catch(error => console.warn(error))

    }

    fetchAndSetProfilePicture = () => {

        const profilePictureElement = getId("preview-page-comment-builder-left-image")

        fetch("/user/profile_picture")
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    profilePictureElement.src = data.body.profile_picture
                }
            })
            .catch(error => console.warn(error))

    }

    showCommentOptions = (commentRightbuilder, commentInput) => {
        const optionsBox = getId("preview-page-comment-builder-right-options")
        commentInput.value.trim()
        optionsBox.classList.add("active")
        commentRightbuilder.classList.add("active")

        if (isLandscape()) commentRightbuilder.scrollIntoView({ behavior: "smooth" });
    }

    revertToDefaultState = (cancelComment, commentRightbuilder) => {
        cancelComment.parentElement.classList.remove("active")
        commentRightbuilder.classList.remove("active")
    }

    createComment = async (commentList, commentInput) => {

        if (commentInput.value.trim() === '') {
            makeToastNotification("Comment cannot be empty")
            return
        }

        const response = await fetch(`/comment/${this.movieCsvId}/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ comment: commentInput.value }),
        })
            
        const data = await response.json()

        if (data.status) {
            makeToastNotification(data.message)
        }

        if (data.status === "success") {
            const commentListHasChildren = commentList.children.length > 0

            const commentListLength = commentList.children.length
            const nextCommentIndex = commentListHasChildren ? commentListLength + 1 : 0
            
            commentList.innerHTML += new Comment(
                data.body.new_comment,
                data.body.current_user_csv_id,
                nextCommentIndex,
            )
        }

    }

    loadScripts = () => {
        setTimeout(async () => {
            const commentInput = getId("preview-page-comment-builder-right-input-builder-input")
            const commentButton = getId("preview-page-comment-builder-right-options-comment")
            const cancelComment = getId("preview-page-comment-builder-right-options-cancel")
            const commentRightbuilder = getId("preview-page-comment-builder-right")
            const commentList = getId(this.commentListId)

            this.fetchAndSetUserName()
            this.fetchAndSetProfilePicture()

            commentInput.oninput = () => autoResize(commentInput)
            commentInput.onclick = () => this.showCommentOptions(commentRightbuilder, commentInput)
            commentButton.onclick = async () => await this.createComment(commentList, commentInput)  
            cancelComment.onclick = () => this.revertToDefaultState(cancelComment, commentRightbuilder)    
        }, 0);
    }
}