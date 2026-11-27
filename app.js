// the python server runs on localhost:1234
const API = "http://localhost:1234";

// 5 purdue dining courts
const COURTS = ["Earhart", "Ford", "Hillenbrand", "Wiley", "Windsor"];

const courtsEl = document.querySelector("#courts");
const statusEl = document.querySelector("#status");
const menuEl = document.querySelector("#menu");

// cache menus by court so re-clicking a button skips the API call
const cache = {};

// create buttons for each dining court
for (const name of COURTS) {
  const btn = document.createElement("button");

  // set the button to the name of the court. 
  btn.textContent = name;

  // on click action listener -> load data for the respective dining court
  btn.addEventListener("click", () => load(name, btn));

  // add it to the html
  courtsEl.appendChild(btn);
}


// load data
async function load(court, btn) {

  for (const b of courtsEl.querySelectorAll("button")) b.classList.remove("on");
  btn.classList.add("on");

  // reuse a previously fetched menu for this court
  if (cache[court]) {
    show(cache[court]);
    return;
  }

  statusEl.textContent = "Loading...";
  menuEl.replaceChildren();

  try {

    // load data from python server
    const res = await fetch(`${API}/menu/${encodeURIComponent(court)}`);

    // bad response if we don't get an HTTP 200 OK
    if (!res.ok) throw new Error("bad response");
      const data = await res.json();
      cache[court] = data;
      show(data);
  } catch {
      statusEl.textContent = "server error";
  }
}

function show(data) {

  // have a status text saying the date the menu is for.
  statusEl.textContent = `Menus for ${data.date}`;

  // in the event that there is no vegetarian+eggless food on menu. Usually this does not happen (i hope so Purdue don't let me starve)
  if (!data.meals.length) {
    menuEl.textContent = "Nothing vegetarian + eggless :(";
    return;
  }

  // use the XML ordering to keep data readable. 
  // split the food into breakfast/lunch/dinner and different food stations
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

    // add the menu element to the HTML
    menuEl.appendChild(section);
  }
}

courtsEl.querySelector("button").click();
