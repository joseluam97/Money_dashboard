const expandTemplateButton = document.querySelector(".accordian-logo");
const templateContainer = document.querySelector(".event-container")
const blockBackgroundDiv = document.querySelector(".block-background");
const addTemplateButton = document.getElementById("add-event-template");
const formContainer = document.querySelector(".form-container");
const exitButton = document.querySelector(".exit");
const form = document.querySelector(".form-container form");
const formHeader = document.querySelector(".form-header");
let deleteTemplateButtons;

let date = new Date();
let templates = [1, 2]

function renderCalendar() {
    let today = new Date();
    let dayToday;
    if(date.getMonth() == today.getMonth() && date.getFullYear() == today.getFullYear()){
        dayToday = today.getDate();
    }
    // Setting date to first day of month
    date.setDate(1)

    // Getting the last day of the month
    const monthDays = document.querySelector(".days");

    // Getting the last day of the month
    const lastDay = new Date(date.getFullYear(),
    date.getMonth() + 1, 0).getDate();

    // Getting the last day of the previous month
    const prevLastDay = new Date(date.getDate(),
    date.getMonth(), 0).getDate();

    // Getting the index of the last day
    const firstDayIndex = date.getDay() - 1;

    // Getting the index of teh last day
    const lastDayIndex = new Date(date.getFullYear(),
    date.getMonth() + 1, 0).getDay();

    // Getting the number of days in the next month
    // that will appear on the end of the calendar
    const nextDays = 6 - lastDayIndex;

    const months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    // Getting current month and year
    // and adding these to the calendar
    const month = months[date.getMonth()];
    const year = date.getFullYear().toString();
    document.querySelector(".date").innerHTML = month + ", " + year;

    let days = "";

    // Adding the prev month days to the calendar
    for (let i = firstDayIndex - 1; i >= 0; i--) {
        //days += `<div class="prev-date"><div>${prevLastDay - 1}</div></div>`;
        days += `<div class="prev-date"><div></div></div>`;
    }

    // Adding the current month days to the calendar
    for (let i = 1; i <= lastDay; i++) {
        if(dayToday == i && dayToday != undefined){
            days += `<div class="drop-container bg-primary" id="day-${i}"><div class="day-today-format">${i}</div></div>`;
        }
        else{
            days += `<div class="drop-container" id="day-${i}"><div class="day-format">${i}</div></div>`;
        }
    }

    // Adding the next month days to the calendar
    /*for (let i = 1; i <= nextDays; i++) {
        //days += `<div class="next-date"><div>${i}</div></div>`;
        days += `<div class="next-date"><div></div></div>`;
    }*/

    // Adding the days to the html
    monthDays.innerHTML = days;

    draggingFunctionality();
    loadDataToCalendar(date.getMonth() + 1, date.getFullYear());
    deleteEventFunctionality();
    dropContainer();
    functionExitButton();
}

function nextMonth(date) {
    document.querySelector(".next").
    addEventListener("click", () => {
        date.setMonth(date.getMonth() + 1);
        renderCalendar();
    });
}

function prevMonth(date) {
    document.querySelector(".prev").
    addEventListener("click", () => {
        date.setMonth(date.getMonth() - 1);
        renderCalendar();
    });
}

function functionExitButton(){
    exitButton.addEventListener("click", () => {
        clearForm();
    });
}

function dropContainer() {
    var dropContainers = document.querySelectorAll('.drop-container');

    // Iterar sobre cada elemento drop-container
    dropContainers.forEach(function(dropContainer) {
        // Agregar un event listener para el evento de clic
        dropContainer.addEventListener('click', function(event) {
        // Verificar si el clic ocurrió en un elemento con la clase "event"
        if (event.target.classList.contains('event')) {

            let idEvent = event.target.id.split("-")[2]
            
            $.ajax({
                url: 'http://127.0.0.1:8000/get-event/' + idEvent + "/", 
                type: 'GET',
                success: function (data) {

                    document.getElementById('input-user').value = data.event.full_name
                    document.getElementById('input-title').value = data.event.name
                    document.getElementById('input-amount').value = data.event.amount + " €"
                    document.getElementById('input-date').value = data.event.date
                    document.getElementById('input-notes').value = data.event.notes

                },
                error: function () {
                    console.error('Error al cargar los datos.');
                }
              });


        }
        });
    });
}

function clearForm() {
    document.getElementById('id_event_name').value = ""
    document.getElementById('id_event_account').value = ""
    document.getElementById('id_event_date').value = ""
    document.getElementById('id_event_notes').value = ""
}

function deleteTemplate(event) {
    let template = event.target.parentElement
    let templateId = template.id
    let data = {
        "templateId": templateId
    }
    fetch(`${window.origin}/delete-template/`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(data),
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(() => {
        window.location.reload();
    })
}

function dragstart_handler(event) {
    event.dataTransfer.setData("text", event.target.id);
    event.effectAllowed = "copyMove";
}

function dragover_handler(event) {
    event.preventDefault();
}

function drop_handler(event) {
    event.preventDefault();
    let id = event.dataTransfer.getData("text");
    let nodeCopy = document.getElementById(id).cloneNode(true);
    nodeCopy.classList.remove("eventTemplate");
    nodeCopy.classList.add("event");

    // Ensuring element is dropped in the div.drop-container
    let parent = event.target;
    while (!parent.classList.contains("drop-container")) {
        parent = parent.parentElement;
    }
    let deleteButton = nodeCopy.querySelector(".bx-trash");
    nodeCopy.removeChild(deleteButton);

    nodeCopy.removeAttribute("draggable");
    parent.appendChild(nodeCopy)

    let eventYear = date.getFullYear();
    let eventMonth = date.getMonth() + 1;
    let eventDay = parent.id.split("-")[1];
    let eventDate = `${eventYear}-${eventMonth}-${eventDay}`;

    let data = {
        "templateId": id,
        "date": eventDate,
    };
    sendTemplateData("event", data);
}

function sendTemplateData(templateType, data) {
    fetch(`${window.origin}/create-${templateType}/`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(data),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(res => {
        res.json().then(resData => {
            console.log(resData.message);
        })
    })
}

function draggingFunctionality() {
    document.querySelectorAll(".eventTemplate").forEach(template => {
        template.addEventListener("dragstart", dragstart_handler);
    });
    document.querySelectorAll(".drop-container").forEach(date => {
        date.addEventListener("drop", drop_handler);
        date.addEventListener("dragover", dragover_handler);
    });
}

function loadDataToCalendar(month, yearSelected) {

    $.ajax({
          url: 'http://127.0.0.1:8000/get-events/' + month + "/",  // Ajusta la URL según tu configuración
          type: 'GET',
          success: function (data) {
            templates = data.templates
            data.events.forEach(event => {
                let yearEvent = event.date.split("-")[0]
                if(yearEvent == yearSelected){
                    let eventDay = parseInt(event.date.split("-")[2]);
                    let eventId = `event-id-${event.id}`;
                    let dateId = `#day-${eventDay}`;
                    let theDay = document.querySelector(dateId);
                    let theEvent = document.createElement("div");
                    theEvent.textContent = event.name;
                    theEvent.setAttribute("id", eventId);
                    theEvent.setAttribute("class", "event ");
                    theDay.appendChild(theEvent);
                }
                
            });
          },
          error: function () {
              console.error('Error al cargar los datos.');
          }
        });
}

function deleteEventFunctionality() {
    document.querySelectorAll(".event").forEach(event => {
        event.addEventListener("dblclick", deleteEvent);
    });
    document.querySelectorAll(".wellness-questionaire").forEach(event => {
        event.addEventListener("dblclick", deleteEvent);
    });
}

function deleteEvent(event) {
    let eventId = parseInt(event.target.id.split("-")[2]);
    let type = event.target.id.split("-")[0]
    let data = {
        "type": type,
        "eventId": eventId,
    }
    fetch(`${window.origin}/delete-event/`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(data),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(res => {
        res.json().then(data => {
            console.log(data.message);
            window.location.reload();
        })
    })
}

function startApp() {
    
    renderCalendar();
    nextMonth(date);
    prevMonth(date);
}

startApp();