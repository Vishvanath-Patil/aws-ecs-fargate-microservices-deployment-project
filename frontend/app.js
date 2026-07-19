const services = {
  auth: "/api/auth",
  user: "/api/user",
  post: "/api/post",
  like: "/api/like",
};

let authMode = "login";
let token = localStorage.getItem("devconnect_token") || "";
let currentUser = JSON.parse(localStorage.getItem("devconnect_user") || "null");

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[char]));
}

function headers() {
  return token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
}

async function api(service, path, options = {}) {
  const res = await fetch(`${services[service]}${path}`, {
    ...options,
    headers: { ...headers(), ...(options.headers || {}) },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail || "Request failed");
  }
  return res.json();
}

function setMessage(text, ok = false) {
  $("authMessage").textContent = text;
  $("authMessage").style.color = ok ? "#0f766e" : "#e85d4f";
}

function setUser(user) {
  currentUser = user;
  localStorage.setItem("devconnect_user", JSON.stringify(user));
  $("profileName").textContent = user ? user.username : "Guest builder";
  $("profileMeta").textContent = user ? user.email : "Sign in to save your profile";
  $("avatar").textContent = user ? user.username.slice(0, 2).toUpperCase() : "DC";
}

async function checkServices() {
  const container = $("serviceStatus");
  container.innerHTML = "";
  await Promise.all(Object.entries(services).map(async ([name, base]) => {
    let status = "offline";
    try {
      const res = await fetch(`${base}/health`);
      status = res.ok ? "online" : "offline";
    } catch (_) {
      status = "offline";
    }
    const pill = document.createElement("div");
    pill.className = "service-pill";
    pill.innerHTML = `<strong>${name}-service</strong><span>${status}</span>`;
    container.appendChild(pill);
  }));
}

async function loadProfile() {
  if (!token) return;
  const profile = await api("user", "/profiles/me");
  $("displayName").value = profile.display_name;
  $("title").value = profile.title;
  $("location").value = profile.location;
  $("bio").value = profile.bio;
  $("avatar").style.background = profile.avatar_color;
  $("profileName").textContent = profile.display_name;
  $("profileMeta").textContent = `${profile.title} · ${profile.location}`;
}

async function loadPeople() {
  const people = await api("user", "/profiles");
  $("peopleList").innerHTML = people.length ? "" : "<p class='post-meta'>No profiles yet.</p>";
  people.forEach((person) => {
    const item = document.createElement("div");
    item.className = "person";
    item.innerHTML = `<div class="avatar" style="background:${escapeHtml(person.avatar_color)}">${escapeHtml(person.display_name.slice(0, 2).toUpperCase())}</div>
      <div><strong>${escapeHtml(person.display_name)}</strong><span>${escapeHtml(person.title)}</span></div>`;
    $("peopleList").appendChild(item);
  });
}

async function loadFeed() {
  const [posts, likes] = await Promise.all([api("post", "/posts"), api("like", "/likes")]);
  const list = $("feedList");
  list.innerHTML = posts.length ? "" : "<article class='post'>No posts yet. Be the first to ship a thought.</article>";
  posts.forEach((post) => {
    const article = document.createElement("article");
    article.className = "post";
    const created = new Date(post.created_at).toLocaleString();
    article.innerHTML = `
      <div class="post-header">
        <div><strong>@${escapeHtml(post.username)}</strong><span class="post-meta">${created}</span></div>
        <span class="tag">${escapeHtml(post.tag)}</span>
      </div>
      <p>${escapeHtml(post.body)}</p>
      <div class="like-row">
        <span class="post-meta">${likes[post.id] || 0} likes</span>
        <button class="like-button" data-like="${post.id}">Like</button>
      </div>`;
    list.appendChild(article);
  });
}

document.querySelectorAll("[data-auth-tab]").forEach((button) => {
  button.addEventListener("click", () => {
    authMode = button.dataset.authTab;
    document.querySelectorAll("[data-auth-tab]").forEach((tab) => tab.classList.toggle("active", tab === button));
    $("email").classList.toggle("hidden", authMode !== "register");
  });
});

$("authForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = { username: $("username").value, password: $("password").value };
    if (authMode === "register") payload.email = $("email").value;
    const result = await api("auth", authMode === "register" ? "/register" : "/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    token = result.access_token;
    localStorage.setItem("devconnect_token", token);
    setUser(result.user);
    setMessage("Signed in. You are connected.", true);
    await Promise.all([loadProfile(), loadPeople(), loadFeed()]);
  } catch (error) {
    setMessage(error.message);
  }
});

$("profileForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!token) return setMessage("Sign in before saving a profile.");
  await api("user", "/profiles/me", {
    method: "PUT",
    body: JSON.stringify({
      display_name: $("displayName").value,
      title: $("title").value,
      location: $("location").value,
      bio: $("bio").value,
      avatar_color: "#0f766e",
    }),
  });
  setMessage("Profile saved.", true);
  await Promise.all([loadProfile(), loadPeople()]);
});

$("postForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!token) return setMessage("Sign in before posting.");
  await api("post", "/posts", {
    method: "POST",
    body: JSON.stringify({ body: $("postBody").value, tag: $("tag").value }),
  });
  $("postBody").value = "";
  await loadFeed();
});

$("feedList").addEventListener("click", async (event) => {
  const id = event.target.dataset.like;
  if (!id) return;
  if (!token) return setMessage("Sign in before liking posts.");
  await api("like", "/likes/toggle", { method: "POST", body: JSON.stringify({ post_id: Number(id) }) });
  await loadFeed();
});

setUser(currentUser);
checkServices();
Promise.allSettled([loadFeed(), loadPeople(), loadProfile()]);
