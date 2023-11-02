import { getId, makeToastNotification } from "../../../../static/helper.js"

export default class Comment {
	
	constructor(commentData, current_user_csv_id, index) {

		console.log(current_user_csv_id, commentData.user_csv_id);

		this.commentAuthor = current_user_csv_id == commentData.user_csv_id

		this.commentValue = commentData.content
		this.authorCsvId = commentData.user_csv_id

		this.commentId = commentData.id
		this.movieCsvId = commentData.movie_csv_id

		this.commentBoxId = ["preview-page-comment-list-item", index].join("-")
        
		this.commentUpdateInputId = ["preview-page-comment-list-item-center-input-box-input", index].join("-")
        this.authorNameId = ["preview-page-comment-list-item-center-author", index].join("-")
        
		this.profilePictureId = ["preview-page-comment-list-item-left-profile-picture", index].join("-")
		
		this.cancelCommentUpdateButtonId = ["preview-page-comment-list-item-center-options-cancel", index].join("-")
		this.commentUpdateButtonId = ["preview-page-comment-list-item-right-update", index].join('-')
        
		this.commentDeleteButtonId = ["preview-page-comment-list-item-options-delete", index].join("-")
		this.editCommentButtonId = ["preview-page-comment-list-item-options-update", index].join("-")
		this.commentOptionsOppenerId = ["preview-page-comment-list-item-right", index].join("-")
		this.commentFloatingOptions = ["preview-page-comment-list-item-options", index].join("-")

		this.commentItemRightId = ["preview-page-comment-list-item-center-options", index].join('-')
				
		this.options = `
			<div class="preview__page__comment__list__item__right" id="${ this.commentOptionsOppenerId }">
				<!-- menu icon -->
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12,7a2,2,0,1,0-2-2A2,2,0,0,0,12,7Zm0,10a2,2,0,1,0,2,2A2,2,0,0,0,12,17Zm0-7a2,2,0,1,0,2,2A2,2,0,0,0,12,10Z"/></svg>
				
				<div class="preview__page__comment__list__item__options" id="${this.commentFloatingOptions}">
					<button class="preview__page__comment__list__item__options__delete" id="${this.commentDeleteButtonId}">Delete</button>
					<button class="preview__page__comment__list__item__options__edit" id="${this.editCommentButtonId}">Edit</button>
				</div>    
			</div>
        `

		this.template = `
            <div class="preview__page__comment__list__item" id="${this.commentBoxId}">
                <div class="preview__page__comment__list__item__left">
                    <img id="${this.profilePictureId}">
                </div>
                <div class="preview__page__comment__list__item__center">
                    <p id="${this.authorNameId}">User</p>
                    <div class="preview__page__comment__list__item__center__input-box">
                        <textarea
							class="preview__page__comment__list__item__center__input-box__input"
                            id="${this.commentUpdateInputId}" 
                            required
							readonly
							rows="1">${ this.commentValue }</textarea>
                    </div>
					<div class="preview__page__comment__list__item__center__options" id="${ this.commentItemRightId }">
						<p class="preview__page__comment__list__item__center__options__cancel" id="${this.cancelCommentUpdateButtonId}">Cancel</p>
						<button class="preview__page__comment__list__item__center__options__update" id="${ this.commentUpdateButtonId }">Update</button>
					</div>
                </div>
				${this.commentAuthor ? this.options : '<div></div>'}
            </div>
        `

		this.loadScripts()
	}

	toString() {
		return this.template
	}

	fetchAndSetAuthorProfilePicture = async () => {
		
		const response = await fetch(`/comments/user/${this.authorCsvId}/profile_picture`)
		const data = await response.json()

		const profilePictureElement = getId(this.profilePictureId)
		const commentAuthorElement = getId(this.authorNameId)

		if (data.status == "failed") {
			makeToastNotification(data.message)
			return
		}

		profilePictureElement.src = data.body.profile_picture_path
		commentAuthorElement.textContent = data.body.username

	}

	deleteComment = async () => {

		const commentBox = getId(this.commentBoxId)
		commentBox.style.display = "none"
		
		try {
			const response = await fetch(`/comment/${this.commentId}/delete`, {
				method: "POST",
			})
	
			const data = await response.json()
	
			if (data.status == "success") {
				commentBox.remove()
			} else {
				makeToastNotification(response.message)
				commentBox.style.display = "flex"
			}
		} catch (error) {
			commentBox.style.display = "flex"
		}
	}

	startEdit = () => {
		
		const commentFloatingOptions = getId(this.commentFloatingOptions)
		const commentUpdateInput = getId(this.commentUpdateInputId)
		const commentBottomOptions = getId(this.commentItemRightId)

		commentBottomOptions.style.display = "flex"
		commentUpdateInput.removeAttribute("readonly")
		commentUpdateInput.classList.add("active")
		commentFloatingOptions.classList.remove("active")
		setTimeout(() => commentFloatingOptions.style.display = "none", 100);

	}

	cancelEdit = (changeValue=true) => {
		
		const commentUpdateInput = getId(this.commentUpdateInputId)
		const commentBottomOptions = getId(this.commentItemRightId)

		commentUpdateInput.readonly = true
		commentBottomOptions.style.display = "none"
		
		if (changeValue) {
			commentUpdateInput.value = this.commentValue
		}

		commentUpdateInput.classList.remove("active")
	}

	updateComment = async () => {

		const commentUpdateInput = getId(this.commentUpdateInputId)

		if (commentUpdateInput.value.trim() === "") {
			makeToastNotification("Cannot update a comment with an empty string")
			return
		}

		const response = await fetch(`/comment/${this.commentId}/update`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ new_comment: commentUpdateInput.value }),
		})

		const data = response.json()

		if (data.status == "failed") {
			makeToastNotification("message")
			commentUpdateInput.value = this.commentValue
			return
		}

		this.cancelEdit(false)

	}

	showHideOptions = () => {

		const commentFloatingOptions = getId(this.commentFloatingOptions)

		if (commentFloatingOptions.classList.contains("active")) {
			commentFloatingOptions.style.display = "none"
			setTimeout(() => commentFloatingOptions.classList.remove("active"), 100);
		} else {
			commentFloatingOptions.style.display = "flex"
			setTimeout(() => commentFloatingOptions.classList.add("active"), 100);	
		}
	}

	loadScripts() {
		setTimeout(async () => {

			const cancelCommentUpdateButton = getId(this.cancelCommentUpdateButtonId)
			const commentEditButton = getId(this.editCommentButtonId)
			const commentDeleteButton = getId(this.commentDeleteButtonId)
			const commentEditToggle = getId(this.commentOptionsOppenerId)
			const updateCommentButton = getId(this.commentUpdateButtonId)
			
			await this.fetchAndSetAuthorProfilePicture()

			console.log(this.commentAuthor);
			if (this.commentAuthor) {
				commentDeleteButton.onclick = async () => await this.deleteComment()	
				updateCommentButton.onclick = async () => await this.updateComment()
				cancelCommentUpdateButton.onclick = () => this.cancelEdit()
				commentEditToggle.onclick = () => this.showHideOptions()
				commentEditButton.onclick = () => this.startEdit()
			}

		}, 0)
	}
}
