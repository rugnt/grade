function ajaxSend(url, params) {
    // Отправляем запрос
    fetch(`${url}?${params}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => response.json())
        .then(json => render(json))
        .catch(error => console.error(error))
}

const forms = document.querySelector('form[name=filter]');

forms.addEventListener('submit', function (e) {
    // Получаем данные из формы
    e.preventDefault();
    let url = this.action;
    let params = new URLSearchParams(new FormData(this)).toString();
    ajaxSend(url, params);
});

function render(data) {
    // Рендер шаблона
    let template = Hogan.compile(html);
    let output = template.render(data);

    const div = document.querySelector('div[id=div-filter]');
    div.innerHTML = output;
}

let html = '\
{{#items}}\
      <div class="col-md-4">\
        <div class="card mb-4 box-shadow">\
          <img class="card-img-top" src="{{ image_url }}" data-holder-rendered="true">\
          <div class="card-body">\
          <h2 class="card-title">{{ title }}</h2>\
            <p class="card-text">{{ description }}</p>\
            <div class="d-flex justify-content-between align-items-center">\
              <div class="btn-group">\
                <p class="center">{{ category }}</p>\
                </br>\
                <a type="button" class="btn btn-sm btn-outline-secondary" href="{{ detail_url }}">Показать</a>\
              </div>\
              <small class="text-muted">{{ rating }}/10</small>\
            </div>\
          </div>\
        </div>\
      </div>\
{{/items}}'