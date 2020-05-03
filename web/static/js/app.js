
const MAX_CHARACTERS = 500;

/**
 * When called, will check the length of text in `targetDiv`. If 
 * the length is greater than `MAX_CHARACTERS`, it will decorate the 
 * counter value in red. If it's under, it will just update the 
 * text
 */
const updateCounter = (targetDiv, counterDiv) => {
    let newLength = $(targetDiv).val().length;
    let display = newLength + "/" + MAX_CHARACTERS;
    $(counterDiv).html(display);

    if (newLength > MAX_CHARACTERS) {
        $(counterDiv).addClass("over");
        $(targetDiv).addClass("is-invalid");
    } else if ($(counterDiv).hasClass("over")) {
        $(counterDiv).removeClass("over");
        $(targetDiv).removeClass("is-invalid");
    }
}

/**
 * Listens for changes in specified textarea field and then
 * updates value of counter
 */
const counter = (targetDiv) => {
    let counterDiv = targetDiv + "_counter";

    updateCounter(targetDiv, counterDiv);

    $(targetDiv).on('input', () => {
        updateCounter(targetDiv, counterDiv);
    })
}