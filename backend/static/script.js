const perfInputBox = document.querySelector("#search-text")

function answerBoxTemplate(title,titleDesc,rating){
  return `<div class=''>
      <h3 class='episode-title'>${title}</h3>
      <p class='episode-desc'>${titleDesc}</p>
      <p class='episode-rating'>IMDB Rating: ${rating}</p>
  </div>`
}

function sendFocus(){
  document.getElementById('filter-text-val').focus()
}

function filterText(){
  document.getElementById("answer-box").innerHTML = ""
  console.log(document.getElementById("filter-text-val").value)
  fetch("/episodes?" + new URLSearchParams({ title: document.getElementById("filter-text-val").value }).toString())
  .then((response) => response.json())
  .then((data) => data.forEach(row => {
      
      let tempDiv = document.createElement("div")
      tempDiv.innerHTML = answerBoxTemplate(row.title,row.descr,row.imdb_rating)
      document.getElementById("answer-box").appendChild(tempDiv)
  }));

}