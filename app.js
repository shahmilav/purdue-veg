const API = "http://localhost:1234";

const COURTS = ["Earhart", "Ford", "Hillenbrand", "Wiley", "Windsor"];

const courtsEl = document.querySelector("#courts");
const statusEl = document.querySelector("#status");
const menuEl = document.querySelector("#menu");

// create buttons for each dining court
for (const name of COURTS) {
  const btn = document.createElement("button");
  btn.textContent = name;
  btn.addEventListener("click", () => load(name, btn));
  courtsEl.appendChild(btn);
}


// load data
async function load(court, btn) {
  for (const b of courtsEl.querySelectorAll("button")) b.classList.remove("on");
  btn.classList.add("on");

  statusEl.textContent = "Loading...";
  menuEl.replaceChildren();

  try {
    const res = await fetch(`${API}/menu/${encodeURIComponent(court)}`);
    if (!res.ok) throw new Error("bad response");
    show(await res.json());
  } catch {
    statusEl.textContent = "server error";
  }
}

function show(data) {
  statusEl.textContent = `${data.location} · ${data.date}`;

  if (!data.meals.length) {
    menuEl.textContent = "Nothing vegetarian + eggless :(";
    return;
  }

  for (const meal of data.meals) {
    const section = document.createElement("section");
    const h2 = document.createElement("h2");
    h2.textContent = meal.meal;
    section.appendChild(h2);

    for (const station of meal.stations) {
      const h3 = document.createElement("h3");
      h3.textContent = station.station;
      const ul = document.createElement("ul");
      for (const item of station.items) {
        const li = document.createElement("li");
        li.textContent = item;
        ul.appendChild(li);
      }
      section.append(h3, ul);
    }

    menuEl.appendChild(section);
  }
}

courtsEl.querySelector("button").click();
