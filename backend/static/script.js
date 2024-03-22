const productSearchBox = document.querySelector("#search-box");
const productAutoBox = document.querySelector("#auto-box");
const productInputBox = document.querySelector("#prod-search-text");

const disSearchBox = document.querySelector("#dis-search-box");
const disAutoBox = document.querySelector("#dis-auto-box");
const disInputBox = document.querySelector("#dis-search-text");

function answerBoxTemplate(title, titleDesc, rating) {
  return `<div class=''>
      <h3 class='episode-title'>${title}</h3>
      <p class='episode-desc'>${titleDesc}</p>
      <p class='episode-rating'>IMDB Rating: ${rating}</p>
  </div>`;
}

function sendFocus() {
  productSearchBox.focus();
}

function filterText() {
  document.getElementById("answer-box").innerHTML = "";
  console.log(document.getElementById("filter-text-val").value);
  fetch(
    "/episodes?" +
      new URLSearchParams({
        title: document.getElementById("filter-text-val").value,
      }).toString()
  )
    .then((response) => response.json())
    .then((data) =>
      data.forEach((row) => {
        let tempDiv = document.createElement("div");
        tempDiv.innerHTML = answerBoxTemplate(
          row.title,
          row.descr,
          row.imdb_rating
        );
        document.getElementById("answer-box").appendChild(tempDiv);
      })
    );
}

function setProductClickable(list) {
  for (let i = 0; i < list.length; i++) {
    list[i].setAttribute("onclick", "selectProduct(this)");
  }
}

function selectProduct(element) {
  let selectUserData = element.textContent;
  productInputBox.value = selectUserData;
  productSearchBox.classList.remove("active");
}

function showProducts() {
  if (productInputBox.value != "") {
    productSearchBox.classList.add("active");
    productAutoBox.innerHTML =
      "<li>product 1</li><li>product 2</li><li>product 3</li>";
    allList = productAutoBox.querySelectorAll("li");
    setProductClickable(allList);
  } else {
    productSearchBox.classList.remove("active");
  }
}

function selectDislike(element) {
  let selectUserData = element.textContent;
  disInputBox.value = selectUserData;
  disSearchBox.classList.remove("active");
}

function setDisClickable(list) {
  for (let i = 0; i < list.length; i++) {
    list[i].setAttribute("onclick", "selectDislike(this)");
  }
}

function showDislikes() {
  if (disInputBox.value != "") {
    disSearchBox.classList.add("active");
    disAutoBox.innerHTML = "<li>Alcohol</li><li>Talc</li>";
    allList = disAutoBox.querySelectorAll("li");
    setDisClickable(allList);
  } else {
    disSearchBox.classList.remove("active");
  }
}
