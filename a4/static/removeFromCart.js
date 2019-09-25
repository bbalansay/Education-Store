document.getElementById("purchase").addEventListener("click", purchase);

const buttons = document.querySelectorAll(".delete");
for (let i = 0; i < buttons.length; i++) {
  buttons[i].addEventListener("click", deleteFromCart);
}

function purchase() {
  fetch("/main/purchase", {
      method: 'POST',
      body: JSON.stringify({}),
    credentials: 'include'
  }).then(checkStatus).then(purchased).catch(signIn);
}

function purchased() {
  const out = `<div class="alert alert-success" role="alert">
  Purchase successfull!
</div>`
  document.getElementById("alert").innerHTML = out;
  clear();
  document.getElementById("cart").innerHTML = "";
}

function deleteFromCart() {
  const id = this.getAttribute('item');
  fetch("/main/cart", {
      method: 'DELETE',
      body: JSON.stringify({
        'product_id': id,
      }),
    credentials: 'include'
  }).then(checkStatus).then(success.bind(this)).catch(signIn);
}

function success() {
  const out = `<div class="alert alert-success" role="alert">
  Deleted item from cart!
</div>`
  document.getElementById("alert").innerHTML = out;
  this.parentNode.parentNode.parentNode.removeChild(this.parentNode.parentNode);
  clear();
}

function signIn() {
  const out = `<div class="alert alert-danger" role="alert">
  Failed to delete from cart! Please try again later.
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
