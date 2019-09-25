document.getElementById("add").addEventListener("click", addToCart);

const lists = document.querySelectorAll(".listname");
for (let i = 0; i < lists.length; i++) {
  lists[i].addEventListener("click", addToList);
}

function addToList(e) {
  const id = this.id;
  fetch("/main/list/" + id, {
    method: 'POST',
      body: JSON.stringify({
        product_id: document.querySelector("main").id
      }),
    credentials: 'include'
  }).then(checkStatus).then(addedToList).catch(failList);
}

function addToCart() {
  const id = window.location.href.substring(window.location.href.lastIndexOf('/') + 1);
  fetch("/main/cart", {
      method: 'POST',
      body: JSON.stringify({
        'product_id': id,
        'quantity': 1
      }),
    credentials: 'include'
  }).then(checkStatus).then(success).catch(signIn);
}

function success() {
  const out = `<div class="alert alert-success" role="alert">
  Added book to cart!
</div>`
  document.getElementById("alert").innerHTML = out;
  clear();
}

function addedToList() {
  const out = `<div class="alert alert-success" role="alert">
  Added book to list!
</div>`
  document.getElementById("alert").innerHTML = out;
  clear();
}

function failList() {
  const out = `<div class="alert alert-danger" role="alert">
  Failed to add product to list. Please try again later.
</div>`
  document.getElementById("alert").innerHTML = out;
  clear();
}

function signIn() {
  const out = `<div class="alert alert-danger" role="alert">
  Please sign in before adding to cart.
</div>`
  document.getElementById("alert").innerHTML = out;
  clear();
}

function clear() {
  setTimeout(() => document.getElementById("alert").innerHTML = "", 2500);
}

function checkStatus(response) {
  if (response.status >= 200 && response.status < 300) {
    return response.text();
  } else {
    return Promise.reject(new Error(response.status + ": " + response.statusText));
  }
}
