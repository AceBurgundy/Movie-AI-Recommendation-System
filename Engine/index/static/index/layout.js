import { getId, setMode } from "../../../static/helper.js"

const navigationBar = getId("side-bar")
    const filterBlur = getId("filter-blur")

    // open navigation bar toggle
    getId("open-nav-box").onclick = () => {
        filterBlur.style.display = "block"
        navigationBar.style.display = "flex"
        setTimeout(() => {
            filterBlur.classList.add("active")
            navigationBar.classList.add("active")
        }, 50)
    }

    // close navigation bar toggle
    getId("close-nav-box").onclick = () => {
        filterBlur.classList.remove("active")
        navigationBar.classList.remove("active")
        setTimeout(() => {
            navigationBar.style.display = "none"
            filterBlur.style.display = "none"
        }, 300)
}

const sunIcon = getId("sun")
const sunOffIcon = getId("sun-off")

window.onclick = function (event) {

    const target = event.target
    const targetId = target.id
    const targetClassList = target.classList

    if (targetClassList.contains("nav-link")) {
        closeNavBar()
        setTimeout(() => {
            window.location.href = target.dataset.href
        }, 300)
    }

    switch (targetId) {

        case "sun-off":
            setMode("Night")
            sunOffIcon.style.display = "none"
            sunIcon.style.display = "block"
            break
        
        case "sun":
            setMode("Day")
            sunIcon.style.display = "none"
            sunOffIcon.style.display = "block"
            break
    }
}