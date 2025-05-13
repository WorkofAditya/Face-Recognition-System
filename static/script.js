function register() {
  const name = document.getElementById('name').value;
  if (!name) {
    alert("Please enter a name.");
    return;
  }

  fetch("/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: "name=" + encodeURIComponent(name)
  })
    .then(res => res.text())
    .then(msg => alert(msg));
}
