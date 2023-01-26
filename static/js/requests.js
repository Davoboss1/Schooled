

const htmxProcess = (selector) => {
    document.querySelectorAll(selector).forEach((elem) => {
        htmx.process(elem);
    });
}

document.addEventListener("htmx:beforeSend", function (event) {
    let detail = event.detail;
    let element = detail.elt;
    let target = detail.target;
    let message = '<div class="m-auto d-flex flex-column"><div class="mx-auto progressBar"></div><small class="text-center">Processing...</small></div>';
    if (element.hasAttribute("hx-loading-target"))
        document.querySelector(element.getAttribute("hx-loading-target")).innerHTML = message;
    else
        target.innerHTML = message;

});

document.addEventListener("htmx:responseError", function (event) {
    let detail = event.detail;
    let element = detail.elt;
    let target = detail.target;
    let message = '<div class="alert alert-danger mx-auto alert-dismissible fade show" role="alert"><strong>Sorry!</strong>  But your request could not be completed. <hr class="mb-0">' + detail.xhr.responseText + '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>';

    if (element.hasAttribute("hx-error-target"))
        document.querySelector(element.getAttribute("hx-error-target")).innerHTML = message;
    else
        target.innerHTML = message;

});

document.addEventListener("htmx:sendError", function (event) {
    let detail = event.detail;
    let element = detail.elt;
    let target = detail.target;

    let message = '<div class="d-flex flex-column h-100 justify-content-center"><svg class="mx-auto" width="100px" height="100px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3.23 7.913 7.91 3.23c.15-.15.35-.23.57-.23h7.05c.21 0 .42.08.57.23l4.67 4.673c.15.15.23.35.23.57v7.054c0 .21-.08.42-.23.57L16.1 20.77c-.15.15-.35.23-.57.23H8.47a.81.81 0 0 1-.57-.23l-4.67-4.673a.793.793 0 0 1-.23-.57V8.473c0-.21.08-.42.23-.57v.01Z" fill="#000000" fill-opacity=".16" stroke="#d50000" stroke-width="1.5" stroke-miterlimit="10" stroke-linejoin="round"/><path d="M12 16h.008M12 8v5" stroke="#d50000" stroke-width="1.5" stroke-miterlimit="10" stroke-linecap="round"/></svg><small class="mx-auto text-center text-danger">Something went wrong. Check your connection and try again</div>';
    
    if (element.hasAttribute("hx-error-target"))
        document.querySelector(element.getAttribute("hx-error-target")).innerHTML = message;
    else
        target.innerHTML = message;
});

document.addEventListener("htmx:afterRequest", function (event) {
   
    let detail = event.detail;
    let element = detail.elt;
    let tag_type = element.tagName.toLowerCase();

    if (detail.successful && tag_type === "form" && !element.hasAttribute("no-reset")) {
        detail.elt.reset();
    }
    if (element.hasAttribute("hx-loading-target"))
        document.querySelector(element.getAttribute("hx-loading-target")).innerHTML = '';
    
});