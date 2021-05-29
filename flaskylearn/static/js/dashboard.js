function getLessons(){
    fetch(`${window.origin}/dashboard/getLessons`, {
        method: "POST",
        body: JSON.stringify({
            'id': parseInt(document.getElementById('course').value)
        }),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }) //getting the response back
    .then(function (response) {
        if (response.status !== 200) {
            console.log(`Response status was ${response.status}`)
            return;
        }

        response.json().then(function (data) {
            const lessonDiv = document.getElementById('lessons')
            if (data.lessons.length){
                lessonDiv.innerText = `These lessons are already present: ${data.lessons.join(", ")}`
            } else {
                lessonDiv.innerText = '';
            }
            return;
        })
    })
}
window.onload = getLessons();
document.getElementById('course').addEventListener("change", getLessons, false);