document.getElementById("new").addEventListener("click", newList);

const buttons = document.querySelectorAll(".del");
for (let i = 0; i < buttons.length; i++) {
  buttons[i].addEventListener("click", deleteList);
}

function deleteList(e) {
  e.preventDefault();
  const id = this.getAttribute('id');
  fetch("/main/list/" + id, {
    method: 'DELETE',
      body: JSON.stringify({}),
    credentials: 'include'
  }).then(checkStatus).then(deleted).catch(failDelete);
}

function newList() {
  fetch("/main/list", {
      method: 'POST',
      body: JSON.stringify({
        name: document.getElementById("name").value,
        description: document.getElementById("desc").value
      }),
    credentials: 'include'
  }).then(checkStatus).then(success).catch(failure);
}

function success() {
  const out = `<div class="alert alert-success" role="alert">
  Successfully created new list!
</div>`
  document.getElementById("alert").innerHTML = out;
  clear();
  window.location.reload();
}

function deleted() {
  const out = `<div class="alert alert-success" role="alert">
  Successfully deleted list!
</div>`
  document.getElementById("alert").innerHTML = out;
  clear();
  window.location.reload();
}

function failure() {
  const out = `<div class="alert alert-danger" role="alert">
  Failed to create new list. Please try again later.
</div>`
  document.getElementById("alert").innerHTML = out;
  clear();
}

function failDelete() {
  const out = `<div class="alert alert-danger" role="alert">
  Failed to delete list. Please try again later.
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
