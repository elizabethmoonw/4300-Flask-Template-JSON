const productSearchBox = document.querySelector("#search-box");
const productAutoBox = document.querySelector("#auto-box");
const productInputBox = document.querySelector("#prod-search-text");

const disSearchBox = document.querySelector("#dis-search-box");
const disAutoBox = document.querySelector("#dis-auto-box");
const disInputBox = document.querySelector("#dis-search-text");

function answerBoxTemplate(product, category, link, price) {
  return `<div class=''>
      <h3 class='product-name'>${product}</h3>
      <p class='product-category'>${category}</p>
      <p class='product-price'>${price}</p>
      <p class='product-link'>${link}</p>
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
          row.product,
          row.category,
          row.link,
          row.price
        );
        document.getElementById("answer-box").appendChild(tempDiv);
      })
    );
}

function setProductClickable(list) {
  for (let i = 0; i < list.length; i++) {
    list[i].setAttribute("onclick", "selectProduct(this)");
    // list[i].style.setAttribute("width", productSearchBox.offsetWidth + "px");
  }
}

function selectProduct(element) {
  let selectUserData = element.textContent;
  productInputBox.value = selectUserData;
  productSearchBox.classList.remove("active");
  productAutoBox.hidden = true;
}

async function matchProducts() {
  var match = "";
  await fetch(
    "/search?" +
      new URLSearchParams({
        title: document.getElementById("prod-search-text").value,
      }).toString()
  )
    .then((response) => response.json())
    .then((data) =>
      data.forEach((row) => {
        match += `<li>${row.product}</li>`;
        console.log(match);
      })
    );
  console.log("outside");
  console.log(match);
  console.log(document.getElementById("prod-search-text").value);
  return match;
}

async function showProducts() {
  if (productInputBox.value != "") {
    productSearchBox.classList.add("active");
    productAutoBox.hidden = false;
    // productAutoBox.offsetWidth = productSearchBox.offsetWidth + "px";
    productAutoBox.innerHTML = await matchProducts();
    allList = productAutoBox.querySelectorAll("li");
    setProductClickable(allList);
  } else {
    productSearchBox.classList.remove("active");
    productAutoBox.hidden = true;
  }
}

function selectDislike(element) {
  let selectUserData = element.textContent;
  disInputBox.value = selectUserData;
  disSearchBox.classList.remove("active");
  disAutoBox.hidden = true;
}

function setDisClickable(list) {
  for (let i = 0; i < list.length; i++) {
    list[i].setAttribute("onclick", "selectDislike(this)");
  }
}

function showDislikes() {
  if (disInputBox.value != "") {
    disSearchBox.classList.add("active");
    disAutoBox.hidden = false;
    disAutoBox.innerHTML = "<li>Alcohol</li><li>Talc</li>";
    allList = disAutoBox.querySelectorAll("li");
    setDisClickable(allList);
  } else {
    disSearchBox.classList.remove("active");
    disAutoBox.hidden = true;
  }
}
