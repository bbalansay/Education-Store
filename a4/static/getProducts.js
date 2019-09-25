fetch("/main/products/api", {
headers: {
'Accept': 'application/json',
'X-Requested-With': 'XMLHttpRequest'
},
credentials: 'include'
}).then(res => res.json()).then(show).catch(console.log);

function show(res) {
  res.forEach(item => {
    // const outer = document.createElement("div");
    // outer.className = "col-lg-4 col-md-6 mb-4";
    const inner = document.createElement("div");
    inner.className = "card product";
    // outer.appendChild(inner);
    const link = document.createElement("a");
    link.href = "/main/products/" + item.id;
    inner.appendChild(link);
    const img = document.createElement("img");
    img.className = "card-img-top";
    img.src = item.image_url;
    img.alt = item.name;
    link.appendChild(img);
    const body = document.createElement("div");
    body.className = "card-body";
    inner.appendChild(body);
    const title = document.createElement("h4");
    title.className = "card-title";
    body.appendChild(title);
    const titleLink = document.createElement("a");
    titleLink.href = "/main/products/" + item.id;
    titleLink.textContent = item.name;
    title.appendChild(titleLink);
    const price = document.createElement("h5");
    price.textContent = "$" + item.price;
    body.appendChild(price);
    const desc = document.createElement("p");
    desc.className = "card-text";
    if (item.description.length > 50) {

    }
    desc.textContent = item.description.length > 100 ? item.description.substring(0, 49) + "...": item.description;
    body.appendChild(desc);
    document.getElementById("products").appendChild(inner);
  });
}
