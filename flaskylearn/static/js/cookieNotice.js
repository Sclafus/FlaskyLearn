
const cookieNotice = document.getElementById("cookieAccept").parentElement;
if (document.cookie == 'cookie=true') {
    cookieNotice.style = "display: none";
} else {
    cookieNotice.children[0].addEventListener('click', () => {
        document.cookie = "cookie=true";
        cookieNotice.style = "display: none";
    });
}