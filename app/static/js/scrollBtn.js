
document.addEventListener("DOMContentLoaded", () => {
    const scrollButton = document.getElementById("scrollButton")
    const scrollIcon = document.getElementById("scrollIcon")

    const updateButton = () => {
        const atTop = window.scrollY <= 50
        scrollButton.style.opacity = "1"

        if (atTop) {
            // At top → show down arrow (scrolls to bottom)
            scrollIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />'
        } else {
            // Not at top → show up arrow (scrolls to top)
            scrollIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />'
        }
    }

    window.addEventListener("scroll", updateButton)

    scrollButton.addEventListener("click", () => {
        const atTop = window.scrollY <= 50
        if (atTop) {
            window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" })
        } else {
            window.scrollTo({ top: 0, behavior: "smooth" })
        }
    })

    updateButton()
})
