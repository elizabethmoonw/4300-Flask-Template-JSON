const productSearchBox = document.querySelector("#search-box");
const productAutoBox = document.querySelector("#auto-box");
const productInputBox = document.querySelector("#prod-search-text");

const disSearchBox = document.querySelector("#dis-search-box");
const disAutoBox = document.querySelector("#dis-auto-box");
const disInputBox = document.querySelector("#dis-search-text");
const disChips = document.querySelector("#dis-chips");

const filterSearchBox = document.querySelector("#filter-text");
const filterInputBox = document.querySelector("#filter-input-box");
const filterChips = document.querySelector("#keyword-chips");

const priceSlider = document.querySelector("#amount");

const answerBox = document.querySelector("#answer-box");

const loader = document.querySelector("#loader");

var dislike_chips = [];
var filter_chips = [];

function answerBoxTemplate(
  product,
  link,
  price,
  img_link,
  ingredients,
  review,
  avg_rating,
  summary
) {
  price_formatted = price.toFixed(2);
  avg_rating = avg_rating.toFixed(1);
  if (avg_rating == -1) {
    avg_rating = "No reviews";
  }
  return `<div class='answer-item'>
      <img src=${img_link} class='product-image' style='height: 150px; width:150px; margin-top: 1em'></img>
      <div class='answer-text'>
        <h3 class='product-name'>${product}</h3>
        <div class='product-info'>
          <div class='product-price'>$${price_formatted}</div>
          <div class='answer-rating'>
            <div class='product-price'>${avg_rating}</div>
            <img src='/static/images/star.svg' style='height: 12px; width: 12px; margin-left: 0.25em'></img>
          </div>
        </div>
        <a href=${link} target='_blank' class='add-button'>Go to product</a>
        <p class='product-name'>${summary}</p>
        <p class='product-name'><b>Ingredients: </b>${ingredients}</h3>
        <p class='product-name'><b>Here's what people are saying about this product: </b>${review}</h3>
        <p class='product-name'><b>Did you like this result? </b>
          <button class="feedback-button"><img src='/static/images/thumbsup.svg'></img></button>
          <button class="feedback-button"><img src='/static/images/thumbsdown.svg'></img></button>
        </p>
      </div>
  </div>`;
}

function sendFocus() {
  productSearchBox.focus();
}

function filterText() {
  document.getElementById("answer-box").innerHTML = "";
  // console.log(document.getElementById("filter-text-val").value);
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
          row.link,
          row.price,
          row.img_link
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
        // console.log(match);
      })
    );
  return match;
}

async function showProducts() {
  if (productInputBox.value != "") {
    productSearchBox.classList.add("active");
    productAutoBox.hidden = false;
    productAutoBox.innerHTML = await matchProducts();
    allList = productAutoBox.querySelectorAll("li");
    setProductClickable(allList);
  } else {
    productSearchBox.classList.remove("active");
    productAutoBox.hidden = true;
  }
}

async function matchDislikes() {
  var match = "";
  await fetch(
    "/dislikes?" +
      new URLSearchParams({
        title: document.getElementById("dis-search-text").value,
      }).toString()
  )
    .then((response) => response.json())
    .then((data) =>
      data.forEach((row) => {
        match += `<li>${row.ingredients}</li>`;
        // console.log(match);
      })
    );
  return match;
}

function selectDislike(element) {
  // console.log("selected fskldj");
  let selectUserData = element.textContent;
  if (!dislike_chips.includes(selectUserData)) {
    dislike_chips.push(selectUserData);
    // console.log(dislike_chips);
    var chip = document.createElement("div");
    chip.classList.add("dis-chip");
    chip_text = document.createElement("span");
    chip_text.classList.add("chip--text");
    chip_text.innerHTML = selectUserData;
    chip.appendChild(chip_text);
    close_icon = document.createElement("img");
    close_icon.src = "/static/images/close-x.svg";
    close_icon.style.height = "16px";
    close_icon.style.width = "16px";
    close_icon.style.marginLeft = "8px";
    close_icon.setAttribute("onclick", "removeDislike(this)");
    close_icon.style.cursor = "pointer";
    chip.appendChild(close_icon);
    disChips.appendChild(chip);
  }
  disInputBox.value = "";
  disSearchBox.classList.remove("active");
  disAutoBox.hidden = true;
}

function removeDislike(element) {
  // console.log("removing element");
  dis_index = dislike_chips.indexOf(element.textContent);
  dislike_chips.splice(dis_index, 1);
  element.parentNode.remove();
  // console.log(dislike_chips);
}

function setDisClickable(list) {
  for (let i = 0; i < list.length; i++) {
    list[i].setAttribute("onclick", "selectDislike(this)");
  }
}

async function showDislikes() {
  if (disInputBox.value != "") {
    disSearchBox.classList.add("active");
    disAutoBox.hidden = false;
    disAutoBox.innerHTML = await matchDislikes();
    // disAutoBox.innerHTML = "<li>Alcohol</li><li>Talc</li>";
    allList = disAutoBox.querySelectorAll("li");
    setDisClickable(allList);
  } else {
    disSearchBox.classList.remove("active");
    disAutoBox.hidden = true;
  }
}

function enterKeyword(e) {
  // console.log("entering keyword");
  filterSearchBox.classList.add("active");
  if (e.which == 13) {
    let selectUserData = filterSearchBox.value;
    if (!filter_chips.includes(selectUserData) && selectUserData != "") {
      filter_chips.push(selectUserData);
      var chip = document.createElement("div");
      chip.classList.add("keyword-chip");
      chip_text = document.createElement("span");
      chip_text.classList.add("chip--text");
      chip_text.innerHTML = selectUserData;
      chip.appendChild(chip_text);
      close_icon = document.createElement("img");
      close_icon.src = "/static/images/close-x.svg";
      close_icon.style.height = "16px";
      close_icon.style.width = "16px";
      close_icon.style.marginLeft = "8px";
      close_icon.setAttribute("onclick", "removeFilter(this)");
      close_icon.style.cursor = "pointer";
      chip.appendChild(close_icon);
      filterChips.appendChild(chip);
    }
    filterSearchBox.value = "";
  }
  // console.log(filter_chips);
}

function removeFilter(element) {
  // console.log("removing element");
  filter_index = filter_chips.indexOf(element.textContent);
  filter_chips.splice(filter_index, 1);
  element.parentNode.remove();
}

function formatIngredients(ingredients) {
  ingred_string = "";
  for (i = 0; i < 5; i++) {
    if (i == ingredients.length) {
      break;
    }
    if (i == ingredients.length - 1) {
      ingred_string += ingredients[i];
      break;
    }
    ingred_string += ingredients[i] + ", ";
  }
  if (ingredients.length > 5) {
    ingred_string += "and " + (ingredients.length - 5) + " more";
  }
  return ingred_string;
}

function getResults() {
  if (productInputBox.value == "") {
    answerBox.innerHTML = "";
    priceTokens = priceSlider.value.split(" ");
    minPrice = priceTokens[0].slice(1);
    maxPrice = priceTokens[2].slice(1);
    // product = productInputBox.value;
    dislikes = dislike_chips;
    keywords = filter_chips;

    loader.hidden = false;

    console.log(loader.innerHTML);
    fetch(
      "/suggest?" +
        new URLSearchParams({
          // product: product,
          dislikes: dislike_chips,
          keywords: filter_chips,
          minPrice: minPrice,
          maxPrice: maxPrice,
        }).toString()
    )
      .then((response) => response.json())
      .then((data) => {
        data.forEach((row) => {
          let tempDiv = document.createElement("div");
          var review = row.reviews[0];
          if (review.length > 250) {
            review = review.substring(0, 250) + "...";
          }
          tempDiv.innerHTML = answerBoxTemplate(
            row.product,
            row.link,
            row.price,
            row.img_link,
            formatIngredients(row.ingredients),
            review,
            row.avg_rating,
            row.summary
          );
          answerBox.appendChild(tempDiv);
        });
        loader.hidden = true;
      });
  } else {
    answerBox.innerHTML = "";
    priceTokens = priceSlider.value.split(" ");
    minPrice = priceTokens[0].slice(1);
    maxPrice = priceTokens[2].slice(1);
    product = productInputBox.value;
    dislikes = dislike_chips;
    keywords = filter_chips;

    loader.hidden = false;

    // console.log(loader.innerHTML);
    fetch(
      "/filter?" +
        new URLSearchParams({
          product: product,
          dislikes: dislike_chips,
          keywords: filter_chips,
          minPrice: minPrice,
          maxPrice: maxPrice,
        }).toString()
    )
      .then((response) => response.json())
      .then((data) => {
        data.forEach((row) => {
          let tempDiv = document.createElement("div");
          var review = row.reviews[0];
          if (review.length > 250) {
            review = review.substring(0, 250) + "...";
          }
          tempDiv.innerHTML = answerBoxTemplate(
            row.product,
            row.link,
            row.price,
            row.img_link,
            formatIngredients(row.ingredients),
            review,
            row.avg_rating,
            row.summary
          );
          answerBox.appendChild(tempDiv);
        });
        loader.hidden = true;
      });
  }
}
