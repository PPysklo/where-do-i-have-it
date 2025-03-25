document.addEventListener('DOMContentLoaded', function() {
    const listViewButton = document.querySelector('.listView');
    const gridViewButton = document.querySelector('.gridView');
    const container = document.getElementById('thingsContainer');

    listViewButton.addEventListener('click', function() {
      container.classList.add('list-view');
      container.classList.remove('grid-view');
    });

    gridViewButton.addEventListener('click', function() {
      container.classList.add('grid-view');
      container.classList.remove('list-view');
    });
  });


